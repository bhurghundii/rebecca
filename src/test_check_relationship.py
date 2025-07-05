"""
OpenFGA-powered RelationshipDAL - check_relationship() implementation

This demonstrates how to transform the existing RelationshipDAL.check_relationship() 
method to use OpenFGA while maintaining the exact same interface.
"""
import asyncio
import sys
import os

# Add the openfga directory to path
sys.path.insert(0, os.path.dirname(__file__))

from service import get_openfga_service

class OpenFGARelationshipDAL:
    """Demonstration of OpenFGA-powered RelationshipDAL methods"""
    
    @staticmethod
    def _run_async(coro):
        """Helper to run async functions from sync methods"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    @staticmethod
    def _format_user(user: str) -> str:
        """Ensure user is in correct OpenFGA format"""
        if not user.startswith('user:'):
            return f"user:{user}"
        return user
    
    @staticmethod
    def _format_object(object_ref: str) -> str:
        """Ensure object is in correct OpenFGA format
        
        Maps your existing object references to OpenFGA object types:
        - documents/resources -> doc:id
        - folders -> folder:id
        - groups -> group:id
        """
        if ':' in object_ref:
            return object_ref  # Already formatted
            
        # Add logic to detect and format your object types
        # Adjust these rules based on your actual data patterns
        if 'doc' in object_ref.lower() or 'resource' in object_ref.lower():
            return f"doc:{object_ref}"
        elif 'folder' in object_ref.lower():
            return f"folder:{object_ref}"
        elif 'group' in object_ref.lower():
            return f"group:{object_ref}"
        else:
            # Default to doc type - adjust based on your most common object type
            return f"doc:{object_ref}"
    
    @staticmethod
    async def _check_relationship_async(user: str, relation: str, object_ref: str) -> bool:
        """Async version of check_relationship using OpenFGA"""
        try:
            service = await get_openfga_service()
            
            formatted_user = OpenFGARelationshipDAL._format_user(user)
            formatted_object = OpenFGARelationshipDAL._format_object(object_ref)
            
            # Use OpenFGA's check API
            result = await service.check_permission(formatted_user, relation, formatted_object)
            
            print(f"OpenFGA Check: {formatted_user} {relation} {formatted_object} = {result}")
            return result
            
        except Exception as e:
            print(f"OpenFGA check failed: {e}")
            # In production, you might want to fall back to the original SQLite method
            # or handle this error differently based on your requirements
            return False
    
    @staticmethod
    def check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Check if a specific relationship exists - OpenFGA powered
        
        This is a drop-in replacement for the original check_relationship method.
        Same interface, but powered by OpenFGA instead of SQLite.
        """
        return OpenFGARelationshipDAL._run_async(
            OpenFGARelationshipDAL._check_relationship_async(user, relation, object_ref)
        )


def test_check_relationship():
    """Test the OpenFGA-powered check_relationship method"""
    print("🧪 Testing OpenFGA-powered check_relationship()")
    print("=" * 50)
    
    dal = OpenFGARelationshipDAL()
    
    # Test 1: Check a relationship that doesn't exist
    print("\n1. Testing non-existent relationship:")
    result = dal.check_relationship("alice", "owner", "mydoc")
    print(f"   alice owner mydoc = {result}")
    
    # Test 2: Create a relationship first, then check it
    print("\n2. Creating a test relationship...")
    
    # We'll use the service directly to create a relationship for testing
    async def create_test_relationship():
        service = await get_openfga_service()
        success = await service.write_tuple("user:alice", "owner", "doc:mydoc")
        print(f"   Created relationship: {success}")
        return success
    
    # Create the relationship
    created = OpenFGARelationshipDAL._run_async(create_test_relationship())
    
    if created:
        # Test 3: Check the relationship we just created
        print("\n3. Testing existing relationship:")
        result = dal.check_relationship("alice", "owner", "mydoc")
        print(f"   alice owner mydoc = {result}")
        
        # Test 4: Test different relations on same object
        print("\n4. Testing different relation (should be false):")
        result = dal.check_relationship("alice", "viewer", "mydoc")
        print(f"   alice viewer mydoc = {result}")
        
        # Clean up
        print("\n5. Cleaning up test data...")
        async def cleanup():
            service = await get_openfga_service()
            await service.delete_tuple("user:alice", "owner", "doc:mydoc")
            await service.close()
            print("   Cleanup complete")
        
        OpenFGARelationshipDAL._run_async(cleanup())
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_check_relationship()
