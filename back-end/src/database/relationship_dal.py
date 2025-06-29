"""
Data Access Layer for Relationships
"""
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

class RelationshipDAL:
    @staticmethod
    def get_all(user_filter: Optional[str] = None, resource_filter: Optional[str] = None,
                relation_filter: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all relationships with optional filtering"""
        query = 'SELECT * FROM relationships WHERE 1=1'
        params = []
        
        if user_filter:
            query += ' AND user LIKE ?'
            params.append(f'%{user_filter}%')
        
        if resource_filter:
            query += ' AND object LIKE ?'
            params.append(f'%{resource_filter}%')
        
        if relation_filter:
            query += ' AND relation = ?'
            params.append(relation_filter)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        with get_db() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_id(relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship by ID"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM relationships WHERE id = ?', (relationship_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create(user: str, relation: str, object_ref: str) -> Dict[str, Any]:
        """Create a new relationship"""
        relationship_id = generate_id()
        timestamp = get_timestamp()
        
        relationship_data = {
            'id': relationship_id,
            'user': user,
            'relation': relation,
            'object': object_ref,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO relationships (id, user, relation, object, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (relationship_id, user, relation, object_ref, timestamp, timestamp))
            conn.commit()
        
        return relationship_data
    
    @staticmethod
    def update(relationship_id: str, user: Optional[str] = None, relation: Optional[str] = None,
               object_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update relationship"""
        with get_db() as conn:
            # Check if relationship exists
            cursor = conn.execute('SELECT * FROM relationships WHERE id = ?', (relationship_id,))
            existing_relationship = cursor.fetchone()
            if not existing_relationship:
                return None
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if user is not None:
                update_fields.append('user = ?')
                params.append(user)
            
            if relation is not None:
                update_fields.append('relation = ?')
                params.append(relation)
            
            if object_ref is not None:
                update_fields.append('object = ?')
                params.append(object_ref)
            
            if update_fields:
                timestamp = get_timestamp()
                update_fields.append('updated_at = ?')
                params.append(timestamp)
                params.append(relationship_id)
                
                conn.execute(f'''
                    UPDATE relationships SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
                conn.commit()
            
            # Return updated relationship
            cursor = conn.execute('SELECT * FROM relationships WHERE id = ?', (relationship_id,))
            return dict(cursor.fetchone())
    
    @staticmethod
    def delete(relationship_id: str) -> bool:
        """Delete relationship"""
        with get_db() as conn:
            cursor = conn.execute('DELETE FROM relationships WHERE id = ?', (relationship_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def check_relationship(user: str, relation: str, object_ref: str) -> bool:
        """Check if a specific relationship exists"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT 1 FROM relationships
                WHERE user = ? AND relation = ? AND object = ?
                LIMIT 1
            ''', (user, relation, object_ref))
            return cursor.fetchone() is not None
    
    @staticmethod
    def get_relationships_by_user(user: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific user"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM relationships WHERE user = ?
                ORDER BY created_at DESC
            ''', (user,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_relationships_by_object(object_ref: str) -> List[Dict[str, Any]]:
        """Get all relationships for a specific object"""
        with get_db() as conn:
            cursor = conn.execute('''
                SELECT * FROM relationships WHERE object = ?
                ORDER BY created_at DESC
            ''', (object_ref,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def relationship_exists(user: str, relation: str, object_ref: str) -> bool:
        """Check if a relationship already exists (for duplicate prevention)"""
        return RelationshipDAL.check_relationship(user, relation, object_ref)
    
    @staticmethod
    def delete_by_criteria(user: Optional[str] = None, relation: Optional[str] = None,
                          object_ref: Optional[str] = None) -> int:
        """Delete relationships matching criteria. Returns number of deleted relationships."""
        if not any([user, relation, object_ref]):
            return 0  # Don't delete everything by accident
        
        query = 'DELETE FROM relationships WHERE 1=1'
        params = []
        
        if user:
            query += ' AND user = ?'
            params.append(user)
        
        if relation:
            query += ' AND relation = ?'
            params.append(relation)
        
        if object_ref:
            query += ' AND object = ?'
            params.append(object_ref)
        
        with get_db() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
