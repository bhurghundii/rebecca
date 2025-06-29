"""
Sample data loader for Rebecca API
"""
from .config import init_database, reset_database
from .user_dal import UserDAL
from .resource_dal import ResourceDAL
from .resource_group_dal import ResourceGroupDAL
from .user_group_dal import UserGroupDAL
from .relationship_dal import RelationshipDAL

def load_sample_data():
    """Load sample data into the database"""
    print("📦 Loading sample data...")
    
    # Check if we already have data
    existing_users = UserDAL.get_all()
    if existing_users:
        print("   ℹ️  Sample data already exists, skipping...")
        return {
            'users': len(existing_users),
            'resource_groups': len(ResourceGroupDAL.get_all()),
            'resources': len(ResourceDAL.get_all()),
            'user_groups': len(UserGroupDAL.get_all()),
            'relationships': len(RelationshipDAL.get_all())
        }
    
    # Sample users
    sample_users = [
        {"name": "Alice Johnson", "email": "alice@example.com"},
        {"name": "Bob Smith", "email": "bob@example.com"},
        {"name": "Charlie Brown", "email": "charlie@example.com"}
    ]
    
    created_users = []
    for user_data in sample_users:
        try:
            user = UserDAL.create(user_data["name"], user_data["email"])
            created_users.append(user)
            print(f"   ✅ Created user: {user['name']}")
        except Exception as e:
            # User might already exist, try to get it
            existing_user = UserDAL.get_by_email(user_data["email"])
            if existing_user:
                created_users.append(existing_user)
                print(f"   ℹ️  User already exists: {existing_user['name']}")
            else:
                print(f"   ❌ Failed to create user {user_data['name']}: {e}")
    
    # Sample resource groups
    sample_resource_groups = [
        {"name": "Project Documents", "description": "Documents related to project planning and execution"},
        {"name": "System Resources", "description": "System-level resources and configurations"},
        {"name": "Shared Assets", "description": "Shared files and documents accessible to team members"}
    ]
    
    created_resource_groups = []
    for group_data in sample_resource_groups:
        try:
            group = ResourceGroupDAL.create(group_data["name"], group_data["description"])
            created_resource_groups.append(group)
            print(f"   ✅ Created resource group: {group['name']}")
        except Exception as e:
            print(f"   ❌ Failed to create resource group {group_data['name']}: {e}")
    
    # Sample resources
    sample_resources = [
        {"resource_type": "document", "name": "Project Plan", "metadata": {"category": "planning"}, "group_idx": 0},
        {"resource_type": "project", "name": "Rebecca API", "metadata": {"status": "active"}, "group_idx": 1},
        {"resource_type": "folder", "name": "Shared Documents", "metadata": {"access": "team"}, "group_idx": 2}
    ]
    
    created_resources = []
    for resource_data in sample_resources:
        if resource_data["group_idx"] < len(created_resource_groups):
            resource_group_id = created_resource_groups[resource_data["group_idx"]]["id"]
            try:
                resource = ResourceDAL.create(
                    resource_data["resource_type"],
                    resource_data["name"],
                    resource_group_id,
                    resource_data["metadata"]
                )
                created_resources.append(resource)
                print(f"   ✅ Created resource: {resource['name']}")
            except Exception as e:
                print(f"   ❌ Failed to create resource {resource_data['name']}: {e}")
    
    # Sample user groups
    created_user_groups = []
    if len(created_users) >= 3:
        sample_user_groups = [
            {"name": "Admin Team", "description": "System administrators", "user_indices": [0, 1]},
            {"name": "Project Team", "description": "Project contributors", "user_indices": [1, 2]},
            {"name": "All Users", "description": "All system users", "user_indices": [0, 1, 2]}
        ]
        
        for group_data in sample_user_groups:
            user_ids = [created_users[i]["id"] for i in group_data["user_indices"] if i < len(created_users)]
            try:
                group = UserGroupDAL.create(group_data["name"], user_ids, group_data["description"])
                created_user_groups.append(group)
                print(f"   ✅ Created user group: {group['name']} with {len(user_ids)} members")
            except Exception as e:
                print(f"   ❌ Failed to create user group {group_data['name']}: {e}")
    
    # Sample relationships
    if created_users and created_resources:
        sample_relationships = [
            {"user": f"user:{created_users[0]['id']}", "relation": "owner", "object": f"document:{created_resources[0]['id']}"},
            {"user": f"user:{created_users[1]['id']}", "relation": "editor", "object": f"document:{created_resources[0]['id']}"},
            {"user": f"user:{created_users[2]['id']}", "relation": "viewer", "object": f"project:{created_resources[1]['id']}"}
        ]
        
        for rel_data in sample_relationships:
            try:
                relationship = RelationshipDAL.create(
                    rel_data["user"],
                    rel_data["relation"],
                    rel_data["object"]
                )
                print(f"   ✅ Created relationship: {rel_data['user']} -> {rel_data['relation']} -> {rel_data['object']}")
            except Exception as e:
                print(f"   ❌ Failed to create relationship: {e}")
    
    print("✅ Sample data loaded successfully!")
    return {
        'users': len(created_users),
        'resource_groups': len(created_resource_groups),
        'resources': len(created_resources),
        'user_groups': len(created_user_groups),
        'relationships': len(sample_relationships) if 'sample_relationships' in locals() else 0
    }

def reset_and_load_sample_data():
    """Reset database and load sample data"""
    print("🔄 Resetting database...")
    reset_database()
    return load_sample_data()

if __name__ == '__main__':
    # Initialize database and load sample data
    init_database()
    stats = load_sample_data()
    print(f"\n📊 Database populated with:")
    for entity, count in stats.items():
        print(f"   - {count} {entity}")
