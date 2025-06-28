#!/usr/bin/env python3
"""
Simple startup script for Rebecca API
"""
import subprocess
import sys
import os

def main():
    """Start the Rebecca API server"""
    print("🚀 Starting Rebecca API Server...")
    print("=" * 40)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # Run the Flask app
        subprocess.run([sys.executable, "src/app.py"], check=True)
    except KeyboardInterrupt:
        print("\n⚠️  Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
