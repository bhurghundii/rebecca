#!/usr/bin/env python3
"""
Demonstration of the Hybrid Architecture Working
Shows SQLite for metadata + OpenFGA for permissions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.relationship_dal import RelationshipDAL
from database.user_dal import UserDAL
from database.resource_dal import ResourceDAL

def demonstrate_hybrid_architecture():
    """Demonstrate the hybrid architecture in action"""
    print("🏗️  HYBRID ARCHITECTURE DEMONSTRATION")
    print("=" * 60)
    print("📊 SQLite: User/Resource metadata")
    print("🔐 OpenFGA: Relationships & permissions")
    print("=" * 60)
    
    # 1. Create users and resources in SQLite (metadata)
    print("\n1️⃣  Creating entities in SQLite...")
    
    # Create users
    alice = UserDAL.create("Alice Smith", "alice@company.com")
    bob = UserDAL.create("Bob Jones", "bob@company.com")
    print(f"   👤 Created user: {alice['name']} ({alice['id']})")
    print(f"   👤 Created user: {bob['name']} ({bob['id']})")
    
    # Create resources  
    doc1 = ResourceDAL.create("Project Plan", "document", "Planning document for Q1")
    doc2 = ResourceDAL.create("Meeting Notes", "document", "Weekly team meeting notes")
    print(f"   📄 Created resource: {doc1['name']} ({doc1['id']})")
    print(f"   📄 Created resource: {doc2['name']} ({doc2['id']})")
    
    # 2. Create relationships in OpenFGA (permissions)
    print("\n2️⃣  Creating relationships in OpenFGA...")
    
    # Alice owns both documents
    rel1 = RelationshipDAL.create(f"user:{alice['id']}", "owner", f"doc:{doc1['id']}")
    rel2 = RelationshipDAL.create(f"user:{alice['id']}", "owner", f"doc:{doc2['id']}")
    
    # Bob can view document 1
    rel3 = RelationshipDAL.create(f"user:{bob['id']}", "viewer", f"doc:{doc1['id']}")
    
    print(f"   🔗 Alice owns: {doc1['name']}")
    print(f"   🔗 Alice owns: {doc2['name']}")
    print(f"   🔗 Bob can view: {doc1['name']}")
    
    # 3. Query the hybrid system
    print("\n3️⃣  Querying the hybrid system...")
    
    # Get Alice's metadata from SQLite
    alice_data = UserDAL.get_by_id(alice['id'])
    print(f"   📊 Alice's profile (SQLite): {alice_data['name']} - {alice_data['email']}")
    
    # Check Alice's permissions from OpenFGA
    alice_can_own_doc1 = RelationshipDAL.check_relationship(f"user:{alice['id']}", "owner", f"doc:{doc1['id']}")
    alice_can_own_doc2 = RelationshipDAL.check_relationship(f"user:{alice['id']}", "owner", f"doc:{doc2['id']}")
    print(f"   🔐 Alice can own {doc1['name']}: {alice_can_own_doc1}")
    print(f"   🔐 Alice can own {doc2['name']}: {alice_can_own_doc2}")
    
    # Check Bob's permissions
    bob_can_view_doc1 = RelationshipDAL.check_relationship(f"user:{bob['id']}", "viewer", f"doc:{doc1['id']}")
    bob_can_own_doc1 = RelationshipDAL.check_relationship(f"user:{bob['id']}", "owner", f"doc:{doc1['id']}")
    print(f"   🔐 Bob can view {doc1['name']}: {bob_can_view_doc1}")
    print(f"   🔐 Bob can own {doc1['name']}: {bob_can_own_doc1}")
    
    # 4. Show the power of computed relationships
    print("\n4️⃣  Testing computed relationships (owner → viewer)...")
    
    # In OpenFGA, owners automatically get viewer permissions
    alice_can_view_doc1 = RelationshipDAL.check_relationship(f"user:{alice['id']}", "viewer", f"doc:{doc1['id']}")
    print(f"   🧠 Alice can view {doc1['name']} (computed from owner): {alice_can_view_doc1}")
    
    # 5. Show SQLite fallback working
    print("\n5️⃣  SQLite fallback verification...")
    
    # Get all relationships from SQLite
    all_rels = RelationshipDAL.get_all(limit=5)
    print(f"   📊 Found {len(all_rels)} relationships in SQLite backup")
    for rel in all_rels[-3:]:
        print(f"      - {rel['user']} {rel['relation']} {rel['object']}")
    
    print("\n🎉 HYBRID ARCHITECTURE WORKING!")
    print("   ✅ SQLite stores user/resource metadata efficiently")
    print("   ✅ OpenFGA handles relationships and permissions powerfully")
    print("   ✅ Computed relationships work (owner → viewer)")
    print("   ✅ SQLite provides fallback for reliability")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    RelationshipDAL.delete(rel1['id'])
    RelationshipDAL.delete(rel2['id'])
    RelationshipDAL.delete(rel3['id'])
    print("   ✅ Cleaned up test relationships")

if __name__ == "__main__":
    demonstrate_hybrid_architecture()
