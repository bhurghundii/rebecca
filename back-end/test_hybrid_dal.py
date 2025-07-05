#!/usr/bin/env python3
"""
Test the hybrid RelationshipDAL (SQLite + OpenFGA)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.relationship_dal import RelationshipDAL

def test_hybrid_dal():
    """Test the hybrid RelationshipDAL"""
    print("🔗 Testing Hybrid RelationshipDAL (SQLite + OpenFGA)")
    print("=" * 60)
    
    # Test creating a relationship
    print("\n1. Creating relationship...")
    relationship = RelationshipDAL.create("user:alice", "owner", "doc:project-plan")
    print(f"Created: {relationship}")
    
    # Test checking the relationship (should use OpenFGA)
    print("\n2. Checking relationship with OpenFGA...")
    exists = RelationshipDAL.check_relationship("user:alice", "owner", "doc:project-plan")
    print(f"Relationship exists: {exists}")
    
    # Test that non-existent relationship returns False
    print("\n3. Checking non-existent relationship...")
    not_exists = RelationshipDAL.check_relationship("user:bob", "owner", "doc:project-plan")
    print(f"Non-existent relationship exists: {not_exists}")
    
    # Test getting relationships from SQLite
    print("\n4. Getting all relationships from SQLite...")
    all_relationships = RelationshipDAL.get_all()
    print(f"Found {len(all_relationships)} relationships in SQLite")
    for rel in all_relationships[-3:]:  # Show last 3
        print(f"  - {rel['user']} {rel['relation']} {rel['object']}")
    
    # Test deleting relationship
    print(f"\n5. Deleting relationship {relationship['id']}...")
    deleted = RelationshipDAL.delete(relationship['id'])
    print(f"Deleted: {deleted}")
    
    # Verify it's gone from OpenFGA
    print("\n6. Verifying deletion in OpenFGA...")
    exists_after_delete = RelationshipDAL.check_relationship("user:alice", "owner", "doc:project-plan")
    print(f"Relationship exists after delete: {exists_after_delete}")
    
    print("\n✅ Hybrid RelationshipDAL test completed!")

if __name__ == "__main__":
    test_hybrid_dal()
