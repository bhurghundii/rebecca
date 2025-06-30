#!/usr/bin/env python3
"""
Test script to verify group relationship creation via API
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_group_relationship_creation():
    """Test creating a group relationship via the API"""
    
    print("🧪 Testing group relationship creation...")
    
    # First, get available user groups
    response = requests.get(f"{API_BASE}/user-groups")
    if response.status_code != 200:
        print(f"❌ Failed to get user groups: {response.status_code}")
        return
    
    user_groups = response.json()
    if not user_groups:
        print("❌ No user groups found")
        return
    
    print(f"✅ Found {len(user_groups)} user groups")
    
    # Get available resources
    response = requests.get(f"{API_BASE}/resources")
    if response.status_code != 200:
        print(f"❌ Failed to get resources: {response.status_code}")
        return
    
    resources = response.json()
    if not resources:
        print("❌ No resources found")
        return
    
    print(f"✅ Found {len(resources)} resources")
    
    # Try to create a group relationship
    test_group = user_groups[0]
    test_resource = resources[0]
    
    relationship_data = {
        "user": f"group:{test_group['id']}",
        "relation": "viewer",
        "object": f"{test_resource['type']}:{test_resource['id']}"
    }
    
    print(f"🔍 Creating relationship: {relationship_data}")
    
    response = requests.post(f"{API_BASE}/relationships", json=relationship_data)
    
    if response.status_code == 201:
        print("✅ Group relationship created successfully!")
        result = response.json()
        print(f"   Created: {result}")
    elif response.status_code == 409:
        print("⚠️  Relationship already exists")
    else:
        print(f"❌ Failed to create relationship: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Check if the relationship exists
    check_data = {
        "user": relationship_data["user"],
        "relation": relationship_data["relation"],
        "object": relationship_data["object"]
    }
    
    response = requests.post(f"{API_BASE}/relationships/check", json=check_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Relationship check result: {result['allowed']}")
    else:
        print(f"❌ Failed to check relationship: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_group_relationship_creation()
