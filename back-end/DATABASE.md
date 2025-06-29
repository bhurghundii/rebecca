# Rebecca API Database Layer

This document describes the database layer for the Rebecca API, which has been migrated from in-memory storage to SQLite.

## Database Structure

The Rebecca API now uses SQLite as its database backend, with the following structure:

### Tables

1. **users** - User management
   - `id`: Primary key (UUID)
   - `name`: User's full name
   - `email`: User's email (unique)
   - `created_at`: Timestamp when user was created
   - `updated_at`: Timestamp when user was last updated

2. **resource_groups** - Resource grouping
   - `id`: Primary key (UUID)
   - `name`: Group name
   - `description`: Group description
   - `created_at`: Timestamp when group was created
   - `updated_at`: Timestamp when group was last updated

3. **resources** - Resources within groups
   - `id`: Primary key (UUID)
   - `type`: Resource type (document, project, organization, folder, file)
   - `name`: Resource name
   - `metadata`: JSON metadata
   - `resource_group_id`: Foreign key to resource_groups
   - `created_at`: Timestamp when resource was created
   - `updated_at`: Timestamp when resource was last updated

4. **user_groups** - User grouping
   - `id`: Primary key (UUID)
   - `name`: Group name
   - `description`: Group description
   - `created_at`: Timestamp when group was created
   - `updated_at`: Timestamp when group was last updated

5. **user_group_members** - Many-to-many relationship between users and user groups
   - `id`: Primary key (UUID)
   - `user_group_id`: Foreign key to user_groups
   - `user_id`: Foreign key to users
   - `created_at`: Timestamp when relationship was created

6. **relationships** - OpenFGA-style relationships
   - `id`: Primary key (UUID)
   - `user`: User reference (e.g., "user:123")
   - `relation`: Relationship type (e.g., "owner", "editor", "viewer", "member")
   - `object`: Object reference (e.g., "document:456", "group:789")
   - `created_at`: Timestamp when relationship was created
   - `updated_at`: Timestamp when relationship was last updated

## Data Access Layer (DAL)

The database layer is organized into Data Access Layer (DAL) classes:

- **UserDAL** (`database/user_dal.py`) - User operations
- **ResourceDAL** (`database/resource_dal.py`) - Resource operations
- **ResourceGroupDAL** (`database/resource_group_dal.py`) - Resource group operations
- **UserGroupDAL** (`database/user_group_dal.py`) - User group operations
- **RelationshipDAL** (`database/relationship_dal.py`) - Relationship operations

## Database Configuration

- **Database file**: `rebecca.db` (SQLite)
- **Configuration**: `database/config.py`
- **Initialization**: Automatic on first run
- **Sample data**: Automatically loaded on first run

## Key Features

1. **Foreign Key Constraints**: Enabled for data integrity
2. **Unique Constraints**: Email addresses must be unique
3. **Indexes**: Created for better query performance
4. **Transaction Support**: Each operation is properly committed
5. **Error Handling**: Graceful handling of constraint violations
6. **Automatic Relationships**: User group membership creates OpenFGA relationships

## Usage

### Initialize Database
```python
from database.config import init_database
init_database()
```

### Reset Database and Load Sample Data
```python
from database.sample_data import reset_and_load_sample_data
stats = reset_and_load_sample_data()
```

### Using DAL Classes
```python
from database.user_dal import UserDAL

# Create a user
user = UserDAL.create("John Doe", "john@example.com")

# Get all users
users = UserDAL.get_all()

# Update a user
updated_user = UserDAL.update(user_id, name="Jane Doe")
```

## Migration from In-Memory Storage

The API has been successfully migrated from dictionary-based in-memory storage to SQLite:

### Before (In-Memory)
```python
users = {}
resources = {}
user_groups = {}
resource_groups = {}
relationships = {}
```

### After (SQLite)
```python
from database.user_dal import UserDAL
from database.resource_dal import ResourceDAL
# ... other DAL imports

users = UserDAL.get_all()
resources = ResourceDAL.get_all()
```

## Benefits of the Migration

1. **Data Persistence**: Data survives server restarts
2. **ACID Compliance**: Atomic, Consistent, Isolated, Durable operations
3. **Concurrent Access**: Multiple requests can safely access the database
4. **Data Integrity**: Foreign key constraints and unique constraints
5. **Query Performance**: Indexes for faster lookups
6. **Scalability**: Can handle larger datasets efficiently
7. **Backup/Restore**: Simple file-based backup and restore
8. **Schema Evolution**: Structured approach to database changes

## Database File Location

The SQLite database file is created at:
- Development: `back-end/rebecca.db`
- Path can be configured in `database/config.py`

## Setup Script

Use the `setup_database.py` script for database management:

```bash
cd back-end
python setup_database.py
```

This provides options to:
1. Initialize database (create tables)
2. Reset database and load sample data
3. Load sample data (preserve existing)
4. Exit

## Notes

- The database is automatically initialized when the app starts
- Sample data is only loaded once to prevent duplicates
- All timestamps are stored in ISO format
- UUIDs are used for all primary keys
- The database uses SQLite's row factory for dict-like access to results
