#!/usr/bin/env python3
"""
Test creating a new OpenFGA model and check if group permissions work
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from openfga.service import OpenFGAService

async def test_new_model():
    """Create a new model and test group inheritance"""
    print("🧪 Creating new OpenFGA model for group inheritance test...")
    
    service = OpenFGAService()
    await service.initialize()
    
    # Force a new model creation
    service.model_id = None
    await service._ensure_model()
    
    # Test data
    test_user = "user:testuser456"
    test_group = "group:testgroup456"
    test_resource = "folder:testfolder456"
    
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
        
        print(f"\n4️⃣ Cleaning up test tuples...")
        await service.delete_tuple(test_user, "member", test_group)
        await service.delete_tuple(test_group, "viewer", test_resource)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(test_new_model())
