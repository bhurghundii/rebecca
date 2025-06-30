#!/usr/bin/env python3
"""
Test script to verify OpenFGA-UI synchronization
"""
import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.openfga.service import get_openfga_service

async def test_sync():
    """Test that OpenFGA service properly syncs with config"""
    print("🔄 Testing OpenFGA-UI synchronization...")
    
    try:
        # Initialize the service
        service = await get_openfga_service()
        
        print(f"Store ID: {service.store_id}")
        print(f"Model ID: {service.model_id}")
        
        # Test reading current config
        from src.openfga.config import OPENFGA_STORE_ID, OPENFGA_MODEL_ID
        print(f"Config Store ID: {OPENFGA_STORE_ID}")
        print(f"Config Model ID: {OPENFGA_MODEL_ID}")
        
        # Check if they match
        if service.store_id == OPENFGA_STORE_ID and service.model_id == OPENFGA_MODEL_ID:
            print("✅ Service and config are in sync!")
        else:
            print("⚠️  Service and config are NOT in sync")
            print("This should be fixed automatically...")
        
        # Test health check
        is_healthy = await service.health_check()
        print(f"Health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        
        # Test permission check with sample data
        print("\n🔍 Testing permission checks...")
        
        # First, let's read some tuples to see what we have
        tuples = await service.read_tuples()
        print(f"Found {len(tuples)} tuples in OpenFGA:")
        for i, tuple_data in enumerate(tuples[:3]):  # Show first 3
            print(f"  {i+1}. {tuple_data['user']} -> {tuple_data['relation']} -> {tuple_data['object']}")
        
        if tuples:
            # Test a permission check with the first tuple
            first_tuple = tuples[0]
            result = await service.check_permission(
                first_tuple['user'], 
                first_tuple['relation'], 
                first_tuple['object']
            )
            print(f"Permission check result: {'✅ Allowed' if result else '❌ Denied'}")
        
        await service.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_sync())
