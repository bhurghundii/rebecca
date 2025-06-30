#!/usr/bin/env python3
"""
Check what OpenFGA tuples exist for group memberships
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from openfga.service import get_openfga_service
from database.user_dal import UserDAL
from database.user_group_dal import UserGroupDAL

async def check_memberships():
    """Check what group membership tuples exist in OpenFGA"""
    print("🔍 Checking OpenFGA group memberships...")
    
    # Get users and groups
    users = UserDAL.get_all()
    groups = UserGroupDAL.get_all()
    
    print(f"\n📊 Found {len(users)} users, {len(groups)} groups")
    
    service = await get_openfga_service()
    
    # Check for all membership tuples
    print("\n🔍 Reading all 'member' relationships...")
    tuples = await service.read_tuples(relation="member")
    
    if tuples:
        print(f"📋 Found {len(tuples)} membership tuples:")
        for tuple_data in tuples:
            print(f"   {tuple_data['user']} member {tuple_data['object']}")
    else:
        print("❌ No membership tuples found!")
    
    # Let's also check all tuples
    print("\n🔍 Reading all tuples...")
    all_tuples = await service.read_tuples()
    print(f"📋 Found {len(all_tuples)} total tuples:")
    for tuple_data in all_tuples:
        print(f"   {tuple_data['user']} {tuple_data['relation']} {tuple_data['object']}")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(check_memberships())
