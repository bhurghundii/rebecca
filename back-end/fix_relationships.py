#!/usr/bin/env python3
"""
Fix relationships to use proper OpenFGA format
"""
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.relationship_dal import RelationshipDAL
from database.user_dal import UserDAL
from database.resource_dal import ResourceDAL
from database.user_group_dal import UserGroupDAL

def fix_relationships():
    """Fix relationships to use proper OpenFGA format"""
    print("🔧 Fixing relationship formats...")
    
    # Get all relationships
    relationships = RelationshipDAL.get_all(limit=1000)
    
    fixed_count = 0
    
    for rel in relationships:
        needs_update = False
        new_user = rel['user']
        new_object = rel['object']
        
        # Fix user format
        if not rel['user'].startswith(('user:', 'group:')):
            # Check if it's a user ID
            user = UserDAL.get_by_id(rel['user'])
            if user:
                new_user = f"user:{rel['user']}"
                needs_update = True
            else:
                # Check if it's a group ID
                group = UserGroupDAL.get_by_id(rel['user'])
                if group:
                    new_user = f"group:{rel['user']}"
                    needs_update = True
        
        # Fix object format
        if ':' not in rel['object']:
            # Check if it's a resource ID
            resource = ResourceDAL.get_by_id(rel['object'])
            if resource:
                new_object = f"{resource['type']}:{rel['object']}"
                needs_update = True
            else:
                # Check if it's a group ID
                group = UserGroupDAL.get_by_id(rel['object'])
                if group:
                    new_object = f"group:{rel['object']}"
                    needs_update = True
        
        # Update the relationship if needed
        if needs_update:
            try:
                RelationshipDAL.update(
                    rel['id'],
                    user=new_user,
                    object_ref=new_object
                )
                print(f"   ✅ Fixed: {rel['user']} -> {new_user}, {rel['object']} -> {new_object}")
                fixed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to fix relationship {rel['id']}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} relationships")
    
    # Show current relationships
    print("\n📋 Current relationships:")
    relationships = RelationshipDAL.get_all(limit=1000)
    for rel in relationships:
        print(f"   {rel['user']} -> {rel['relation']} -> {rel['object']}")

if __name__ == '__main__':
    fix_relationships()
