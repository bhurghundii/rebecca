"""
OpenFGA-powered RelationshipDAL - Drop-in replacement for the existing RelationshipDAL

This maintains the same interface as the original RelationshipDAL but uses OpenFGA 
as the backend instead of SQLite, providing fine-grained authorization capabilities.
"""
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio

from service import get_openfga_service
from config import OBJECT_TYPES, RELATIONS

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class RelationshipDAL:
    """OpenFGA-powered RelationshipDAL with the same interface as the original"""
    
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
        - documents -> doc:id
        - resources -> doc:id  
        - folders -> folder:id
        - groups -> group:id
        """
        if ':' in object_ref:
            return object_ref  # Already formatted
            
        # Add logic to detect and format your object types
        if object_ref.startswith('doc') or object_ref.startswith('resource'):
            return f"doc:{object_ref}"
        elif object_ref.startswith('folder'):
            return f"folder:{object_ref}"
        elif object_ref.startswith('group'):
            return f"group:{object_ref}"
        else:
            # Default to doc type
            return f"doc:{object_ref}"
    
    @staticmethod
    async def _get_all_async(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                            relation_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Async version of get_all"""
        service = await get_openfga_service()
        
        # Format filters for OpenFGA
        formatted_user = RelationshipDAL._format_user(user_filter) if user_filter else None
        formatted_object = RelationshipDAL._format_object(resource_filter) if resource_filter else None
        
        # Read tuples from OpenFGA
        tuples = await service.read_tuples(
            user=formatted_user,
            relation=relation_filter,
            object_ref=formatted_object
        )
        
        # Convert OpenFGA tuples back to original format for compatibility
        relationships = []
        for i, tuple_data in enumerate(tuples[offset:offset+limit]):
            # Strip OpenFGA prefixes for backward compatibility
            user = tuple_data['user'].replace('user:', '')
            obj = tuple_data['object']
            for prefix in ['doc:', 'folder:', 'group:']:
                obj = obj.replace(prefix, '')
            
            relationships.append({
                'id': generate_id(),  # Generate ID for compatibility
                'user': user,
                'relation': tuple_data['relation'],
                'object': obj,
                'created_at': get_timestamp(),  # Placeholder timestamp
                'updated_at': get_timestamp()   # Placeholder timestamp
            })
        
        return relationships
    
    @staticmethod
    def get_all(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                relation_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all relationships with optional filtering - OpenFGA powered"""
        return RelationshipDAL._run_async(
            RelationshipDAL._get_all_async(user_filter, resource_filter, relation_filter, limit, offset)
        )
    
    @staticmethod
    async def _create_async(user: str, relation: str, object_ref: str) -> Dict[str, Any]:
        """Async version of create"""
        service = await get_openfga_service()
        
        formatted_user = RelationshipDAL._format_user(user)
        formatted_object = RelationshipDAL._format_object(object_ref)
        
        # Write tuple to OpenFGA
        success = await service.write_tuple(formatted_user, relation, formatted_object)
        
        if not success:
            raise Exception(f"Failed to create relationship in OpenFGA")
        
        # Return data in original format for compatibility
        relationship_data = {
            'id': generate_id(),
            'user': user,
            'relation': relation,
            'object': object_ref,
            'created_at': get_timestamp(),
            'updated_at': get_timestamp()
        }
        
        return relationship_data
    
    @staticmethod
    def create(user: str, relation: str, object_ref: str) -> Dict[str, Any]:
        """Create a new relationship - OpenFGA powered"""
        return RelationshipDAL._run_async(
            RelationshipDAL._create_async(user, relation, object_ref)
        )
    
    @staticmethod
    async def _check_relationship_async(user: str, relation: str, object_ref: str) -> bool:
        """Async version of check_relationship"""
        service = await get_openfga_service()
        
        formatted_user = RelationshipDAL._format_user(user)
        formatted_object = RelationshipDAL._format_object(object_ref)
        
        return await service.check_permission(formatted_user, relation, formatted_object)
    
    @staticmethod
    def check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Check if a specific relationship exists - OpenFGA powered"""
        return RelationshipDAL._run_async(
            RelationshipDAL._check_relationship_async(user, relation, object_ref)
        )
    
    @staticmethod
    def relationship_exists(user: str, relation: str, object_ref: str) -> bool:
        """Check if a relationship already exists (for duplicate prevention)"""
        return RelationshipDAL.check_relationship(user, relation, object_ref)
    
    # TODO: Implement the remaining methods:
    # - get_by_id() - might need to store metadata in local DB
    # - update() - delete old tuple, write new tuple
    # - delete() - delete tuple from OpenFGA
    # - get_relationships_by_user()
    # - get_relationships_by_object() 
    # - delete_by_criteria()
    
    @staticmethod
    def get_by_id(relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship by ID - NOT IMPLEMENTED YET
        
        Note: OpenFGA doesn't store relationship IDs, so this would need
        a hybrid approach with local metadata storage.
        """
        raise NotImplementedError("get_by_id not yet implemented for OpenFGA backend")
    
    @staticmethod
    def update(relationship_id: str, user: Optional[str] = None, relation: Optional[str] = None,
               object_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update relationship - NOT IMPLEMENTED YET"""
        raise NotImplementedError("update not yet implemented for OpenFGA backend")
    
    @staticmethod 
    def delete(relationship_id: str) -> bool:
        """Delete relationship - NOT IMPLEMENTED YET"""
        raise NotImplementedError("delete not yet implemented for OpenFGA backend")


# TODO for Phase 2:
# 1. Implement remaining methods (get_by_id, update, delete, etc.)
# 2. Add proper error handling and logging
# 3. Consider hybrid approach for metadata (timestamps, IDs) 
# 4. Add batch operations for better performance
# 5. Add connection pooling and retry logic
