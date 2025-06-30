#!/usr/bin/env python3
"""
Test script to verify OpenFGA connection and setup
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.openfga_service import get_openfga_service

async def test_openfga_connection():
    """Test basic OpenFGA connectivity and setup"""
    print("🚀 Testing OpenFGA connection...")
    
    try:
        # Get the OpenFGA service
        service = await get_openfga_service()
        print(f"✅ OpenFGA service initialized")
        print(f"   Store ID: {service.store_id}")
        print(f"   Model ID: {service.model_id}")
        
        # Test health check
        is_healthy = await service.health_check()
        if is_healthy:
            print("✅ OpenFGA health check passed")
        else:
            print("❌ OpenFGA health check failed")
            await service.close()
            return False
        
        # Test writing a simple tuple using correct types from the model
        print("\n📝 Testing tuple operations...")
        success = await service.write_tuple("user:alice", "owner", "doc:mydoc")
        if success:
            print("✅ Successfully wrote test tuple")
        else:
            print("❌ Failed to write test tuple")
            await service.close()
            return False
        
        # Test checking the permission
        has_permission = await service.check_permission("user:alice", "owner", "doc:mydoc")
        if has_permission:
            print("✅ Permission check passed - alice is owner of mydoc")
        else:
            print("❌ Permission check failed")
            await service.close()
            return False
        
        # Test reading tuples
        tuples = await service.read_tuples()
        print(f"✅ Read {len(tuples)} tuples from OpenFGA")
        for tuple_data in tuples:
            print(f"   {tuple_data['user']} {tuple_data['relation']} {tuple_data['object']}")
        
        # Clean up test tuple
        await service.delete_tuple("user:alice", "owner", "doc:mydoc")
        print("✅ Cleaned up test tuple")
        
        print("\n🎉 All OpenFGA tests passed!")
        await service.close()
        return True
        
    except Exception as e:
        print(f"❌ OpenFGA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""    
    print("Rebecca OpenFGA Integration Test")
    print("=" * 40)
    
    # Check if OpenFGA is running
    print("📡 Make sure OpenFGA is running on http://localhost:8080")
    print("   (docker-compose up openfga)\n")
    
    # Run the async test
    success = asyncio.run(test_openfga_connection())
    
    if success:
        print("\n✅ OpenFGA integration is ready!")
        print("Next steps:")
        print("1. Update RelationshipDAL to use OpenFGA")
        print("2. Test with existing API endpoints")
        print("3. Migrate existing data")
    else:
        print("\n❌ OpenFGA integration failed!")
        print("Check that OpenFGA is running and accessible")

if __name__ == "__main__":
    main()
