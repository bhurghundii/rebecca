"""
Database configuration and connection management for Rebecca API
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'rebecca.db')

def get_db_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict-like access"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with all required tables"""
    with get_db() as conn:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create resource_groups table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS resource_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create resources table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                resource_group_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (resource_group_id) REFERENCES resource_groups (id) ON DELETE CASCADE
            )
        ''')
        
        # Create user_groups table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create user_group_members table (many-to-many relationship)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_group_members (
                id TEXT PRIMARY KEY,
                user_group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_group_id) REFERENCES user_groups (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_group_id, user_id)
            )
        ''')
        
        # Note: Relationships are now stored in OpenFGA, not SQLite
        # This improves performance and reduces complexity
        
        # Create indexes for better performance
        conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_resources_group ON resources(resource_group_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_group_members_user ON user_group_members(user_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_group_members_group ON user_group_members(user_group_id)')
        
        conn.commit()
        print("✅ Database initialized successfully (relationships stored in OpenFGA)")

def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("🗑️  Existing database removed")
    init_database()
