#!/usr/bin/env python3
"""
Test script to verify user group permissions work in OpenFGA
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_user_group_permissions():
    print("🧪 Testing user group permissions...")
    
    # Step 1: Get existing users and groups
    print("\n1️⃣ Getting existing data...")
    users_response = requests.get(f"{BASE_URL}/users")
    user_groups_response = requests.get(f"{BASE_URL}/user-groups")
    resources_response = requests.get(f"{BASE_URL}/resources")
    
    if any(r.status_code != 200 for r in [users_response, user_groups_response, resources_response]):
        print("❌ Failed to fetch existing data")
        return
    
    users = users_response.json()
    user_groups = user_groups_response.json()
    resources = resources_response.json()
    
    print(f"📊 Found {len(users)} users, {len(user_groups)} groups, {len(resources)} resources")
    
    if not users or not user_groups or not resources:
        print("⚠️  Need at least 1 user, 1 group, and 1 resource to test")
        return
    
    # Pick test subjects
    test_user = users[0]
    test_group = user_groups[0] 
    test_resource = resources[0]
    
    print(f"🎯 Test subjects:")
    print(f"   User: {test_user['name']} ({test_user['id']})")
    print(f"   Group: {test_group['name']} ({test_group['id']})")
    print(f"   Resource: {test_resource['name']} ({test_resource['id']})")
    
    # Step 2: Create a relationship between the group and resource
    print(f"\n2️⃣ Creating group permission: {test_group['name']} viewer {test_resource['name']}...")
    
    create_data = {
        "user": f"group:{test_group['id']}",
        "relation": "viewer",
        "object": f"{test_resource['type']}:{test_resource['id']}"
    }
    
    create_response = requests.post(f"{BASE_URL}/relationships", json=create_data)
    if create_response.status_code != 201:
        print(f"❌ Failed to create group relationship: {create_response.status_code}")
        print(create_response.text)
        return
    
    created_rel = create_response.json()
    print(f"✅ Created group relationship: {created_rel}")
    
    time.sleep(2)  # Give OpenFGA time to process
    
    # Step 3: Check if the user (who is a member of the group) has the permission
    print(f"\n3️⃣ Checking if user inherits permission from group...")
    
    # First check the group permission directly
    group_check_data = {
        "user": f"group:{test_group['id']}",
        "relation": "viewer", 
        "object": f"{test_resource['type']}:{test_resource['id']}"
    }
    
    group_check_response = requests.post(f"{BASE_URL}/relationships/check", json=group_check_data)
    if group_check_response.status_code == 200:
        group_check_result = group_check_response.json()
        print(f"📊 Group permission check: {group_check_result}")
        
        if group_check_result.get('allowed'):
            print("✅ Group has direct permission!")
        else:
            print("❌ Group does not have permission")
    
    # Now check if a user in the group inherits the permission
    # We need to make sure the user is actually a member of the group first
    print(f"\n4️⃣ Checking user membership in group...")
    
    member_check_data = {
        "user": f"user:{test_user['id']}",
        "relation": "member",
        "object": f"group:{test_group['id']}"
    }
    
    member_check_response = requests.post(f"{BASE_URL}/relationships/check", json=member_check_data)
    if member_check_response.status_code == 200:
        member_result = member_check_response.json()
        print(f"📊 User membership check: {member_result}")
        
        if member_result.get('allowed'):
            print("✅ User is a member of the group!")
            
            # Now check if the user inherits the viewer permission
            print(f"\n5️⃣ Checking if user inherits viewer permission...")
            
            user_permission_check_data = {
                "user": f"user:{test_user['id']}",
                "relation": "viewer",
                "object": f"{test_resource['type']}:{test_resource['id']}"
            }
            
            user_permission_response = requests.post(f"{BASE_URL}/relationships/check", json=user_permission_check_data)
            if user_permission_response.status_code == 200:
                user_permission_result = user_permission_response.json()
                print(f"📊 User permission inheritance check: {user_permission_result}")
                
                if user_permission_result.get('allowed'):
                    print("🎉 SUCCESS! User inherited permission from group!")
                else:
                    print("❌ FAILED! User did not inherit permission from group")
            else:
                print(f"❌ Failed to check user permission: {user_permission_response.status_code}")
        else:
            print("⚠️  User is not a member of the group, cannot test inheritance")
    else:
        print(f"❌ Failed to check user membership: {member_check_response.status_code}")
    
    # Step 6: Clean up - delete the test relationship
    print(f"\n6️⃣ Cleaning up test relationship...")
    
    relationship_id = created_rel['id']
    delete_response = requests.delete(f"{BASE_URL}/relationships/{relationship_id}")
    if delete_response.status_code == 204:
        print("✅ Test relationship deleted successfully")
    else:
        print(f"⚠️  Failed to delete test relationship: {delete_response.status_code}")

if __name__ == "__main__":
    test_user_group_permissions()
