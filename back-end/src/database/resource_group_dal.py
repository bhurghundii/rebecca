"""
Data Access Layer for Resource Groups
"""
import json
from typing import List, Optional, Dict, Any
from .config import get_db
from .resource_dal import ResourceDAL
import uuid
from datetime import datetime

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class ResourceGroupDAL:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all resource groups with their resources"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM resource_groups ORDER BY created_at DESC')
            groups = []
            for row in cursor.fetchall():
                group = dict(row)
                
                # Get resources for this group
                resources = ResourceGroupDAL._get_group_resources(group['id'])
                group['resource_ids'] = [r['id'] for r in resources]
                group['resources'] = resources
                group['resource_count'] = len(resources)
                groups.append(group)
            
            return groups
    
    @staticmethod
    def get_by_id(group_id: str) -> Optional[Dict[str, Any]]:
        """Get resource group by ID with resources"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM resource_groups WHERE id = ?', (group_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            group = dict(row)
            
            # Get resources for this group
            resources = ResourceGroupDAL._get_group_resources(group_id)
            group['resource_ids'] = [r['id'] for r in resources]
            group['resources'] = resources
            group['resource_count'] = len(resources)
            
            return group
    
    @staticmethod
    def _get_group_resources(group_id: str) -> List[Dict[str, Any]]:
        """Helper method to get resources for a group"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM resources WHERE resource_group_id = ?
                ORDER BY created_at DESC
            ''', (group_id,))
            resources = []
            for row in cursor.fetchall():
                resource = dict(row)
                try:
                    resource['metadata'] = json.loads(resource['metadata']) if resource['metadata'] else {}
                except json.JSONDecodeError:
                    resource['metadata'] = {}
                resources.append(resource)
            return resources
    
    @staticmethod
    def create(name: str, description: str = '', resource_ids: List[str] = None) -> Dict[str, Any]:
        """Create a new resource group"""
        group_id = generate_id()
        timestamp = get_timestamp()
        
        with get_db() as conn:
            # Create the group
            conn.execute('''
                INSERT INTO resource_groups (id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (group_id, name, description, timestamp, timestamp))
            
            # Update resources to belong to this group if resource_ids provided
            if resource_ids:
                for resource_id in resource_ids:
                    conn.execute('''
                        UPDATE resources SET resource_group_id = ?, updated_at = ?
                        WHERE id = ?
                    ''', (group_id, timestamp, resource_id))
            
            conn.commit()
        
        return ResourceGroupDAL.get_by_id(group_id)
    
    @staticmethod
    def update(group_id: str, name: Optional[str] = None, description: Optional[str] = None,
               resource_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Update resource group"""
        with get_db() as conn:
            # Check if group exists
            cursor = conn.execute('SELECT * FROM resource_groups WHERE id = ?', (group_id,))
            existing_group = cursor.fetchone()
            if not existing_group:
                return None
            
            # Update group details
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append('name = ?')
                params.append(name)
            
            if description is not None:
                update_fields.append('description = ?')
                params.append(description)
            
            if update_fields:
                timestamp = get_timestamp()
                update_fields.append('updated_at = ?')
                params.append(timestamp)
                params.append(group_id)
                
                conn.execute(f'''
                    UPDATE resource_groups SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
            
            # Update resources if provided
            if resource_ids is not None:
                timestamp = get_timestamp()
                
                # First, remove all resources from this group (set to null or move to default)
                # We'll need to handle this carefully since resource_group_id is NOT NULL
                # For now, we'll just update the specified resources to belong to this group
                
                # Remove current resources from this group by setting them to a default group
                # This is a simplification - in production you might want better handling
                current_resources = ResourceGroupDAL._get_group_resources(group_id)
                
                # Update specified resources to belong to this group
                for resource_id in resource_ids:
                    conn.execute('''
                        UPDATE resources SET resource_group_id = ?, updated_at = ?
                        WHERE id = ?
                    ''', (group_id, timestamp, resource_id))
            
            conn.commit()
        
        return ResourceGroupDAL.get_by_id(group_id)
    
    @staticmethod
    def delete(group_id: str) -> bool:
        """Delete resource group (resources will be cascade deleted)"""
        with get_db() as conn:
            cursor = conn.execute('DELETE FROM resource_groups WHERE id = ?', (group_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def add_resource(group_id: str, resource_id: str) -> bool:
        """Add a resource to a group"""
        with get_db() as conn:
            try:
                timestamp = get_timestamp()
                conn.execute('''
                    UPDATE resources SET resource_group_id = ?, updated_at = ?
                    WHERE id = ?
                ''', (group_id, timestamp, resource_id))
                conn.commit()
                return conn.total_changes > 0
            except Exception:
                return False
    
    @staticmethod
    def remove_resource(group_id: str, resource_id: str) -> bool:
        """Remove a resource from a group (this is tricky since resource_group_id is NOT NULL)"""
        # In a real implementation, you might want to move the resource to a default group
        # For now, we'll just return False as resources must belong to a group
        return False
