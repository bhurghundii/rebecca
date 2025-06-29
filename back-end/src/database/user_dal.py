"""
Data Access Layer for Users
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

class UserDAL:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all users"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM users ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def create(name: str, email: str) -> Dict[str, Any]:
        """Create a new user"""
        user_id = generate_id()
        timestamp = get_timestamp()
        
        user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO users (id, name, email, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, email, timestamp, timestamp))
            conn.commit()
        
        return user_data
    
    @staticmethod
    def update(user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update user"""
        with get_db() as conn:
            # Check if user exists
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            existing_user = cursor.fetchone()
            if not existing_user:
                return None
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append('name = ?')
                params.append(name)
            
            if email is not None:
                update_fields.append('email = ?')
                params.append(email)
            
            if update_fields:
                timestamp = get_timestamp()
                update_fields.append('updated_at = ?')
                params.append(timestamp)
                params.append(user_id)
                
                conn.execute(f'''
                    UPDATE users SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
                conn.commit()
            
            # Return updated user
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            return dict(cursor.fetchone())
    
    @staticmethod
    def delete(user_id: str) -> bool:
        """Delete user"""
        with get_db() as conn:
            cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
