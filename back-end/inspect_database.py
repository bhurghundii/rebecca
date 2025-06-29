#!/usr/bin/env python3
"""
Database inspection tool for Rebecca API
"""
import os
import sys
import sqlite3

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.config import DATABASE_PATH

def inspect_database():
    """Inspect the Rebecca database"""
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database file not found. Run the server first to create it.")
        return
    
    print("🔍 Rebecca Database Inspection")
    print("=" * 50)
    print(f"📁 Database file: {DATABASE_PATH}")
    print(f"📏 File size: {os.path.getsize(DATABASE_PATH)} bytes")
    print()
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("📋 Tables:")
        for table in tables:
            table_name = table['name']
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"   - {table_name}: {count} records")
        
        print()
        
        # Show sample data from each table
        for table in tables:
            table_name = table['name']
            print(f"📊 Sample data from '{table_name}':")
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            
            if rows:
                # Get column names
                columns = [description[0] for description in cursor.description]
                print(f"   Columns: {', '.join(columns)}")
                
                for i, row in enumerate(rows, 1):
                    row_dict = dict(row)
                    # Truncate long values
                    for key, value in row_dict.items():
                        if isinstance(value, str) and len(value) > 50:
                            row_dict[key] = value[:47] + "..."
                    print(f"   Row {i}: {row_dict}")
            else:
                print("   (No data)")
            print()

def show_schema():
    """Show the database schema"""
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database file not found. Run the server first to create it.")
        return
    
    print("🏗️  Rebecca Database Schema")
    print("=" * 50)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # Get table schemas
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table_name, create_sql in tables:
            print(f"📋 Table: {table_name}")
            print(f"   {create_sql}")
            print()
        
        # Get indexes
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY name")
        indexes = cursor.fetchall()
        
        if indexes:
            print("🔍 Indexes:")
            for index_name, create_sql in indexes:
                print(f"   {index_name}: {create_sql}")
            print()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--schema':
        show_schema()
    else:
        inspect_database()

if __name__ == '__main__':
    main()
