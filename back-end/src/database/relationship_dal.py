"""
Data Access Layer for Relationships - Pure OpenFGA
"""
from typing import List, Optional, Dict, Any
import uuid
import asyncio
import sys
import os
from datetime import datetime

def get_openfga_service():
    """Get an OpenFGA service instance with robust import handling"""
    try:
        # Try absolute import first
        from src.openfga.service import get_openfga_service
        return get_openfga_service()
    except ImportError:
        try:
            # Try relative import
            from ..openfga.service import get_openfga_service
            return get_openfga_service()
        except ImportError:
            # Fallback to dynamic import
            import sys
            import os
            
            # Get the project root (back-end directory)
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # Add src to path
            src_path = os.path.join(project_root, 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            try:
                from openfga.service import get_openfga_service
                return get_openfga_service()
            except ImportError as e:
                print(f"❌ Failed to import OpenFGA service: {e}")
                # Return a dummy service that does nothing
                return None

def _get_openfga_service_class():
    """Get OpenFGA service class with robust import handling"""
    try:
        # Try absolute import first
        from src.openfga.service import OpenFGAService
        return OpenFGAService
    except ImportError:
        try:
            # Try relative import
            from ..openfga.service import OpenFGAService
            return OpenFGAService
        except ImportError:
            # Fallback to dynamic import
            import sys
            import os
            
            # Get the project root (back-end directory)
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(current_dir))
            
            # Add src to path
            src_path = os.path.join(project_root, 'src')
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            try:
                from openfga.service import OpenFGAService
                return OpenFGAService
            except ImportError as e:
                print(f"❌ Failed to import OpenFGA service: {e}")
                return None

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class RelationshipDAL:
    @staticmethod
    def get_all(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                relation_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all relationships from OpenFGA"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(RelationshipDAL._async_get_all_openfga(user_filter, resource_filter, relation_filter))
                return result[:limit] if limit > 0 else result  # Simple client-side limiting
            finally:
                loop.close()
        except Exception as e:
            print(f"⚠️  OpenFGA read failed: {e}")
            return []
    
    @staticmethod
    def get_by_id(relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship by ID from OpenFGA (ID format: user:relation:object)"""
        try:
            # Parse the relationship ID by finding the relation in the middle
            known_relations = ['owner', 'editor', 'viewer', 'member']
            
            user_part = None
            relation_part = None
            object_part = None
            
            # Try to find the relation in the ID
            for rel in known_relations:
                rel_pattern = f":{rel}:"
                if rel_pattern in relationship_id:
                    parts = relationship_id.split(rel_pattern, 1)
                    if len(parts) == 2:
                        user_part = parts[0]
                        relation_part = rel
                        object_part = parts[1]
                        break
            
            if not (user_part and relation_part and object_part):
                return None
            
            # Check if this specific relationship exists in OpenFGA
            if RelationshipDAL.check_relationship(user_part, relation_part, object_part):
                return {
                    'id': relationship_id,
                    'user': user_part,
                    'relation': relation_part,
                    'object': object_part,
                    'created_at': 'N/A',
                    'updated_at': 'N/A'
                }
            return None
        except Exception as e:
            print(f"⚠️  Failed to get relationship by ID: {e}")
            return None
    
    @staticmethod
    def create(user: str, relation: str, object_ref: str) -> Dict[str, Any]:
        """Create a new relationship in OpenFGA only"""
        relationship_id = f"{user}:{relation}:{object_ref}"
        timestamp = get_timestamp()
        
        relationship_data = {
            'id': relationship_id,
            'user': user,
            'relation': relation,
            'object': object_ref,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Write to OpenFGA only (no more SQLite storage for relationships)
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(RelationshipDAL._async_create_openfga(user, relation, object_ref))
                print(f"✅ Created relationship in OpenFGA: {user} {relation} {object_ref}")
            finally:
                loop.close()
        except Exception as e:
            print(f"❌ OpenFGA write failed: {e}")
            raise Exception(f"Failed to create relationship: {e}")
        
        return relationship_data
    
    @staticmethod
    async def _async_create_openfga(user: str, relation: str, object_ref: str):
        """Async helper to create relationship in OpenFGA"""
        service_class = _get_openfga_service_class()
        if service_class is None:
            print("❌ OpenFGA service class not available")
            return
        
        service = service_class()
        await service.initialize()
        
        try:
            await service.write_tuple(user, relation, object_ref)
        finally:
            await service.close()
    
    @staticmethod
    def update(relationship_id: str, user: Optional[str] = None, relation: Optional[str] = None,
               object_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update relationship in OpenFGA (delete old, create new)"""
        try:
            # Parse the current relationship ID by finding the relation in the middle
            # Expected format: user_part:relation:object_part
            # Known relations: owner, editor, viewer, member
            known_relations = ['owner', 'editor', 'viewer', 'member']
            
            current_user = None
            current_relation = None
            current_object = None
            
            # Try to find the relation in the ID
            for rel in known_relations:
                rel_pattern = f":{rel}:"
                if rel_pattern in relationship_id:
                    parts = relationship_id.split(rel_pattern, 1)
                    if len(parts) == 2:
                        current_user = parts[0]
                        current_relation = rel
                        current_object = parts[1]
                        break
            
            if not (current_user and current_relation and current_object):
                print(f"❌ Could not parse relationship ID: {relationship_id}")
                return None
            
            print(f"🔍 Parsed relationship: {current_user} {current_relation} {current_object}")
            
            # Use provided values or keep current ones
            new_user = user if user is not None else current_user
            new_relation = relation if relation is not None else current_relation
            new_object_ref = object_ref if object_ref is not None else current_object
            
            print(f"🔄 Updating: {current_user} {current_relation} {current_object} -> {new_user} {new_relation} {new_object_ref}")
            
            # Delete the old relationship
            if not RelationshipDAL.delete(relationship_id):
                print(f"❌ Failed to delete old relationship: {relationship_id}")
                return None
            
            # Create the new relationship
            result = RelationshipDAL.create(new_user, new_relation, new_object_ref)
            print(f"✅ Created new relationship: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Failed to update relationship: {e}")
            return None
    
    @staticmethod
    def delete(relationship_id: str) -> bool:
        """Delete relationship from OpenFGA only (ID format: user:relation:object)"""
        try:
            # Parse the relationship ID by finding the relation in the middle
            known_relations = ['owner', 'editor', 'viewer', 'member']
            
            user_part = None
            relation_part = None
            object_part = None
            
            # Try to find the relation in the ID
            for rel in known_relations:
                rel_pattern = f":{rel}:"
                if rel_pattern in relationship_id:
                    parts = relationship_id.split(rel_pattern, 1)
                    if len(parts) == 2:
                        user_part = parts[0]
                        relation_part = rel
                        object_part = parts[1]
                        break
            
            if not (user_part and relation_part and object_part):
                print(f"❌ Could not parse relationship ID for deletion: {relationship_id}")
                return False
            
            print(f"🗑️  Deleting relationship: {user_part} {relation_part} {object_part}")
            
            # Delete from OpenFGA
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(RelationshipDAL._async_delete_openfga(user_part, relation_part, object_part))
                print(f"✅ Deleted relationship from OpenFGA: {user_part} {relation_part} {object_part}")
                return True
            finally:
                loop.close()
        except Exception as e:
            print(f"❌ OpenFGA delete failed: {e}")
            return False
    
    @staticmethod
    async def _async_delete_openfga(user: str, relation: str, object_ref: str):
        """Async helper to delete relationship from OpenFGA"""
        service_class = _get_openfga_service_class()
        if service_class is None:
            print("❌ OpenFGA service class not available")
            return
        
        service = service_class()
        await service.initialize()
        
        try:
            await service.delete_tuple(user, relation, object_ref)
        finally:
            await service.close()
    
    @staticmethod
    def check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Check if a specific relationship exists using OpenFGA"""
        try:
            # Create a new event loop for this operation
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(RelationshipDAL._async_check_relationship(user, relation, object_ref))
                return result
            finally:
                loop.close()
        except Exception as e:
            print(f"❌ OpenFGA check failed: {e}")
            return False
    
    @staticmethod
    async def _async_check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Async version of check_relationship using OpenFGA"""
        service_class = _get_openfga_service_class()
        if service_class is None:
            print("❌ OpenFGA service class not available")
            return False
        
        service = service_class()
        await service.initialize()
        
        try:
            result = await service.check_permission(user, relation, object_ref)
            return result
        finally:
            await service.close()
    
    @staticmethod
    def get_relationships_by_user(user: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific user from OpenFGA"""
        return RelationshipDAL.get_all(user_filter=user)
    
    @staticmethod
    def get_relationships_by_object(object_ref: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific object from OpenFGA"""
        return RelationshipDAL.get_all(resource_filter=object_ref)
    
    @staticmethod
    def relationship_exists(user: str, relation: str, object_ref: str) -> bool:
        """Check if a relationship already exists (for duplicate prevention)"""
        return RelationshipDAL.check_relationship(user, relation, object_ref)
    
    @staticmethod
    def delete_by_criteria(user: Optional[str] = None, relation: Optional[str] = None,
                          object_ref: Optional[str] = None) -> int:
        """Delete relationships matching criteria from OpenFGA. Returns number of deleted relationships."""
        if not any([user, relation, object_ref]):
            return 0  # Don't delete everything by accident
        
        try:
            # First, get all relationships matching the criteria
            relationships = RelationshipDAL.get_all(user_filter=user, resource_filter=object_ref, relation_filter=relation)
            
            # Delete each relationship
            deleted_count = 0
            for rel in relationships:
                if RelationshipDAL.delete(rel['id']):
                    deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"❌ Failed to delete relationships by criteria: {e}")
            return 0
    
    @staticmethod
    async def _async_get_all_openfga(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                                   relation_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Async helper to get all relationships from OpenFGA"""
        service_class = _get_openfga_service_class()
        if service_class is None:
            print("❌ OpenFGA service class not available")
            return []
        
        service = service_class()
        await service.initialize()
        
        try:
            # Read tuples with filters
            tuples = await service.read_tuples(
                user=user_filter, 
                relation=relation_filter, 
                object_ref=resource_filter
            )
            
            # Convert to the expected format with IDs and timestamps
            relationships = []
            for tuple_data in tuples:
                relationships.append({
                    'id': f"{tuple_data['user']}:{tuple_data['relation']}:{tuple_data['object']}",  # Generate consistent ID
                    'user': tuple_data['user'],
                    'relation': tuple_data['relation'], 
                    'object': tuple_data['object'],
                    'created_at': 'N/A',  # OpenFGA doesn't store timestamps
                    'updated_at': 'N/A'
                })
            
            return relationships
        finally:
            await service.close()
