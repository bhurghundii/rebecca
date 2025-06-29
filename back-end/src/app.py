from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Mock data storage (in-memory for now)
users = {}
resources = {}
user_groups = {}
resource_groups = {}
relationships = {}

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
    timestamp = get_timestamp()
    
    for user_id in user_ids:
        # Check if relationship already exists
        relationship_exists = False
        for rel in relationships.values():
            if (rel['user'] == f"user:{user_id}" and 
                rel['relation'] == "member" and 
                rel['object'] == f"group:{group_id}"):
                relationship_exists = True
                break
        
        if not relationship_exists:
            rel_id = generate_id()
            relationship = {
                "id": rel_id,
                "user": f"user:{user_id}",
                "relation": "member",
                "object": f"group:{group_id}",
                "created_at": timestamp,
                "updated_at": timestamp
            }
            relationships[rel_id] = relationship
            created_relationships.append(relationship)
    
    return created_relationships

# Helper function to remove OpenFGA member relationships for user groups
def remove_member_relationships(group_id, user_ids=None):
    """Remove 'member' relationships for users in a group"""
    removed_relationships = []
    
    # If user_ids is None, remove all member relationships for the group
    if user_ids is None:
        to_remove = []
        for rel_id, rel in relationships.items():
            if (rel['relation'] == "member" and 
                rel['object'] == f"group:{group_id}"):
                to_remove.append(rel_id)
                removed_relationships.append(rel)
        
        for rel_id in to_remove:
            del relationships[rel_id]
    else:
        # Remove relationships for specific users
        to_remove = []
        for rel_id, rel in relationships.items():
            if (rel['relation'] == "member" and 
                rel['object'] == f"group:{group_id}" and
                rel['user'] in [f"user:{uid}" for uid in user_ids]):
                to_remove.append(rel_id)
                removed_relationships.append(rel)
        
        for rel_id in to_remove:
            del relationships[rel_id]
    
    return removed_relationships

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
    return jsonify(list(users.values())), 200

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return error_response("Name and email are required", 400)
    
    user_id = generate_id()
    timestamp = get_timestamp()
    
    user = {
        "id": user_id,
        "name": data['name'],
        "email": data['email'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    users[user_id] = user
    return jsonify(user), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Get user by ID"""
    if user_id not in users:
        return error_response("User not found", 404)
    
    return jsonify(users[user_id]), 200

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    if user_id not in users:
        return error_response("User not found", 404)
    
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    user = users[user_id]
    if 'name' in data:
        user['name'] = data['name']
    if 'email' in data:
        user['email'] = data['email']
    
    user['updated_at'] = get_timestamp()
    
    return jsonify(user), 200

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    if user_id not in users:
        return error_response("User not found", 404)
    
    del users[user_id]
    return '', 204

# =============================================================================
# RESOURCE ENDPOINTS
# =============================================================================

@app.route('/resources', methods=['GET'])
def get_resources():
    """Get all resources"""
    return jsonify(list(resources.values())), 200

@app.route('/resources', methods=['POST'])
def create_resource():
    """Create a new resource"""
    data = request.get_json()
    
    if not data or 'resource_type' not in data or 'resource_name' not in data or 'resource_group_id' not in data:
        return error_response("Resource type, name, and resource group ID are required", 400)
    
    # Validate that the resource group exists
    if data['resource_group_id'] not in resource_groups:
        return error_response("Resource group not found", 404)
    
    valid_types = ['document', 'project', 'organization', 'folder', 'file']
    if data['resource_type'] not in valid_types:
        return error_response(f"Invalid resource type. Must be one of: {', '.join(valid_types)}", 400)
    
    resource_id = generate_id()
    timestamp = get_timestamp()
    
    resource = {
        "id": resource_id,
        "type": data['resource_type'],
        "name": data['resource_name'],
        "metadata": data.get('metadata', {}),
        "resource_group_id": data['resource_group_id'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    resources[resource_id] = resource
    
    # Add the resource to the resource group
    resource_group = resource_groups[data['resource_group_id']]
    if resource_id not in resource_group['resource_ids']:
        resource_group['resource_ids'].append(resource_id)
        resource_group['updated_at'] = timestamp
    
    return jsonify(resource), 201

@app.route('/resources/<resource_id>', methods=['GET'])
def get_resource_by_id(resource_id):
    """Get resource by ID"""
    if resource_id not in resources:
        return error_response("Resource not found", 404)
    
    return jsonify(resources[resource_id]), 200

@app.route('/resources/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """Update resource"""
    if resource_id not in resources:
        return error_response("Resource not found", 404)
    
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    resource = resources[resource_id]
    old_group_id = resource.get('resource_group_id')
    
    if 'resource_type' in data:
        valid_types = ['document', 'project', 'organization', 'folder', 'file']
        if data['resource_type'] not in valid_types:
            return error_response(f"Invalid resource type. Must be one of: {', '.join(valid_types)}", 400)
        resource['type'] = data['resource_type']
    
    if 'resource_name' in data:
        resource['name'] = data['resource_name']
    
    if 'metadata' in data:
        resource['metadata'] = data['metadata']
    
    # Handle resource group change
    if 'resource_group_id' in data:
        new_group_id = data['resource_group_id']
        
        # Validate that the new resource group exists
        if new_group_id not in resource_groups:
            return error_response("Resource group not found", 404)
        
        # Remove from old group if it exists
        if old_group_id and old_group_id in resource_groups:
            old_group = resource_groups[old_group_id]
            if resource_id in old_group['resource_ids']:
                old_group['resource_ids'].remove(resource_id)
                old_group['updated_at'] = get_timestamp()
        
        # Add to new group
        new_group = resource_groups[new_group_id]
        if resource_id not in new_group['resource_ids']:
            new_group['resource_ids'].append(resource_id)
            new_group['updated_at'] = get_timestamp()
        
        resource['resource_group_id'] = new_group_id
    
    resource['updated_at'] = get_timestamp()
    
    return jsonify(resource), 200

@app.route('/resources/<resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """Delete resource"""
    if resource_id not in resources:
        return error_response("Resource not found", 404)
    
    resource = resources[resource_id]
    resource_group_id = resource.get('resource_group_id')
    
    # Remove resource from its resource group
    if resource_group_id and resource_group_id in resource_groups:
        resource_group = resource_groups[resource_group_id]
        if resource_id in resource_group['resource_ids']:
            resource_group['resource_ids'].remove(resource_id)
            resource_group['updated_at'] = get_timestamp()
    
    del resources[resource_id]
    return '', 204

# =============================================================================
# USER GROUP ENDPOINTS
# =============================================================================

@app.route('/user-groups', methods=['GET'])
def get_user_groups():
    """Get all user groups"""
    # Populate user details for each group
    groups_with_users = []
    for group in user_groups.values():
        group_copy = group.copy()
        group_copy['users'] = [users.get(uid, {"id": uid, "name": "Unknown", "email": "unknown@example.com"}) 
                              for uid in group['user_ids']]
        group_copy['user_count'] = len(group_copy['users'])
        groups_with_users.append(group_copy)
    
    return jsonify(groups_with_users), 200

@app.route('/user-groups', methods=['POST'])
def create_user_group():
    """Create a new user group"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'user_ids' not in data:
        return error_response("Name and user_ids are required", 400)
    
    group_id = generate_id()
    timestamp = get_timestamp()
    
    group = {
        "id": group_id,
        "name": data['name'],
        "description": data.get('description', ''),
        "user_ids": data['user_ids'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    user_groups[group_id] = group
    
    # Create OpenFGA member relationships for users in the group
    if data['user_ids']:
        created_relationships = create_member_relationships(group_id, data['user_ids'])
        print(f"🔗 Created {len(created_relationships)} member relationships for group '{data['name']}'")
    
    # Return group with user details
    response_group = group.copy()
    response_group['users'] = [users.get(uid, {"id": uid, "name": "Unknown", "email": "unknown@example.com"}) 
                              for uid in group['user_ids']]
    response_group['user_count'] = len(response_group['users'])
    
    return jsonify(response_group), 201

@app.route('/user-groups/<group_id>', methods=['GET'])
def get_user_group_by_id(group_id):
    """Get user group by ID"""
    if group_id not in user_groups:
        return error_response("User group not found", 404)
    
    group = user_groups[group_id].copy()
    group['users'] = [users.get(uid, {"id": uid, "name": "Unknown", "email": "unknown@example.com"}) 
                     for uid in group['user_ids']]
    group['user_count'] = len(group['users'])
    
    return jsonify(group), 200

@app.route('/user-groups/<group_id>', methods=['PUT'])
def update_user_group(group_id):
    """Update user group"""
    if group_id not in user_groups:
        return error_response("User group not found", 404)
    
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    group = user_groups[group_id]
    old_user_ids = set(group.get('user_ids', []))
    
    if 'name' in data:
        group['name'] = data['name']
    if 'description' in data:
        group['description'] = data['description']
    if 'user_ids' in data:
        new_user_ids = set(data['user_ids'])
        
        # Find users to add and remove
        users_to_add = new_user_ids - old_user_ids
        users_to_remove = old_user_ids - new_user_ids
        
        # Update the group's user_ids
        group['user_ids'] = data['user_ids']
        
        # Create relationships for new users
        if users_to_add:
            created_relationships = create_member_relationships(group_id, list(users_to_add))
            print(f"🔗 Created {len(created_relationships)} new member relationships for group '{group['name']}'")
        
        # Remove relationships for users no longer in the group
        if users_to_remove:
            removed_relationships = remove_member_relationships(group_id, list(users_to_remove))
            print(f"🔗 Removed {len(removed_relationships)} member relationships from group '{group['name']}'")
    
    group['updated_at'] = get_timestamp()
    
    # Return group with user details
    response_group = group.copy()
    response_group['users'] = [users.get(uid, {"id": uid, "name": "Unknown", "email": "unknown@example.com"}) 
                              for uid in group['user_ids']]
    response_group['user_count'] = len(response_group['users'])
    
    return jsonify(response_group), 200

@app.route('/user-groups/<group_id>', methods=['DELETE'])
def delete_user_group(group_id):
    """Delete user group"""
    if group_id not in user_groups:
        return error_response("User group not found", 404)
    
    group = user_groups[group_id]
    
    # Remove all member relationships for this group
    removed_relationships = remove_member_relationships(group_id)
    if removed_relationships:
        print(f"🔗 Removed {len(removed_relationships)} member relationships for deleted group '{group['name']}'")
    
    del user_groups[group_id]
    return '', 204

# =============================================================================
# RESOURCE GROUP ENDPOINTS
# =============================================================================

@app.route('/resource-groups', methods=['GET'])
def get_resource_groups():
    """Get all resource groups"""
    # Populate resource details for each group
    groups_with_resources = []
    for group in resource_groups.values():
        group_copy = group.copy()
        group_copy['resources'] = [resources.get(rid, {"id": rid, "type": "unknown", "name": "Unknown Resource"}) 
                                  for rid in group['resource_ids']]
        group_copy['resource_count'] = len(group_copy['resources'])
        groups_with_resources.append(group_copy)
    
    return jsonify(groups_with_resources), 200

@app.route('/resource-groups', methods=['POST'])
def create_resource_group():
    """Create a new resource group"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'resource_ids' not in data:
        return error_response("Name and resource_ids are required", 400)
    
    group_id = generate_id()
    timestamp = get_timestamp()
    
    group = {
        "id": group_id,
        "name": data['name'],
        "description": data.get('description', ''),
        "resource_ids": data['resource_ids'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    resource_groups[group_id] = group
    
    # Return group with resource details
    response_group = group.copy()
    response_group['resources'] = [resources.get(rid, {"id": rid, "type": "unknown", "name": "Unknown Resource"}) 
                                  for rid in group['resource_ids']]
    response_group['resource_count'] = len(response_group['resources'])
    
    return jsonify(response_group), 201

@app.route('/resource-groups/<group_id>', methods=['GET'])
def get_resource_group_by_id(group_id):
    """Get resource group by ID"""
    if group_id not in resource_groups:
        return error_response("Resource group not found", 404)
    
    group = resource_groups[group_id].copy()
    group['resources'] = [resources.get(rid, {"id": rid, "type": "unknown", "name": "Unknown Resource"}) 
                         for rid in group['resource_ids']]
    group['resource_count'] = len(group['resources'])
    
    return jsonify(group), 200

@app.route('/resource-groups/<group_id>', methods=['PUT'])
def update_resource_group(group_id):
    """Update resource group"""
    if group_id not in resource_groups:
        return error_response("Resource group not found", 404)
    
    data = request.get_json()
    if not data:
        return error_response("Invalid request data", 400)
    
    group = resource_groups[group_id]
    
    if 'name' in data:
        group['name'] = data['name']
    if 'description' in data:
        group['description'] = data['description']
    if 'resource_ids' in data:
        group['resource_ids'] = data['resource_ids']
    
    group['updated_at'] = get_timestamp()
    
    # Return group with resource details
    response_group = group.copy()
    response_group['resources'] = [resources.get(rid, {"id": rid, "type": "unknown", "name": "Unknown Resource"}) 
                                  for rid in group['resource_ids']]
    response_group['resource_count'] = len(response_group['resources'])
    
    return jsonify(response_group), 200

@app.route('/resource-groups/<group_id>', methods=['DELETE'])
def delete_resource_group(group_id):
    """Delete resource group"""
    if group_id not in resource_groups:
        return error_response("Resource group not found", 404)
    
    del resource_groups[group_id]
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
    
    filtered_relationships = list(relationships.values())
    
    # Apply filters
    if user_filter:
        filtered_relationships = [r for r in filtered_relationships if user_filter in r['user']]
    if resource_filter:
        filtered_relationships = [r for r in filtered_relationships if resource_filter in r['object']]
    if relation_filter:
        filtered_relationships = [r for r in filtered_relationships if r['relation'] == relation_filter]
    
    # Apply pagination
    paginated = filtered_relationships[offset:offset + limit]
    
    return jsonify(paginated), 200

@app.route('/relationships', methods=['POST'])
def create_relationship():
    """Create a new relationship"""
    data = request.get_json()
    
    if not data or 'user' not in data or 'relation' not in data or 'object' not in data:
        return error_response("User, relation, and object are required", 400)
    
    # Check if relationship already exists
    for rel in relationships.values():
        if (rel['user'] == data['user'] and 
            rel['relation'] == data['relation'] and 
            rel['object'] == data['object']):
            return jsonify({
                "error": "conflict",
                "message": "Relationship already exists"
            }), 409
    
    relationship_id = generate_id()
    timestamp = get_timestamp()
    
    relationship = {
        "id": relationship_id,
        "user": data['user'],
        "relation": data['relation'],
        "object": data['object'],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    relationships[relationship_id] = relationship
    return jsonify(relationship), 201

@app.route('/relationships/<relationship_id>', methods=['GET'])
def get_relationship_by_id(relationship_id):
    """Get relationship by ID"""
    if relationship_id not in relationships:
        return jsonify({
            "error": "not_found",
            "message": "Relationship not found"
        }), 404
    
    return jsonify(relationships[relationship_id]), 200

@app.route('/relationships/<relationship_id>', methods=['PUT'])
def update_relationship(relationship_id):
    """Update relationship"""
    if relationship_id not in relationships:
        return jsonify({
            "error": "not_found",
            "message": "Relationship not found"
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "bad_request",
            "message": "Invalid input"
        }), 400
    
    relationship = relationships[relationship_id]
    
    if 'user' in data:
        relationship['user'] = data['user']
    if 'relation' in data:
        relationship['relation'] = data['relation']
    if 'object' in data:
        relationship['object'] = data['object']
    
    relationship['updated_at'] = get_timestamp()
    
    return jsonify(relationship), 200

@app.route('/relationships/<relationship_id>', methods=['DELETE'])
def delete_relationship(relationship_id):
    """Delete relationship"""
    if relationship_id not in relationships:
        return jsonify({
            "error": "not_found",
            "message": "Relationship not found"
        }), 404
    
    del relationships[relationship_id]
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
    
    # Check if relationship exists
    allowed = False
    for rel in relationships.values():
        if (rel['user'] == data['user'] and 
            rel['relation'] == data['relation'] and 
            rel['object'] == data['object']):
            allowed = True
            break
    
    return jsonify({
        "allowed": allowed,
        "checked_at": get_timestamp()
    }), 200

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Add some sample data for testing
    
    # Sample users
    sample_users = [
        {"name": "Alice Johnson", "email": "alice@example.com"},
        {"name": "Bob Smith", "email": "bob@example.com"},
        {"name": "Charlie Brown", "email": "charlie@example.com"}
    ]
    
    for user_data in sample_users:
        user_id = generate_id()
        timestamp = get_timestamp()
        users[user_id] = {
            "id": user_id,
            "name": user_data["name"],
            "email": user_data["email"],
            "created_at": timestamp,
            "updated_at": timestamp
        }
    
    # Sample resource groups first (since resources require them)
    sample_resource_groups = [
        {"name": "Project Documents", "description": "Documents related to project planning and execution"},
        {"name": "System Resources", "description": "System-level resources and configurations"},
        {"name": "Shared Assets", "description": "Shared files and documents accessible to team members"}
    ]
    
    for group_data in sample_resource_groups:
        group_id = generate_id()
        timestamp = get_timestamp()
        resource_groups[group_id] = {
            "id": group_id,
            "name": group_data["name"],
            "description": group_data["description"],
            "resource_ids": [],
            "created_at": timestamp,
            "updated_at": timestamp
        }
    
    # Sample resources (now with resource groups)
    group_ids = list(resource_groups.keys())
    sample_resources = [
        {"resource_type": "document", "resource_name": "Project Plan", "metadata": {"category": "planning"}, "resource_group_id": group_ids[0]},
        {"resource_type": "project", "resource_name": "Rebecca API", "metadata": {"status": "active"}, "resource_group_id": group_ids[1]},
        {"resource_type": "folder", "resource_name": "Shared Documents", "metadata": {"access": "team"}, "resource_group_id": group_ids[2]}
    ]
    
    for resource_data in sample_resources:
        resource_id = generate_id()
        timestamp = get_timestamp()
        resource = {
            "id": resource_id,
            "type": resource_data["resource_type"],
            "name": resource_data["resource_name"],
            "metadata": resource_data["metadata"],
            "resource_group_id": resource_data["resource_group_id"],
            "created_at": timestamp,
            "updated_at": timestamp
        }
        resources[resource_id] = resource
        
        # Add resource to its group
        resource_groups[resource_data["resource_group_id"]]["resource_ids"].append(resource_id)
    
    # Sample relationships
    user_ids = list(users.keys())
    resource_ids = list(resources.keys())
    
    if user_ids and resource_ids:
        sample_relationships = [
            {"user": f"user:{user_ids[0]}", "relation": "owner", "object": f"document:{resource_ids[0]}"},
            {"user": f"user:{user_ids[1]}", "relation": "editor", "object": f"document:{resource_ids[0]}"},
            {"user": f"user:{user_ids[2]}", "relation": "viewer", "object": f"project:{resource_ids[1]}"}
        ]
        
        for rel_data in sample_relationships:
            rel_id = generate_id()
            timestamp = get_timestamp()
            relationships[rel_id] = {
                "id": rel_id,
                "user": rel_data["user"],
                "relation": rel_data["relation"],
                "object": rel_data["object"],
                "created_at": timestamp,
                "updated_at": timestamp
            }
    
    print("🚀 Starting Rebecca API server...")
    print("📊 Sample data loaded:")
    print(f"   - {len(users)} users")
    print(f"   - {len(resources)} resources") 
    print(f"   - {len(resource_groups)} resource groups")
    print(f"   - {len(relationships)} relationships")
    print("🌐 Server running on http://localhost:8000")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
