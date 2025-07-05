#!/usr/bin/env python3
"""
Test simulating what the matrix UI would do when creating a group relationship
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_matrix_group_relationship():
    """Test creating a group relationship exactly like the matrix UI would"""
    
    print("🧪 Testing matrix group relationship creation...")
    
    # Get the first user group
    response = requests.get(f"{API_BASE}/user-groups")
    if response.status_code != 200:
        print(f"❌ Failed to get user groups: {response.status_code}")
        return
    
    user_groups = response.json()
    if not user_groups:
        print("❌ No user groups found")
        return
    
    # Get the first resource
    response = requests.get(f"{API_BASE}/resources")
    if response.status_code != 200:
        print(f"❌ Failed to get resources: {response.status_code}")
        return
    
    resources = response.json()
    if not resources:
        print("❌ No resources found")
        return
    
    # Simulate what the updateMatrixGroupRelation function would do
    group = user_groups[0]
    resource = resources[0]
    
    print(f"✅ Testing with group: {group['name']} (ID: {group['id']})")
    print(f"✅ Testing with resource: {resource['name']} (ID: {resource['id']}, type: {resource['type']})")
    
    # Check if any existing relationship exists first (like the UI does)
    existing_relationships = requests.get(f"{API_BASE}/relationships").json()
    
    # Look for existing group-resource relationship
    group_user_id = f"group:{group['id']}"
    resource_object = f"{resource['type']}:{resource['id']}"
    
    existing_relation = None
    for rel in existing_relationships:
        if rel['user'] == group_user_id and rel['object'] == resource_object:
            existing_relation = rel
            break
    
    if existing_relation:
        print(f"⚠️  Found existing relationship: {existing_relation}")
        # Update it to viewer
        if existing_relation['relation'] != 'viewer':
            print("🔄 Updating existing relationship to viewer...")
            update_data = {"relation": "viewer"}
            response = requests.put(f"{API_BASE}/relationships/{existing_relation['id']}", json=update_data)
            print(f"   Update result: {response.status_code}")
            if response.status_code == 200:
                print(f"   Updated: {response.json()}")
            else:
                print(f"   Error: {response.text}")
        else:
            print("✅ Relationship already set to viewer")
    else:
        # Create new relationship (this is what the matrix UI would do)
        print("🔨 Creating new group relationship...")
        relationship_data = {
            "user": group_user_id,
            "relation": "viewer", 
            "object": resource_object
        }
        
        print(f"📤 Sending: {relationship_data}")
        response = requests.post(f"{API_BASE}/relationships", json=relationship_data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created successfully: {result}")
            
            # Now verify it appears in the relationships list
            print("🔍 Verifying relationship appears in list...")
            updated_relationships = requests.get(f"{API_BASE}/relationships").json()
            
            found = False
            for rel in updated_relationships:
                if rel['user'] == group_user_id and rel['object'] == resource_object:
                    print(f"✅ Found in list: {rel}")
                    found = True
                    break
            
            if not found:
                print("❌ Relationship not found in list after creation!")
                
        elif response.status_code == 409:
            print("⚠️  Relationship already exists")
        else:
            print(f"❌ Failed to create: {response.status_code}")
            print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_matrix_group_relationship()
