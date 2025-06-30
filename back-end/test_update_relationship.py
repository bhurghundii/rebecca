#!/usr/bin/env python3
"""
Test script to verify relationship update functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_relationship_update():
    print("🧪 Testing relationship update functionality...")
    
    # Step 1: Get current relationships
    response = requests.get(f"{BASE_URL}/relationships")
    if response.status_code != 200:
        print("❌ Failed to get relationships")
        return
    
    relationships = response.json()
    print(f"📋 Found {len(relationships)} relationships")
    
    if not relationships:
        print("⚠️  No relationships found, creating one first...")
        
        # Create a test relationship
        create_data = {
            "user": "user:charlie-brown",
            "relation": "viewer",
            "object": "document:test-doc"
        }
        
        response = requests.post(f"{BASE_URL}/relationships", json=create_data)
        if response.status_code != 201:
            print(f"❌ Failed to create test relationship: {response.status_code}")
            print(response.text)
            return
        
        created_rel = response.json()
        print(f"✅ Created test relationship: {created_rel}")
        time.sleep(1)  # Give OpenFGA time to process
        
        # Get the relationship ID
        relationships = [created_rel]
    
    # Step 2: Pick the first relationship to update
    test_rel = relationships[0]
    relationship_id = test_rel['id']
    current_relation = test_rel['relation']
    
    print(f"🔄 Testing update for relationship: {relationship_id}")
    print(f"   Current: {test_rel['user']} {current_relation} {test_rel['object']}")
    
    # Step 3: Update the relation (change viewer to editor or vice versa)
    new_relation = "editor" if current_relation == "viewer" else "viewer"
    
    # Make sure we only use valid relations
    valid_relations = ["owner", "editor", "viewer", "member"]
    if current_relation not in valid_relations:
        print(f"⚠️  Current relation '{current_relation}' is not in valid relations: {valid_relations}")
        return
    
    if new_relation not in valid_relations:
        new_relation = "editor" if current_relation != "editor" else "viewer"
    
    update_data = {
        "relation": new_relation
    }
    
    print(f"📝 Updating relation from '{current_relation}' to '{new_relation}'...")
    
    response = requests.put(f"{BASE_URL}/relationships/{relationship_id}", json=update_data)
    if response.status_code != 200:
        print(f"❌ Update failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    updated_rel = response.json()
    print(f"✅ Update response: {updated_rel}")
    
    # Step 4: Verify the update worked
    time.sleep(1)  # Give OpenFGA time to process
    
    response = requests.get(f"{BASE_URL}/relationships/{relationship_id}")
    if response.status_code == 404:
        print("⚠️  Original relationship ID no longer exists (expected for updates)")
        
        # Check if new relationship exists
        new_relationship_id = f"{test_rel['user']}:{new_relation}:{test_rel['object']}"
        response = requests.get(f"{BASE_URL}/relationships/{new_relationship_id}")
        if response.status_code == 200:
            final_rel = response.json()
            print(f"✅ Found updated relationship: {final_rel}")
            
            if final_rel['relation'] == new_relation:
                print("🎉 Update test PASSED!")
            else:
                print(f"❌ Update test FAILED: expected '{new_relation}', got '{final_rel['relation']}'")
        else:
            print(f"❌ Could not find updated relationship at {new_relationship_id}")
    else:
        # Original ID still exists, check if it was updated
        current_rel = response.json()
        if current_rel['relation'] == new_relation:
            print("🎉 Update test PASSED!")
        else:
            print(f"❌ Update test FAILED: expected '{new_relation}', got '{current_rel['relation']}'")
    
    # Step 5: Test OpenFGA directly
    print("\n🔍 Checking OpenFGA state...")
    old_tuple = f"{test_rel['user']} {current_relation} {test_rel['object']}"
    new_tuple = f"{test_rel['user']} {new_relation} {test_rel['object']}"
    
    # Check permission for old relation
    check_data = {
        "user": test_rel['user'],
        "relation": current_relation,
        "object": test_rel['object']
    }
    
    response = requests.post(f"{BASE_URL}/relationships/check", json=check_data)
    if response.status_code == 200:
        old_check = response.json()
        print(f"📊 Old relation ({current_relation}) check: {old_check}")
    
    # Check permission for new relation
    check_data = {
        "user": test_rel['user'],
        "relation": new_relation,
        "object": test_rel['object']
    }
    
    response = requests.post(f"{BASE_URL}/relationships/check", json=check_data)
    if response.status_code == 200:
        new_check = response.json()
        print(f"📊 New relation ({new_relation}) check: {new_check}")
        
        if new_check.get('allowed'):
            print("✅ OpenFGA correctly shows new permission")
        else:
            print("❌ OpenFGA does not show new permission")

if __name__ == "__main__":
    test_relationship_update()
