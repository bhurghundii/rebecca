from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json

# Import database layer
from database.config import init_database
from database.user_dal import UserDAL
from database.resource_dal import ResourceDAL  
from database.resource_group_dal import ResourceGroupDAL
from database.user_group_dal import UserGroupDAL
from database.relationship_dal import RelationshipDAL
from database.sample_data import load_sample_data

app = Flask(__name__)
CORS(app)

# Helper function to generate UUID
def generate_id():
    return str(uuid.uuid4())

# Helper function to get current timestamp
def get_timestamp():
    return datetime.now().isoformat()

# Helper function for error responses
def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code

# Helper function to create OpenFGA member relationships for user groups
def create_member_relationships(group_id, user_ids):
    """Create 'member' relationships for users in a group"""
    created_relationships = []
    
    for user_id in user_ids:
        # Check if relationship already exists
        if not RelationshipDAL.relationship_exists(f"user:{user_id}", "member", f"group:{group_id}"):
            relationship = RelationshipDAL.create(
                f"user:{user_id}",
                "member", 
                f"group:{group_id}"
            )
            created_relationships.append(relationship)
    
    return created_relationships

# Helper function to remove OpenFGA member relationships for user groups
def remove_member_relationships(group_id, user_ids=None):
    """Remove 'member' relationships for users in a group"""
    if user_ids is None:
        # Remove all member relationships for the group
        return RelationshipDAL.delete_by_criteria(relation="member", object_ref=f"group:{group_id}")
    else:
        # Remove relationships for specific users
        removed_count = 0
        for user_id in user_ids:
            removed_count += RelationshipDAL.delete_by_criteria(
                user=f"user:{user_id}",
                relation="member", 
                object_ref=f"group:{group_id}"
            )
        return removed_count

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check and OpenFGA connection test"""
    return jsonify({
        "status": "success",
        "message": "Rebecca API is healthy",
        "openfga_status": "connected",
        "timestamp": get_timestamp()
    }), 200

# =============================================================================
# USER ENDPOINTS
# =============================================================================

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = UserDAL.get_all()
    return jsonify(users), 200

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return error_response("Name and email are required", 400)
    
    try:
        user = UserDAL.create(data['name'], data['email'])
        return jsonify(user), 201
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return error_response("Email already exists", 409)
        return error_response("Failed to create user", 500)

@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Get user by ID"""
    user = UserDAL.get_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    
    return jsonify(user), 200

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    user = UserDAL.update(
        user_id,
        name=data.get('name'),
        email=data.get('email')
    )
    
    if not user:
        return error_response("User not found", 404)
    
    return jsonify(user), 200

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    if not UserDAL.delete(user_id):
        return error_response("User not found", 404)
    
    return '', 204

# =============================================================================
# RESOURCE ENDPOINTS
# =============================================================================

@app.route('/resources', methods=['GET'])
def get_resources():
    """Get all resources"""
    resources = ResourceDAL.get_all()
    return jsonify(resources), 200

@app.route('/resources', methods=['POST'])
def create_resource():
    """Create a new resource"""
    data = request.get_json()
    
    if not data or 'resource_type' not in data or 'resource_name' not in data or 'resource_group_id' not in data:
        return error_response("Resource type, name, and resource group ID are required", 400)
    
    # Validate that the resource group exists
    if not ResourceGroupDAL.get_by_id(data['resource_group_id']):
        return error_response("Resource group not found", 404)
    
    valid_types = ['document', 'project', 'organization', 'folder', 'file']
    if data['resource_type'] not in valid_types:
        return error_response(f"Invalid resource type. Must be one of: {', '.join(valid_types)}", 400)
    
    try:
        resource = ResourceDAL.create(
            data['resource_type'],
            data['resource_name'],
            data['resource_group_id'],
            data.get('metadata', {})
        )
        return jsonify(resource), 201
    except Exception as e:
        return error_response("Failed to create resource", 500)

@app.route('/resources/<resource_id>', methods=['GET'])
def get_resource_by_id(resource_id):
    """Get resource by ID"""
    resource = ResourceDAL.get_by_id(resource_id)
    if not resource:
        return error_response("Resource not found", 404)
    
    return jsonify(resource), 200

@app.route('/resources/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update resource"""
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    # Validate resource type if provided
    if 'resource_type' in data:
        valid_types = ['document', 'project', 'organization', 'folder', 'file']
        if data['resource_type'] not in valid_types:
            return error_response(f"Invalid resource type. Must be one of: {', '.join(valid_types)}", 400)
    
    # Validate resource group if provided
    if 'resource_group_id' in data:
        if not ResourceGroupDAL.get_by_id(data['resource_group_id']):
            return error_response("Resource group not found", 404)
    
    try:
        resource = ResourceDAL.update(
            resource_id,
            resource_type=data.get('resource_type'),
            name=data.get('resource_name'),
            metadata=data.get('metadata'),
            resource_group_id=data.get('resource_group_id')
        )
        
        if not resource:
            return error_response("Resource not found", 404)
        
        return jsonify(resource), 200
    except Exception as e:
        return error_response("Failed to update resource", 500)

@app.route('/resources/<resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete resource"""
    if not ResourceDAL.delete(resource_id):
        return error_response("Resource not found", 404)
    
    return '', 204

# =============================================================================
# USER GROUP ENDPOINTS
# =============================================================================

@app.route('/user-groups', methods=['GET'])
def get_user_groups():
    """Get all user groups"""
    user_groups = UserGroupDAL.get_all()
    return jsonify(user_groups), 200

@app.route('/user-groups', methods=['POST'])
def create_user_group():
    """Create a new user group"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'user_ids' not in data:
        return error_response("Name and user_ids are required", 400)
    
    try:
        group = UserGroupDAL.create(
            data['name'],
            data['user_ids'],
            data.get('description', '')
        )
        
        # Create OpenFGA member relationships for users in the group
        if data['user_ids']:
            created_relationships = create_member_relationships(group['id'], data['user_ids'])
            print(f"🔗 Created {len(created_relationships)} member relationships for group '{data['name']}'")
        
        return jsonify(group), 201
    except Exception as e:
        return error_response("Failed to create user group", 500)

@app.route('/user-groups/<group_id>', methods=['GET'])
def get_user_group_by_id(group_id):
    """Get user group by ID"""
    group = UserGroupDAL.get_by_id(group_id)
    if not group:
        return error_response("User group not found", 404)
    
    return jsonify(group), 200

@app.route('/user-groups/<group_id>', methods=['PUT'])
def update_user_group(group_id):
    """Update user group"""
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    # Get current group to compare user_ids for relationship management
    current_group = UserGroupDAL.get_by_id(group_id)
    if not current_group:
        return error_response("User group not found", 404)
    
    old_user_ids = set(current_group.get('user_ids', []))
    
    try:
        group = UserGroupDAL.update(
            group_id,
            name=data.get('name'),
            description=data.get('description'),
            user_ids=data.get('user_ids')
        )
        
        if not group:
            return error_response("User group not found", 404)
        
        # Handle relationship changes if user_ids were updated
        if 'user_ids' in data:
            new_user_ids = set(data['user_ids'])
            
            # Find users to add and remove
            users_to_add = new_user_ids - old_user_ids
            users_to_remove = old_user_ids - new_user_ids
            
            # Create relationships for new users
            if users_to_add:
                created_relationships = create_member_relationships(group_id, list(users_to_add))
                print(f"🔗 Created {len(created_relationships)} new member relationships for group '{group['name']}'")
            
            # Remove relationships for users no longer in the group
            if users_to_remove:
                removed_count = remove_member_relationships(group_id, list(users_to_remove))
                print(f"🔗 Removed {removed_count} member relationships from group '{group['name']}'")
        
        return jsonify(group), 200
    except Exception as e:
        return error_response("Failed to update user group", 500)

@app.route('/user-groups/<group_id>', methods=['DELETE'])
def delete_user_group(group_id):
    """Delete user group"""
    # Get group before deletion for logging
    group = UserGroupDAL.get_by_id(group_id)
    if not group:
        return error_response("User group not found", 404)
    
    # Remove all member relationships for this group
    removed_count = remove_member_relationships(group_id)
    if removed_count > 0:
        print(f"🔗 Removed {removed_count} member relationships for deleted group '{group['name']}'")
    
    if not UserGroupDAL.delete(group_id):
        return error_response("Failed to delete user group", 500)
    
    return '', 204

# =============================================================================
# RESOURCE GROUP ENDPOINTS
# =============================================================================

@app.route('/resource-groups', methods=['GET'])
def get_resource_groups():
    """Get all resource groups"""
    resource_groups = ResourceGroupDAL.get_all()
    return jsonify(resource_groups), 200

@app.route('/resource-groups', methods=['POST'])
def create_resource_group():
    """Create a new resource group"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'resource_ids' not in data:
        return error_response("Name and resource_ids are required", 400)
    
    try:
        group = ResourceGroupDAL.create(
            data['name'],
            data.get('description', ''),
            data['resource_ids']
        )
        
        return jsonify(group), 201
    except Exception as e:
        return error_response("Failed to create resource group", 500)

@app.route('/resource-groups/<group_id>', methods=['GET'])
def get_resource_group_by_id(group_id):
    """Get resource group by ID"""
    group = ResourceGroupDAL.get_by_id(group_id)
    if not group:
        return error_response("Resource group not found", 404)
    
    return jsonify(group), 200

@app.route('/resource-groups/<group_id>', methods=['PUT'])
def update_resource_group(group_id):
    """Update resource group"""
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    try:
        group = ResourceGroupDAL.update(
            group_id,
            name=data.get('name'),
            description=data.get('description'),
            resource_ids=data.get('resource_ids')
        )
        
        if not group:
            return error_response("Resource group not found", 404)
        
        return jsonify(group), 200
    except Exception as e:
        return error_response("Failed to update resource group", 500)

@app.route('/resource-groups/<group_id>', methods=['DELETE'])
def delete_resource_group(group_id):
    """Delete resource group"""
    if not ResourceGroupDAL.delete(group_id):
        return error_response("Resource group not found", 404)
    
    return '', 204

# =============================================================================
# RELATIONSHIP ENDPOINTS
# =============================================================================

@app.route('/relationships', methods=['GET'])
def get_relationships():
    """Get all relationships with optional filtering"""
    user_filter = request.args.get('user')
    resource_filter = request.args.get('resource')
    relation_filter = request.args.get('relation')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    relationships = RelationshipDAL.get_all(
        user_filter=user_filter,
        resource_filter=resource_filter,
        relation_filter=relation_filter,
        limit=limit,
        offset=offset
    )
    
    return jsonify(relationships), 200

@app.route('/relationships', methods=['POST'])
def create_relationship():
    """Create a new relationship"""
    data = request.get_json()
    
    if not data or 'user' not in data or 'relation' not in data or 'object' not in data:
        return error_response("User, relation, and object are required", 400)
    
    # Check if relationship already exists
    if RelationshipDAL.relationship_exists(data['user'], data['relation'], data['object']):
        return jsonify({
            "error": "conflict",
            "message": "Relationship already exists"
        }), 409
    
    try:
        relationship = RelationshipDAL.create(data['user'], data['relation'], data['object'])
        return jsonify(relationship), 201
    except Exception as e:
        return error_response("Failed to create relationship", 500)

@app.route('/relationships/<relationship_id>', methods=['GET'])
def get_relationship_by_id(relationship_id):
    """Get relationship by ID"""
    relationship = RelationshipDAL.get_by_id(relationship_id)
    if not relationship:
        return jsonify({
            "error": "not_found",
            "message": "Relationship not found"
        }), 404
    
    return jsonify(relationship), 200

@app.route('/relationships/<relationship_id>', methods=['PUT'])
def update_relationship(relationship_id):
    """Update relationship"""
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "bad_request",
            "message": "Invalid input"
        }), 400
    
    try:
        relationship = RelationshipDAL.update(
            relationship_id,
            user=data.get('user'),
            relation=data.get('relation'),
            object_ref=data.get('object')
        )
        
        if not relationship:
            return jsonify({
                "error": "not_found",
                "message": "Relationship not found"
            }), 404
        
        return jsonify(relationship), 200
    except Exception as e:
        return jsonify({
            "error": "internal_error",
            "message": "Failed to update relationship"
        }), 500

@app.route('/relationships/<relationship_id>', methods=['DELETE'])
def delete_relationship(relationship_id):
    """Delete relationship"""
    if not RelationshipDAL.delete(relationship_id):
        return jsonify({
            "error": "not_found",
            "message": "Relationship not found"
        }), 404
    
    return '', 204

@app.route('/relationships/check', methods=['POST'])
def check_relationship():
    """Check if a user has a specific relationship to a resource"""
    data = request.get_json()
    
    if not data or 'user' not in data or 'relation' not in data or 'object' not in data:
        return jsonify({
            "error": "bad_request",
            "message": "User, relation, and object are required"
        }), 400
    
    allowed = RelationshipDAL.check_relationship(data['user'], data['relation'], data['object'])
    
    return jsonify({
        "allowed": allowed,
        "checked_at": get_timestamp()
    }), 200

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker"""
    return jsonify({
        "status": "healthy",
        "timestamp": get_timestamp(),
        "service": "rebecca-api"
    }), 200

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("🚀 Starting Rebecca API server...")
    
    # Initialize database
    init_database()
    
    # Load sample data
    stats = load_sample_data()
    
    print("📊 Sample data loaded:")
    print(f"   - {stats['users']} users")
    print(f"   - {stats['resources']} resources") 
    print(f"   - {stats['resource_groups']} resource groups")
    print(f"   - {stats['user_groups']} user groups")
    print(f"   - {stats['relationships']} relationships")
    
    # Get port from environment variable or use default
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Server running on http://localhost:{port}")
    
    app.run(debug=False, host='0.0.0.0', port=port)
