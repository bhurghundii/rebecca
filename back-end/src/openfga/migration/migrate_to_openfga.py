"""
Migration script to transfer existing relationships from SQLite to OpenFGA
"""
import asyncio
import sqlite3
import sys
import os
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from service import get_openfga_service

class OpenFGAMigration:
    """Handles migration from SQLite to OpenFGA"""
    
    def __init__(self, sqlite_db_path: str):
        self.sqlite_db_path = sqlite_db_path
        self.openfga_service = None
        
    async def initialize(self):
        """Initialize OpenFGA service"""
        self.openfga_service = await get_openfga_service()
        
    async def get_existing_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships from SQLite database"""
        relationships = []
        
        try:
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM relationships')
            
            for row in cursor.fetchall():
                relationships.append(dict(row))
                
            conn.close()
            print(f"Found {len(relationships)} existing relationships")
            
        except Exception as e:
            print(f"Failed to read from SQLite: {e}")
            
        return relationships
    
    def transform_relationship(self, relationship: Dict[str, Any]) -> Dict[str, str]:
        """Transform SQLite relationship to OpenFGA tuple format"""
        # Map your current data to OpenFGA format
        # This is where you'd implement the mapping logic
        
        user = relationship['user']
        relation = relationship['relation'] 
        obj = relationship['object']
        
        # Example transformations (adjust based on your data):
        # - If user is just "alice" -> "user:alice"
        # - If object is "doc123" -> "doc:doc123"
        
        if not user.startswith('user:'):
            user = f"user:{user}"
            
        # Map your objects to the correct OpenFGA types
        if obj.startswith('doc') or obj.startswith('document'):
            if not obj.startswith('doc:'):
                obj = f"doc:{obj}"
        elif obj.startswith('folder'):
            if not obj.startswith('folder:'):
                obj = f"folder:{obj}"
        
        return {
            'user': user,
            'relation': relation,
            'object': obj
        }
    
    async def migrate_relationships(self, dry_run: bool = True) -> bool:
        """Migrate all relationships to OpenFGA"""
        try:
            relationships = await self.get_existing_relationships()
            
            if not relationships:
                print("No relationships to migrate")
                return True
            
            success_count = 0
            error_count = 0
            
            for relationship in relationships:
                try:
                    tuple_data = self.transform_relationship(relationship)
                    
                    if dry_run:
                        print(f"Would migrate: {tuple_data['user']} {tuple_data['relation']} {tuple_data['object']}")
                    else:
                        success = await self.openfga_service.write_tuple(
                            tuple_data['user'],
                            tuple_data['relation'], 
                            tuple_data['object']
                        )
                        
                        if success:
                            success_count += 1
                            print(f"✅ Migrated: {tuple_data['user']} {tuple_data['relation']} {tuple_data['object']}")
                        else:
                            error_count += 1
                            print(f"❌ Failed: {tuple_data['user']} {tuple_data['relation']} {tuple_data['object']}")
                            
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error processing relationship {relationship}: {e}")
            
            if not dry_run:
                print(f"\nMigration complete: {success_count} success, {error_count} errors")
            
            return error_count == 0
            
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    async def close(self):
        """Close connections"""
        if self.openfga_service:
            await self.openfga_service.close()

async def main():
    """Main migration function"""
    print("OpenFGA Migration Tool")
    print("=" * 30)
    
    # Path to your SQLite database
    sqlite_path = "../../back-end/rebecca.db"
    
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        return
    
    migration = OpenFGAMigration(sqlite_path)
    
    try:
        await migration.initialize()
        print("✅ OpenFGA connection established")
        
        # First run in dry-run mode
        print("\n🔍 DRY RUN - Preview migration:")
        await migration.migrate_relationships(dry_run=True)
        
        # Uncomment to run actual migration
        # print("\n🚀 Running actual migration...")
        # success = await migration.migrate_relationships(dry_run=False)
        # 
        # if success:
        #     print("✅ Migration completed successfully!")
        # else:
        #     print("❌ Migration completed with errors")
        
    finally:
        await migration.close()

if __name__ == "__main__":
    asyncio.run(main())
