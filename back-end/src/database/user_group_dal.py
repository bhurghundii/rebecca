"""
Data Access Layer for User Groups
"""
import json
from typing import List, Optional, Dict, Any
from .config import get_db
from .user_dal import UserDAL
import uuid
from datetime import datetime

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

class UserGroupDAL:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all user groups with their members"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM user_groups ORDER BY created_at DESC')
            groups = []
            for row in cursor.fetchall():
                group = dict(row)
                # Get user IDs for this group
                members_cursor = conn.execute('''
                    SELECT user_id FROM user_group_members WHERE user_group_id = ?
                ''', (group['id'],))
                user_ids = [row[0] for row in members_cursor.fetchall()]
                group['user_ids'] = user_ids
                
                # Get user details
                users = []
                for user_id in user_ids:
                    user = UserDAL.get_by_id(user_id)
                    if user:
                        users.append(user)
                    else:
                        users.append({"id": user_id, "name": "Unknown", "email": "unknown@example.com"})
                
                group['users'] = users
                group['user_count'] = len(users)
                groups.append(group)
            
            return groups
    
    @staticmethod
    def get_by_id(group_id: str) -> Optional[Dict[str, Any]]:
        """Get user group by ID with members"""
        with get_db() as conn:
            cursor = conn.execute('SELECT * FROM user_groups WHERE id = ?', (group_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            group = dict(row)
            
            # Get user IDs for this group
            members_cursor = conn.execute('''
                SELECT user_id FROM user_group_members WHERE user_group_id = ?
            ''', (group_id,))
            user_ids = [row[0] for row in members_cursor.fetchall()]
            group['user_ids'] = user_ids
            
            # Get user details
            users = []
            for user_id in user_ids:
                user = UserDAL.get_by_id(user_id)
                if user:
                    users.append(user)
                else:
                    users.append({"id": user_id, "name": "Unknown", "email": "unknown@example.com"})
            
            group['users'] = users
            group['user_count'] = len(users)
            
            return group
    
    @staticmethod
    def create(name: str, user_ids: List[str], description: str = '') -> Dict[str, Any]:
        """Create a new user group"""
        group_id = generate_id()
        timestamp = get_timestamp()
        
        with get_db() as conn:
            # Create the group
            conn.execute('''
                INSERT INTO user_groups (id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (group_id, name, description, timestamp, timestamp))
            
            # Add members
            for user_id in user_ids:
                member_id = generate_id()
                conn.execute('''
                    INSERT INTO user_group_members (id, user_group_id, user_id, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (member_id, group_id, user_id, timestamp))
            
            conn.commit()
        
        return UserGroupDAL.get_by_id(group_id)
    
    @staticmethod
    def update(group_id: str, name: Optional[str] = None, description: Optional[str] = None, 
               user_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Update user group"""
        with get_db() as conn:
            # Check if group exists
            cursor = conn.execute('SELECT * FROM user_groups WHERE id = ?', (group_id,))
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
                    UPDATE user_groups SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', params)
            
            # Update members if provided
            if user_ids is not None:
                # Remove all existing members
                conn.execute('DELETE FROM user_group_members WHERE user_group_id = ?', (group_id,))
                
                # Add new members
                timestamp = get_timestamp()
                for user_id in user_ids:
                    member_id = generate_id()
                    conn.execute('''
                        INSERT INTO user_group_members (id, user_group_id, user_id, created_at)
                        VALUES (?, ?, ?, ?)
                    ''', (member_id, group_id, user_id, timestamp))
            
            conn.commit()
        
        return UserGroupDAL.get_by_id(group_id)
    
    @staticmethod
    def delete(group_id: str) -> bool:
        """Delete user group (members will be automatically deleted due to foreign key cascade)"""
        with get_db() as conn:
            cursor = conn.execute('DELETE FROM user_groups WHERE id = ?', (group_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def add_member(group_id: str, user_id: str) -> bool:
        """Add a user to a group"""
        with get_db() as conn:
            try:
                member_id = generate_id()
                timestamp = get_timestamp()
                conn.execute('''
                    INSERT INTO user_group_members (id, user_group_id, user_id, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (member_id, group_id, user_id, timestamp))
                conn.commit()
                return True
            except Exception:
                return False  # User already in group or doesn't exist
    
    @staticmethod
    def remove_member(group_id: str, user_id: str) -> bool:
        """Remove a user from a group"""
        with get_db() as conn:
            cursor = conn.execute('''
                DELETE FROM user_group_members 
                WHERE user_group_id = ? AND user_id = ?
            ''', (group_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
