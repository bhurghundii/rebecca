#!/usr/bin/env python3
"""
Test OpenFGA group inheritance directly
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from openfga.service import get_openfga_service

async def test_direct_inheritance():
    """Test group inheritance by creating simple test tuples"""
    print("🧪 Testing OpenFGA group inheritance directly...")
    
    service = await get_openfga_service()
    
    # Test data
    test_user = "user:testuser123"
    test_group = "group:testgroup123"
    test_resource = "folder:testfolder123"
    
    try:
        print(f"\n1️⃣ Creating membership: {test_user} member {test_group}")
        await service.write_tuple(test_user, "member", test_group)
        
        print(f"2️⃣ Creating group permission: {test_group} viewer {test_resource}")
        await service.write_tuple(test_group, "viewer", test_resource)
        
        print(f"\n3️⃣ Testing if user can view resource through group...")
        can_view = await service.check_permission(test_user, "viewer", test_resource)
        print(f"   Result: {can_view}")
        
        if can_view:
            print("✅ Group inheritance is working!")
        else:
            print("❌ Group inheritance is NOT working")
            print("\n4️⃣ Debugging: Check individual components...")
            
            # Check if membership exists
            is_member = await service.check_permission(test_user, "member", test_group)
            print(f"   User is member of group: {is_member}")
            
            # Check if group has permission  
            group_has_permission = await service.check_permission(test_group, "viewer", test_resource)
            print(f"   Group has viewer permission: {group_has_permission}")
        
        print(f"\n5️⃣ Cleaning up test tuples...")
        await service.delete_tuple(test_user, "member", test_group)
        await service.delete_tuple(test_group, "viewer", test_resource)
        print("   ✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(test_direct_inheritance())
