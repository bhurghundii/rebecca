"""
Data Access Layer for Resources
"""
import json
from typing import List, Optional, Dict, Any
from .config import get_db
import uuid
from datetime import datetime

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class ResourceDAL:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all resources"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT r.*, rg.name as resource_group_name
                FROM resources r
                LEFT JOIN resource_groups rg ON r.resource_group_id = rg.id
                ORDER BY r.created_at DESC
            ''')
            resources = []
            for row in cursor.fetchall():
                resource = dict(row)
                # Parse metadata JSON
                try:
                    resource['metadata'] = json.loads(resource['metadata']) if resource['metadata'] else {}
                except json.JSONDecodeError:
                    resource['metadata'] = {}
                resources.append(resource)
            return resources
    
    @staticmethod
    def get_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource by ID"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT r.*, rg.name as resource_group_name
                FROM resources r
                LEFT JOIN resource_groups rg ON r.resource_group_id = rg.id
                WHERE r.id = ?
            ''', (resource_id,))
            row = cursor.fetchone()
            if row:
                resource = dict(row)
                try:
                    resource['metadata'] = json.loads(resource['metadata']) if resource['metadata'] else {}
                except json.JSONDecodeError:
                    resource['metadata'] = {}
                return resource
            return None
    
    @staticmethod
    def create(resource_type: str, name: str, resource_group_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new resource"""
        resource_id = generate_id()
        timestamp = get_timestamp()
        metadata_json = json.dumps(metadata or {})
        
        resource_data = {
            'id': resource_id,
            'type': resource_type,
            'name': name,
            'metadata': metadata or {},
            'resource_group_id': resource_group_id,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO resources (id, type, name, metadata, resource_group_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (resource_id, resource_type, name, metadata_json, resource_group_id, timestamp, timestamp))
            conn.commit()
        
        return resource_data
    
    @staticmethod
    def update(resource_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update resource"""
        with get_db() as conn:
            # Check if resource exists
            cursor = conn.execute('SELECT * FROM resources WHERE id = ?', (resource_id,))
            existing_resource = cursor.fetchone()
            if not existing_resource:
                return None
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if 'resource_type' in kwargs and kwargs['resource_type'] is not None:
                update_fields.append('type = ?')
                params.append(kwargs['resource_type'])
            
            if 'name' in kwargs and kwargs['name'] is not None:
                update_fields.append('name = ?')
                params.append(kwargs['name'])
            
            if 'metadata' in kwargs and kwargs['metadata'] is not None:
                update_fields.append('metadata = ?')
                params.append(json.dumps(kwargs['metadata']))
            
            if 'resource_group_id' in kwargs and kwargs['resource_group_id'] is not None:
                update_fields.append('resource_group_id = ?')
                params.append(kwargs['resource_group_id'])
            
            if update_fields:
                timestamp = get_timestamp()
                update_fields.append('updated_at = ?')
                params.append(timestamp)
                params.append(resource_id)
                
                conn.execute(f'''
                    UPDATE resources SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
                conn.commit()
            
            # Return updated resource
            return ResourceDAL.get_by_id(resource_id)
    
    @staticmethod
    def delete(resource_id: str) -> bool:
        """Delete resource"""
        with get_db() as conn:
            cursor = conn.execute('DELETE FROM resources WHERE id = ?', (resource_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_by_resource_group(resource_group_id: str) -> List[Dict[str, Any]]:
        """Get all resources in a resource group"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT r.*, rg.name as resource_group_name
                FROM resources r
                LEFT JOIN resource_groups rg ON r.resource_group_id = rg.id
                WHERE r.resource_group_id = ?
                ORDER BY r.created_at DESC
            ''', (resource_group_id,))
            resources = []
            for row in cursor.fetchall():
                resource = dict(row)
                try:
                    resource['metadata'] = json.loads(resource['metadata']) if resource['metadata'] else {}
                except json.JSONDecodeError:
                    resource['metadata'] = {}
                resources.append(resource)
            return resources
