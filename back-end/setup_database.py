#!/usr/bin/env python3
"""
Database setup and test script for Rebecca API
"""
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.config import init_database, reset_database
from database.sample_data import load_sample_data, reset_and_load_sample_data

def main():
    print("🔧 Rebecca API Database Setup")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Initialize database (create tables)")
        print("2. Reset database and load sample data")
        print("3. Load sample data (preserve existing)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n🔧 Initializing database...")
            init_database()
            print("✅ Database initialized successfully!")
            
        elif choice == '2':
            print("\n🔄 Resetting database and loading sample data...")
            stats = reset_and_load_sample_data()
            print(f"✅ Database reset and sample data loaded!")
            print(f"📊 Loaded: {stats}")
            
        elif choice == '3':
            print("\n📦 Loading sample data...")
            stats = load_sample_data()
            print(f"✅ Sample data loaded!")
            print(f"📊 Loaded: {stats}")
            
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please select 1-4.")

if __name__ == '__main__':
    main()
