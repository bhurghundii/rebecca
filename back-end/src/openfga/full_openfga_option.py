"""
Option 2: Full OpenFGA Migration - How It Actually Works

This shows how you could theoretically move EVERYTHING to OpenFGA,
including what we traditionally think of as "entity data".
"""

# THE MIND-BENDING PART: ENTITIES AS OBJECTS IN OPENFGA
# =====================================================

"""
Instead of storing user data in SQLite like:
┌─────────┬───────────┬─────────────────┐
│ user_id │   name    │      email      │
├─────────┼───────────┼─────────────────┤
│ alice   │ Alice     │ alice@email.com │
│ bob     │ Bob Smith │ bob@email.com   │
└─────────┴───────────┴─────────────────┘

You represent it as OpenFGA relationships:
user:alice has_name "Alice"
user:alice has_email "alice@email.com"  
user:alice created_at "2024-01-15T10:30:00Z"
user:bob has_name "Bob Smith"
user:bob has_email "bob@email.com"
"""

# AUTHORIZATION MODEL FOR FULL OPENFGA
# ===================================

FULL_OPENFGA_MODEL = {
    "schema_version": "1.1",
    "type_definitions": [
        {
            "type": "user",
            "relations": {
                # Traditional relationships
                "owner": {"this": {}},
                "member": {"this": {}},
                
                # Metadata relationships (this is the wild part!)
                "has_name": {"this": {}},
                "has_email": {"this": {}}, 
                "has_profile_pic": {"this": {}},
                "created_at": {"this": {}},
                "updated_at": {"this": {}}
            }
        },
        {
            "type": "group", 
            "relations": {
                "member": {"this": {}},
                "admin": {"this": {}},
                
                # Group metadata
                "has_name": {"this": {}},
                "has_description": {"this": {}},
                "created_at": {"this": {}}
            }
        },
        {
            "type": "doc",
            "relations": {
                "owner": {"this": {}},
                "viewer": {"union": {"child": [{"this": {}}, {"computedUserset": {"relation": "owner"}}]}},
                
                # Document metadata
                "has_title": {"this": {}},
                "has_content": {"this": {}},
                "has_file_type": {"this": {}},
                "created_at": {"this": {}}
            }
        },
        {
            "type": "string_value",  # For storing actual string values
            "relations": {}
        },
        {
            "type": "timestamp_value",  # For storing timestamps
            "relations": {}
        }
    ]
}

# HOW DATA STORAGE WORKS
# =====================

class FullOpenFGADAL:
    """All data stored as OpenFGA relationships"""
    
    @staticmethod
    async def create_user(user_id: str, name: str, email: str):
        """Create a user by writing metadata relationships"""
        service = await get_openfga_service()
        
        # User metadata stored as relationships!
        await service.write_tuple(f"string_value:{name}", "is_name_of", f"user:{user_id}")
        await service.write_tuple(f"string_value:{email}", "is_email_of", f"user:{user_id}")
        await service.write_tuple(f"timestamp_value:{datetime.now().isoformat()}", "is_created_at_of", f"user:{user_id}")
        
        print(f"Created user {user_id} with metadata stored in OpenFGA!")
    
    @staticmethod 
    async def get_user(user_id: str) -> dict:
        """Get user by reading metadata relationships"""
        service = await get_openfga_service()
        
        # Read all relationships where something points to this user
        all_tuples = await service.read_tuples(object_ref=f"user:{user_id}")
        
        user_data = {"id": user_id}
        
        for tuple_data in all_tuples:
            if tuple_data["relation"] == "is_name_of":
                user_data["name"] = tuple_data["user"].replace("string_value:", "")
            elif tuple_data["relation"] == "is_email_of":
                user_data["email"] = tuple_data["user"].replace("string_value:", "")
            elif tuple_data["relation"] == "is_created_at_of":
                user_data["created_at"] = tuple_data["user"].replace("timestamp_value:", "")
        
        return user_data
    
    @staticmethod
    async def create_document(doc_id: str, title: str, content: str, owner_id: str):
        """Create document with metadata and ownership"""
        service = await get_openfga_service()
        
        # Document metadata
        await service.write_tuple(f"string_value:{title}", "is_title_of", f"doc:{doc_id}")
        await service.write_tuple(f"string_value:{content}", "is_content_of", f"doc:{doc_id}")
        await service.write_tuple(f"timestamp_value:{datetime.now().isoformat()}", "is_created_at_of", f"doc:{doc_id}")
        
        # Ownership relationship
        await service.write_tuple(f"user:{owner_id}", "owner", f"doc:{doc_id}")
        
        print(f"Created document {doc_id} owned by {owner_id}")
    
    @staticmethod
    async def get_user_documents(user_id: str) -> list:
        """Get all documents a user owns (combining metadata + permissions)"""
        service = await get_openfga_service()
        
        # Find all docs this user owns
        ownership_tuples = await service.read_tuples(
            user=f"user:{user_id}", 
            relation="owner"
        )
        
        documents = []
        for tuple_data in ownership_tuples:
            if tuple_data["object"].startswith("doc:"):
                doc_id = tuple_data["object"]
                
                # Get document metadata
                doc_tuples = await service.read_tuples(object_ref=doc_id)
                
                doc_data = {"id": doc_id}
                for meta_tuple in doc_tuples:
                    if meta_tuple["relation"] == "is_title_of":
                        doc_data["title"] = meta_tuple["user"].replace("string_value:", "")
                    elif meta_tuple["relation"] == "is_content_of":
                        doc_data["content"] = meta_tuple["user"].replace("string_value:", "")
                
                documents.append(doc_data)
        
        return documents

# CRAZY QUERY EXAMPLES
# ===================

async def find_users_by_email_domain(domain: str):
    """Find all users with emails ending in domain (e.g., '@company.com')"""
    service = await get_openfga_service()
    
    # This is where it gets interesting - you'd need to read ALL email relationships
    # and filter them (not as efficient as SQL LIKE queries)
    all_email_tuples = await service.read_tuples(relation="is_email_of")
    
    matching_users = []
    for tuple_data in all_email_tuples:
        email = tuple_data["user"].replace("string_value:", "")
        if email.endswith(domain):
            user_id = tuple_data["object"].replace("user:", "")
            matching_users.append(user_id)
    
    return matching_users

async def get_documents_created_after(date: str):
    """Find documents created after a certain date"""
    service = await get_openfga_service()
    
    # Again, need to read all timestamp relationships and filter
    all_timestamp_tuples = await service.read_tuples(relation="is_created_at_of")
    
    matching_docs = []
    for tuple_data in all_timestamp_tuples:
        if tuple_data["object"].startswith("doc:"):
            timestamp = tuple_data["user"].replace("timestamp_value:", "")
            if timestamp > date:  # String comparison works for ISO timestamps
                matching_docs.append(tuple_data["object"])
    
    return matching_docs

# THE MIND-BLOWING PART: UNIFIED QUERIES
# ======================================

async def find_documents_by_owners_in_group(group_id: str):
    """Find all documents owned by users who are members of a specific group"""
    service = await get_openfga_service()
    
    # Step 1: Find all users in the group
    group_members = await service.read_tuples(
        relation="member",
        object_ref=f"group:{group_id}"
    )
    
    all_docs = []
    
    # Step 2: For each member, find their owned documents
    for member_tuple in group_members:
        user_id = member_tuple["user"]
        
        # Step 3: Find docs owned by this user
        owned_docs = await service.read_tuples(
            user=user_id,
            relation="owner"
        )
        
        for doc_tuple in owned_docs:
            if doc_tuple["object"].startswith("doc:"):
                all_docs.append(doc_tuple["object"])
    
    return all_docs

# PROS AND CONS OF FULL OPENFGA
# =============================

"""
🤯 MIND-BLOWING PROS:
- Everything is unified - data and permissions in one system
- Incredibly powerful relationship queries
- Single source of truth
- Natural graph-like queries
- Authorization and data access in one place

😅 PRACTICAL CONS:
- Performance: Reading metadata requires multiple OpenFGA calls
- Complexity: Simple CRUD becomes relationship management
- Querying: No SQL-like filtering, sorting, pagination
- Tooling: No database admin tools, backup/restore complexity
- Learning curve: Very different mental model
- Scalability: OpenFGA optimized for auth, not general data storage

🤔 VERDICT:
Theoretically possible and actually quite elegant for some use cases,
but probably overkill for most applications. The hybrid approach gives
you the best of both worlds without the complexity.

However, for systems that are naturally relationship-heavy (social networks,
knowledge graphs, complex authorization systems), this could be brilliant!
"""

# EXAMPLE USAGE
# =============

async def demo_full_openfga():
    """Demo of how everything would work in full OpenFGA mode"""
    
    print("🤯 Full OpenFGA Demo")
    print("=" * 30)
    
    dal = FullOpenFGADAL()
    
    # Create users with metadata
    await dal.create_user("alice", "Alice Smith", "alice@company.com")
    await dal.create_user("bob", "Bob Jones", "bob@company.com")
    
    # Create documents
    await dal.create_document("doc1", "Project Plan", "This is the content...", "alice")
    await dal.create_document("doc2", "Meeting Notes", "Meeting summary...", "bob")
    
    # Query users
    alice = await dal.get_user("alice")
    print(f"User: {alice}")
    
    # Query documents by user
    alice_docs = await dal.get_user_documents("alice")
    print(f"Alice's documents: {alice_docs}")
    
    print("🎉 Everything stored in OpenFGA!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_full_openfga())
"""
