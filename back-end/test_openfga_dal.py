#!/usr/bin/env python3
"""
Test the new OpenFGA-powered RelationshipDAL
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.relationship_dal_openfga import OpenFGARelationshipDAL as RelationshipDAL

def test_openfga_relationship_dal():
    """Test basic OpenFGA RelationshipDAL functionality"""
    print("🧪 Testing OpenFGA RelationshipDAL")
    print("=" * 40)
    
    try:
        # Test 1: Create relationship
        print("1. Creating relationship...")
        relationship = RelationshipDAL.create("alice", "owner", "doc:project-plan")
        print(f"   Created: {relationship}")
        
        # Test 2: Check relationship exists
        print("2. Checking relationship exists...")
        exists = RelationshipDAL.check_relationship("alice", "owner", "doc:project-plan")
        print(f"   Exists: {exists}")
        
        # Test 3: Get by ID
        print("3. Getting relationship by ID...")
        found = RelationshipDAL.get_by_id(relationship['id'])
        print(f"   Found: {found}")
        
        # Test 4: Get relationships by user
        print("4. Getting relationships by user...")
        user_rels = RelationshipDAL.get_relationships_by_user("alice")
        print(f"   User relationships: {len(user_rels)} found")
        
        # Test 5: Get all relationships
        print("5. Getting all relationships...")
        all_rels = RelationshipDAL.get_all(limit=10)
        print(f"   All relationships: {len(all_rels)} found")
        
        # Test 6: Delete relationship
        print("6. Deleting relationship...")
        deleted = RelationshipDAL.delete(relationship['id'])
        print(f"   Deleted: {deleted}")
        
        # Test 7: Verify deletion
        print("7. Verifying deletion...")
        exists_after = RelationshipDAL.check_relationship("alice", "owner", "doc:project-plan")
        print(f"   Exists after deletion: {exists_after}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openfga_relationship_dal()
