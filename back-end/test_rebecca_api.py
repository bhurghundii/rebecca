#!/usr/bin/env python3
"""
Pytest test suite for Rebecca API endpoints
"""
import pytest
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Test fixtures and setup
@pytest.fixture(scope="session", autouse=True)
def check_server():
    """Check if server is running before running tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.fail("Server is not responding correctly")
    except requests.exceptions.ConnectionError:
        pytest.fail("Server is not running. Please start the Flask server on http://localhost:8000")

@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    assert response.status_code == 201
    user = response.json()
    
    yield user
    
    # Cleanup - delete the user after test
    try:
        requests.delete(f"{BASE_URL}/users/{user['id']}")
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def sample_resource():
    """Create a sample resource for testing"""
    resource_data = {
        "resource_type": "document",
        "resource_name": "Test Document",
        "metadata": {
            "description": "A test document",
            "category": "testing"
        }
    }
    response = requests.post(f"{BASE_URL}/resources", json=resource_data)
    assert response.status_code == 201
    resource = response.json()
    
    yield resource
    
    # Cleanup - delete the resource after test
    try:
        requests.delete(f"{BASE_URL}/resources/{resource['id']}")
    except:
        pass  # Ignore cleanup errors

@pytest.fixture
def sample_relationship(sample_user, sample_resource):
    """Create a sample relationship for testing"""
    relationship_data = {
        "user": f"user:{sample_user['id']}",
        "relation": "viewer",
        "object": f"document:{sample_resource['id']}"
    }
    response = requests.post(f"{BASE_URL}/relationships", json=relationship_data)
    assert response.status_code == 201
    relationship = response.json()
    
    yield relationship
    
    # Cleanup - delete the relationship after test
    try:
        requests.delete(f"{BASE_URL}/relationships/{relationship['id']}")
    except:
        pass  # Ignore cleanup errors

# Health Tests
class TestHealth:
    """Test health endpoint"""
    
    def test_health_check(self):
        """Test that health endpoint returns success"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "timestamp" in data
        assert "openfga_status" in data

# User Tests
class TestUsers:
    """Test user endpoints"""
    
    def test_get_all_users(self):
        """Test getting all users"""
        response = requests.get(f"{BASE_URL}/users")
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        # Should have at least the sample users from app startup
        assert len(users) >= 3
    
    def test_create_user(self):
        """Test creating a new user"""
        user_data = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        assert response.status_code == 201
        
        user = response.json()
        assert user["name"] == user_data["name"]
        assert user["email"] == user_data["email"]
        assert "id" in user
        assert "created_at" in user
        assert "updated_at" in user
        
        # Cleanup
        requests.delete(f"{BASE_URL}/users/{user['id']}")
    
    def test_create_user_missing_data(self):
        """Test creating user with missing required data"""
        # Missing email
        response = requests.post(f"{BASE_URL}/users", json={"name": "John"})
        assert response.status_code == 400
        
        # Missing name
        response = requests.post(f"{BASE_URL}/users", json={"email": "john@example.com"})
        assert response.status_code == 400
    
    def test_get_user_by_id(self, sample_user):
        """Test getting a specific user by ID"""
        response = requests.get(f"{BASE_URL}/users/{sample_user['id']}")
        assert response.status_code == 200
        
        user = response.json()
        assert user["id"] == sample_user["id"]
        assert user["name"] == sample_user["name"]
        assert user["email"] == sample_user["email"]
    
    def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/users/{fake_id}")
        assert response.status_code == 404
    
    def test_update_user(self, sample_user):
        """Test updating a user"""
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        response = requests.put(f"{BASE_URL}/users/{sample_user['id']}", json=update_data)
        assert response.status_code == 200
        
        user = response.json()
        assert user["name"] == update_data["name"]
        assert user["email"] == update_data["email"]
        assert user["id"] == sample_user["id"]
    
    def test_delete_user(self):
        """Test deleting a user"""
        # Create a user to delete
        user_data = {"name": "Delete Me", "email": "delete@example.com"}
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        user = response.json()
        
        # Delete the user
        response = requests.delete(f"{BASE_URL}/users/{user['id']}")
        assert response.status_code == 204
        
        # Verify user is gone
        response = requests.get(f"{BASE_URL}/users/{user['id']}")
        assert response.status_code == 404

# Resource Tests
class TestResources:
    """Test resource endpoints"""
    
    def test_get_all_resources(self):
        """Test getting all resources"""
        response = requests.get(f"{BASE_URL}/resources")
        assert response.status_code == 200
        
        resources = response.json()
        assert isinstance(resources, list)
        # Should have at least the sample resources from app startup
        assert len(resources) >= 3
    
    def test_create_resource(self):
        """Test creating a new resource"""
        resource_data = {
            "resource_type": "project",
            "resource_name": "Test Project",
            "metadata": {
                "description": "A test project",
                "status": "active"
            }
        }
        response = requests.post(f"{BASE_URL}/resources", json=resource_data)
        assert response.status_code == 201
        
        resource = response.json()
        assert resource["type"] == resource_data["resource_type"]
        assert resource["name"] == resource_data["resource_name"]
        assert resource["metadata"] == resource_data["metadata"]
        assert "id" in resource
        assert "created_at" in resource
        assert "updated_at" in resource
        
        # Cleanup
        requests.delete(f"{BASE_URL}/resources/{resource['id']}")
    
    def test_create_resource_invalid_type(self):
        """Test creating resource with invalid type"""
        resource_data = {
            "resource_type": "invalid_type",
            "resource_name": "Test"
        }
        response = requests.post(f"{BASE_URL}/resources", json=resource_data)
        assert response.status_code == 400
    
    def test_get_resource_by_id(self, sample_resource):
        """Test getting a specific resource by ID"""
        response = requests.get(f"{BASE_URL}/resources/{sample_resource['id']}")
        assert response.status_code == 200
        
        resource = response.json()
        assert resource["id"] == sample_resource["id"]
        assert resource["name"] == sample_resource["name"]
        assert resource["type"] == sample_resource["type"]
    
    def test_update_resource(self, sample_resource):
        """Test updating a resource"""
        update_data = {
            "resource_name": "Updated Resource Name",
            "metadata": {"updated": True}
        }
        response = requests.put(f"{BASE_URL}/resources/{sample_resource['id']}", json=update_data)
        assert response.status_code == 200
        
        resource = response.json()
        assert resource["name"] == update_data["resource_name"]
        assert resource["metadata"] == update_data["metadata"]
        assert resource["id"] == sample_resource["id"]

# Relationship Tests
class TestRelationships:
    """Test relationship endpoints"""
    
    def test_get_all_relationships(self):
        """Test getting all relationships"""
        response = requests.get(f"{BASE_URL}/relationships")
        assert response.status_code == 200
        
        relationships = response.json()
        assert isinstance(relationships, list)
        # Should have at least the sample relationships from app startup
        assert len(relationships) >= 3
    
    def test_create_relationship(self, sample_user, sample_resource):
        """Test creating a new relationship"""
        relationship_data = {
            "user": f"user:{sample_user['id']}",
            "relation": "editor",
            "object": f"document:{sample_resource['id']}"
        }
        response = requests.post(f"{BASE_URL}/relationships", json=relationship_data)
        assert response.status_code == 201
        
        relationship = response.json()
        assert relationship["user"] == relationship_data["user"]
        assert relationship["relation"] == relationship_data["relation"]
        assert relationship["object"] == relationship_data["object"]
        assert "id" in relationship
        
        # Cleanup
        requests.delete(f"{BASE_URL}/relationships/{relationship['id']}")
    
    def test_create_duplicate_relationship(self, sample_relationship):
        """Test creating a duplicate relationship"""
        duplicate_data = {
            "user": sample_relationship["user"],
            "relation": sample_relationship["relation"],
            "object": sample_relationship["object"]
        }
        response = requests.post(f"{BASE_URL}/relationships", json=duplicate_data)
        assert response.status_code == 409
    
    def test_check_relationship_allowed(self, sample_relationship):
        """Test checking a relationship that should be allowed"""
        check_data = {
            "user": sample_relationship["user"],
            "relation": sample_relationship["relation"],
            "object": sample_relationship["object"]
        }
        response = requests.post(f"{BASE_URL}/relationships/check", json=check_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["allowed"] is True
        assert "checked_at" in result
    
    def test_check_relationship_denied(self, sample_user, sample_resource):
        """Test checking a relationship that should be denied"""
        check_data = {
            "user": f"user:{sample_user['id']}",
            "relation": "owner",  # This relationship doesn't exist
            "object": f"document:{sample_resource['id']}"
        }
        response = requests.post(f"{BASE_URL}/relationships/check", json=check_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["allowed"] is False
        assert "checked_at" in result
    
    def test_get_relationships_with_filters(self, sample_relationship):
        """Test getting relationships with query filters"""
        # Filter by user
        response = requests.get(f"{BASE_URL}/relationships?user={sample_relationship['user']}")
        assert response.status_code == 200
        relationships = response.json()
        assert len(relationships) >= 1
        
        # Filter by relation
        response = requests.get(f"{BASE_URL}/relationships?relation={sample_relationship['relation']}")
        assert response.status_code == 200
        relationships = response.json()
        assert len(relationships) >= 1

# User Group Tests
class TestUserGroups:
    """Test user group endpoints"""
    
    def test_get_all_user_groups(self):
        """Test getting all user groups"""
        response = requests.get(f"{BASE_URL}/user-groups")
        assert response.status_code == 200
        
        groups = response.json()
        assert isinstance(groups, list)
    
    def test_create_user_group(self, sample_user):
        """Test creating a user group"""
        group_data = {
            "name": "Test Group",
            "description": "A test group",
            "user_ids": [sample_user["id"]]
        }
        response = requests.post(f"{BASE_URL}/user-groups", json=group_data)
        assert response.status_code == 201
        
        group = response.json()
        assert group["name"] == group_data["name"]
        assert group["description"] == group_data["description"]
        assert group["user_count"] == 1
        assert len(group["users"]) == 1
        assert group["users"][0]["id"] == sample_user["id"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/user-groups/{group['id']}")

# Resource Group Tests  
class TestResourceGroups:
    """Test resource group endpoints"""
    
    def test_get_all_resource_groups(self):
        """Test getting all resource groups"""
        response = requests.get(f"{BASE_URL}/resource-groups")
        assert response.status_code == 200
        
        groups = response.json()
        assert isinstance(groups, list)
    
    def test_create_resource_group(self, sample_resource):
        """Test creating a resource group"""
        group_data = {
            "name": "Test Resource Group",
            "description": "A test resource group",
            "resource_ids": [sample_resource["id"]]
        }
        response = requests.post(f"{BASE_URL}/resource-groups", json=group_data)
        assert response.status_code == 201
        
        group = response.json()
        assert group["name"] == group_data["name"]
        assert group["description"] == group_data["description"]
        assert group["resource_count"] == 1
        assert len(group["resources"]) == 1
        assert group["resources"][0]["id"] == sample_resource["id"]
        
        # Cleanup
        requests.delete(f"{BASE_URL}/resource-groups/{group['id']}")

# Test OpenFGA Integration
# =============================================================================

def test_user_group_creates_member_relationships():
    """Test that creating a user group automatically creates OpenFGA member relationships"""
    # Create a test user first
    user_data = {
        "name": "Test User OpenFGA",
        "email": "testopenfga@example.com"
    }
    user_response = requests.post(f"{BASE_URL}/users", json=user_data)
    assert user_response.status_code == 201
    user = user_response.json()
    user_id = user['id']
    
    try:
        # Create a user group with this user
        group_data = {
            "name": "Test Group OpenFGA",
            "description": "Test group for OpenFGA integration",
            "user_ids": [user_id]
        }
        group_response = requests.post(f"{BASE_URL}/user-groups", json=group_data)
        assert group_response.status_code == 201
        group = group_response.json()
        group_id = group['id']
        
        # Check that a member relationship was created
        time.sleep(0.1)  # Brief pause for relationship creation
        relationships_response = requests.get(f"{BASE_URL}/relationships")
        assert relationships_response.status_code == 200
        relationships = relationships_response.json()
        
        # Find the member relationship
        member_relationship = None
        for rel in relationships:
            if (rel['user'] == f"user:{user_id}" and 
                rel['relation'] == 'member' and 
                rel['object'] == f"group:{group_id}"):
                member_relationship = rel
                break
        
        assert member_relationship is not None, "Member relationship should be created automatically"
        assert member_relationship['user'] == f"user:{user_id}"
        assert member_relationship['relation'] == 'member'
        assert member_relationship['object'] == f"group:{group_id}"
        
        # Test updating the group to remove the user
        updated_group_data = {
            "name": "Test Group OpenFGA Updated",
            "description": "Updated test group",
            "user_ids": []  # Remove the user
        }
        update_response = requests.put(f"{BASE_URL}/user-groups/{group_id}", json=updated_group_data)
        assert update_response.status_code == 200
        
        # Check that the member relationship was removed
        time.sleep(0.1)  # Brief pause for relationship removal
        relationships_response = requests.get(f"{BASE_URL}/relationships")
        assert relationships_response.status_code == 200
        updated_relationships = relationships_response.json()
        
        # The member relationship should no longer exist
        member_relationship_exists = False
        for rel in updated_relationships:
            if (rel['user'] == f"user:{user_id}" and 
                rel['relation'] == 'member' and 
                rel['object'] == f"group:{group_id}"):
                member_relationship_exists = True
                break
        
        assert not member_relationship_exists, "Member relationship should be removed when user is removed from group"
        
    finally:
        # Cleanup
        try:
            requests.delete(f"{BASE_URL}/user-groups/{group_id}")
        except:
            pass
        try:
            requests.delete(f"{BASE_URL}/users/{user_id}")
        except:
            pass

def test_user_group_deletion_removes_member_relationships():
    """Test that deleting a user group removes all member relationships"""
    # Create test users
    user1_data = {"name": "Test User 1", "email": "test1@example.com"}
    user2_data = {"name": "Test User 2", "email": "test2@example.com"}
    
    user1_response = requests.post(f"{BASE_URL}/users", json=user1_data)
    user2_response = requests.post(f"{BASE_URL}/users", json=user2_data)
    
    assert user1_response.status_code == 201
    assert user2_response.status_code == 201
    
    user1 = user1_response.json()
    user2 = user2_response.json()
    
    try:
        # Create a user group with both users
        group_data = {
            "name": "Test Group for Deletion",
            "description": "Test group to be deleted",
            "user_ids": [user1['id'], user2['id']]
        }
        group_response = requests.post(f"{BASE_URL}/user-groups", json=group_data)
        assert group_response.status_code == 201
        group = group_response.json()
        group_id = group['id']
        
        # Verify member relationships were created
        time.sleep(0.1)
        relationships_response = requests.get(f"{BASE_URL}/relationships")
        relationships = relationships_response.json()
        
        member_relationships = [
            rel for rel in relationships 
            if rel['relation'] == 'member' and rel['object'] == f"group:{group_id}"
        ]
        assert len(member_relationships) == 2, "Should have 2 member relationships"
        
        # Delete the group
        delete_response = requests.delete(f"{BASE_URL}/user-groups/{group_id}")
        assert delete_response.status_code == 204
        
        # Verify member relationships were removed
        time.sleep(0.1)
        relationships_response = requests.get(f"{BASE_URL}/relationships")
        updated_relationships = relationships_response.json()
        
        remaining_member_relationships = [
            rel for rel in updated_relationships 
            if rel['relation'] == 'member' and rel['object'] == f"group:{group_id}"
        ]
        assert len(remaining_member_relationships) == 0, "All member relationships should be removed when group is deleted"
        
    finally:
        # Cleanup users
        try:
            requests.delete(f"{BASE_URL}/users/{user1['id']}")
            requests.delete(f"{BASE_URL}/users/{user2['id']}")
        except:
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
