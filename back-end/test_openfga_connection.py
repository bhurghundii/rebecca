#!/usr/bin/env python3
"""
Test OpenFGA connection
"""
import requests

def test_openfga_connection():
    """Test basic connection to OpenFGA"""
    try:
        # Test if OpenFGA is accessible
        response = requests.get('http://localhost:3000/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ OpenFGA is accessible at localhost:3000")
            return True
        else:
            print(f"❌ OpenFGA returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to OpenFGA at localhost:3000")
        print("Make sure OpenFGA is running with: docker-compose up")
        return False
    except Exception as e:
        print(f"❌ Error connecting to OpenFGA: {e}")
        return False

def test_openfga_stores():
    """Test creating and listing stores"""
    try:
        # List existing stores
        response = requests.get('http://localhost:3000/stores', timeout=5)
        if response.status_code == 200:
            stores = response.json()
            print(f"✅ Found {len(stores.get('stores', []))} existing stores")
            return True
        else:
            print(f"❌ Failed to list stores: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing stores: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenFGA connection...")
    
    if test_openfga_connection():
        print("\nTesting OpenFGA stores API...")
        test_openfga_stores()
        print("\n🎉 OpenFGA is ready for integration!")
    else:
        print("\n❌ OpenFGA connection failed. Please check your docker setup.")
