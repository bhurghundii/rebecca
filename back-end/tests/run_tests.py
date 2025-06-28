#!/usr/bin/env python3
"""
Test runner script for Rebecca API
"""
import subprocess
import sys
import requests
import time

def check_server():
    """Check if the Flask server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def main():
    """Run the tests"""
    print("🧪 Rebecca API Test Runner")
    print("=" * 40)
    
    # Check if server is running
    if not check_server():
        print("❌ Flask server is not running!")
        print("💡 Please start the server first: python app.py")
        sys.exit(1)
    
    print("✅ Server is running")
    print("🚀 Running pytest tests...")
    print()
    
    # Run pytest with various options
    try:
        # Basic test run
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/",                # Test directory
            "-v",                    # verbose
            "--tb=short",           # short traceback
            "--color=yes",          # colored output
            "--durations=10"        # show slowest 10 tests
        ], check=True)
        
        print("\n🎉 All tests passed!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with return code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1

if __name__ == "__main__":
    sys.exit(main())
