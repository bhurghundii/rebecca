"""
OpenFGA-Powered Relationship DAL
Replaces the SQLite-based RelationshipDAL with OpenFGA backend
"""
import asyncio
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from .openfga_service import OpenFGAService
from .openfga_config import OPENFGA_API_URL, OPENFGA_STORE_ID, OPENFGA_MODEL_ID

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class OpenFGARelationshipDAL:
    """
    OpenFGA-powered RelationshipDAL
    Maintains the same interface as the original but uses OpenFGA for storage
    """
    
    @staticmethod
    def _run_async(coro):
        """Helper to run async functions in sync context"""
        loop = None
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we need to handle this differently
                # For now, we'll create a new event loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(coro)
    
    @staticmethod
    async def _get_service() -> OpenFGAService:
        """Get initialized OpenFGA service"""
        service = OpenFGAService()
        await service.initialize()
        return service
    
    @staticmethod
    def get_all(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                relation_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all relationships with optional filtering"""
        
        async def _get_all():
            service = await OpenFGARelationshipDAL._get_service()
            
            # Read all tuples (OpenFGA doesn't have built-in filtering, so we do it client-side)
            all_tuples = await service.read_tuples()
            
            # Convert OpenFGA tuples to our format
            relationships = []
            for tuple_data in all_tuples:
                relationship = {
                    'id': f"{tuple_data['user']}#{tuple_data['relation']}#{tuple_data['object']}",
                    'user': tuple_data['user'],
                    'relation': tuple_data['relation'],  
                    'object': tuple_data['object'],
                    'created_at': get_timestamp(),  # OpenFGA doesn't store timestamps
                    'updated_at': get_timestamp()
                }
                
                # Apply filters
                if user_filter and user_filter.lower() not in relationship['user'].lower():
                    continue
                if resource_filter and resource_filter.lower() not in relationship['object'].lower():
                    continue
                if relation_filter and relationship['relation'] != relation_filter:
                    continue
                    
                relationships.append(relationship)
            
            # Apply pagination
            start = offset
            end = offset + limit
            return relationships[start:end]
        
        return OpenFGARelationshipDAL._run_async(_get_all())
    
    @staticmethod
    def get_by_id(relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship by ID (ID format: user#relation#object)"""
        
        async def _get_by_id():
            try:
                # Parse the composite ID
                parts = relationship_id.split('#')
                if len(parts) != 3:
                    return None
                user, relation, object_ref = parts
                
                service = await OpenFGARelationshipDAL._get_service()
                
                # Check if this specific tuple exists
                exists = await service.check_relationship(user, relation, object_ref)
                if not exists:
                    return None
                
                return {
                    'id': relationship_id,
                    'user': user,
                    'relation': relation,
                    'object': object_ref,
                    'created_at': get_timestamp(),
                    'updated_at': get_timestamp()
                }
            except:
                return None
        
        return OpenFGARelationshipDAL._run_async(_get_by_id())
    
    @staticmethod
    def create(user: str, relation: str, object_ref: str) -> Dict[str, Any]:
        """Create a new relationship"""
        
        async def _create():
            service = await OpenFGARelationshipDAL._get_service()
            
            # Write the tuple to OpenFGA
            await service.write_tuple(user, relation, object_ref)
            
            # Return the relationship data
            relationship_id = f"{user}#{relation}#{object_ref}"
            timestamp = get_timestamp()
            
            return {
                'id': relationship_id,
                'user': user,
                'relation': relation,
                'object': object_ref,
                'created_at': timestamp,
                'updated_at': timestamp
            }
        
        return OpenFGARelationshipDAL._run_async(_create())
    
    @staticmethod
    def update(relationship_id: str, user: Optional[str] = None, relation: Optional[str] = None,
               object_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update relationship (delete old, create new)"""
        
        async def _update():
            try:
                # Parse the original relationship
                parts = relationship_id.split('#')
                if len(parts) != 3:
                    return None
                old_user, old_relation, old_object = parts
                
                service = await OpenFGARelationshipDAL._get_service()
                
                # Check if original exists
                exists = await service.check_relationship(old_user, old_relation, old_object)
                if not exists:
                    return None
                
                # Delete the old relationship
                await service.delete_tuple(old_user, old_relation, old_object)
                
                # Create new relationship with updated values
                new_user = user if user is not None else old_user
                new_relation = relation if relation is not None else old_relation
                new_object = object_ref if object_ref is not None else old_object
                
                await service.write_tuple(new_user, new_relation, new_object)
                
                # Return updated relationship
                new_id = f"{new_user}#{new_relation}#{new_object}"
                return {
                    'id': new_id,
                    'user': new_user,
                    'relation': new_relation,
                    'object': new_object,
                    'created_at': get_timestamp(),  # We don't track original creation time
                    'updated_at': get_timestamp()
                }
            except Exception as e:
                print(f"Error updating relationship: {e}")
                return None
        
        return OpenFGARelationshipDAL._run_async(_update())
    
    @staticmethod
    def delete(relationship_id: str) -> bool:
        """Delete relationship"""
        
        async def _delete():
            try:
                # Parse the relationship ID
                parts = relationship_id.split('#')
                if len(parts) != 3:
                    return False
                user, relation, object_ref = parts
                
                service = await OpenFGARelationshipDAL._get_service()
                
                # Delete the tuple
                await service.delete_tuple(user, relation, object_ref)
                return True
            except Exception as e:
                print(f"Error deleting relationship: {e}")
                return False
        
        return OpenFGARelationshipDAL._run_async(_delete())
    
    @staticmethod
    def check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Check if a specific relationship exists (with computed relationships!)"""
        
        async def _check():
            service = await OpenFGARelationshipDAL._get_service()
            return await service.check_relationship(user, relation, object_ref)
        
        return OpenFGARelationshipDAL._run_async(_check())
    
    @staticmethod
    def get_relationships_by_user(user: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific user"""
        
        async def _get_by_user():
            service = await OpenFGARelationshipDAL._get_service()
            
            # Read tuples where this user is the subject
            tuples = await service.read_tuples(user=user)
            
            relationships = []
            for tuple_data in tuples:
                relationship = {
                    'id': f"{tuple_data['user']}#{tuple_data['relation']}#{tuple_data['object']}",
                    'user': tuple_data['user'],
                    'relation': tuple_data['relation'],
                    'object': tuple_data['object'],
                    'created_at': get_timestamp(),
                    'updated_at': get_timestamp()
                }
                relationships.append(relationship)
            
            return relationships
        
        return OpenFGARelationshipDAL._run_async(_get_by_user())
    
    @staticmethod
    def get_relationships_by_object(object_ref: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific object"""
        
        async def _get_by_object():
            service = await OpenFGARelationshipDAL._get_service()
            
            # Read tuples where this object is the target
            tuples = await service.read_tuples(object_ref=object_ref)
            
            relationships = []
            for tuple_data in tuples:
                relationship = {
                    'id': f"{tuple_data['user']}#{tuple_data['relation']}#{tuple_data['object']}",
                    'user': tuple_data['user'],
                    'relation': tuple_data['relation'],
                    'object': tuple_data['object'],
                    'created_at': get_timestamp(),
                    'updated_at': get_timestamp()
                }
                relationships.append(relationship)
            
            return relationships
        
        return OpenFGARelationshipDAL._run_async(_get_by_object())
    
    @staticmethod
    def relationship_exists(user: str, relation: str, object_ref: str) -> bool:
        """Check if a relationship already exists (for duplicate prevention)"""
        return OpenFGARelationshipDAL.check_relationship(user, relation, object_ref)
    
    @staticmethod
    def delete_by_criteria(user: Optional[str] = None, relation: Optional[str] = None,
                          object_ref: Optional[str] = None) -> int:
        """Delete relationships matching criteria. Returns number of deleted relationships."""
        
        async def _delete_by_criteria():
            if not any([user, relation, object_ref]):
                return 0  # Don't delete everything by accident
            
            service = await OpenFGARelationshipDAL._get_service()
            
            # Read all tuples matching criteria
            tuples = await service.read_tuples(user=user, relation=relation, object_ref=object_ref)
            
            # Delete each matching tuple
            deleted_count = 0
            for tuple_data in tuples:
                try:
                    await service.delete_tuple(
                        tuple_data['user'], 
                        tuple_data['relation'], 
                        tuple_data['object']
                    )
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting tuple: {e}")
            
            return deleted_count
        
        return OpenFGARelationshipDAL._run_async(_delete_by_criteria())


# Create an alias for easy switching
RelationshipDAL = OpenFGARelationshipDAL
