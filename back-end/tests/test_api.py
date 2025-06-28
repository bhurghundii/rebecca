#!/usr/bin/env python3
"""
Simple test script for Rebecca API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_users():
    """Test user endpoints"""
    print("👥 Testing user endpoints...")
    
    # Get all users
    response = requests.get(f"{BASE_URL}/users")
    print(f"GET /users - Status: {response.status_code}")
    users = response.json()
    print(f"Found {len(users)} users")
    
    if users:
        user_id = users[0]['id']
        print(f"Testing with user ID: {user_id}")
        
        # Get specific user
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"GET /users/{user_id} - Status: {response.status_code}")
    
    # Create new user
    new_user = {
        "name": "Test User",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=new_user)
    print(f"POST /users - Status: {response.status_code}")
    if response.status_code == 201:
        created_user = response.json()
        print(f"Created user: {created_user['name']} ({created_user['id']})")
    print()

def test_resources():
    """Test resource endpoints"""
    print("📁 Testing resource endpoints...")
    
    # Get all resources
    response = requests.get(f"{BASE_URL}/resources")
    print(f"GET /resources - Status: {response.status_code}")
    resources = response.json()
    print(f"Found {len(resources)} resources")
    
    # Create new resource
    new_resource = {
        "resource_type": "document",
        "resource_name": "Test Document",
        "metadata": {
            "description": "A test document",
            "category": "testing"
        }
    }
    response = requests.post(f"{BASE_URL}/resources", json=new_resource)
    print(f"POST /resources - Status: {response.status_code}")
    if response.status_code == 201:
        created_resource = response.json()
        print(f"Created resource: {created_resource['name']} ({created_resource['id']})")
    print()

def test_relationships():
    """Test relationship endpoints"""
    print("🔗 Testing relationship endpoints...")
    
    # Get all relationships
    response = requests.get(f"{BASE_URL}/relationships")
    print(f"GET /relationships - Status: {response.status_code}")
    relationships = response.json()
    print(f"Found {len(relationships)} relationships")
    
    # Test relationship check
    if relationships:
        rel = relationships[0]
        check_data = {
            "user": rel["user"],
            "relation": rel["relation"],
            "object": rel["object"]
        }
        response = requests.post(f"{BASE_URL}/relationships/check", json=check_data)
        print(f"POST /relationships/check - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Permission check result: {result['allowed']}")
    print()

def main():
    """Run all tests"""
    print("🧪 Testing Rebecca API endpoints...")
    print("=" * 50)
    
    try:
        test_health()
        test_users()
        test_resources()
        test_relationships()
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main()
