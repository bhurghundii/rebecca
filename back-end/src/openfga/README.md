# OpenFGA Integration for Rebecca

This folder contains the OpenFGA (Fine-Grained Authorization) integration for the Rebecca permission system.

## 📁 Structure

```
openfga/
├── README.md           # This file
├── requirements.txt    # OpenFGA-specific dependencies  
├── config.py          # OpenFGA configuration
├── service.py         # OpenFGA service wrapper
├── test_integration.py # Integration tests
├── relationship_dal.py # OpenFGA-powered RelationshipDAL
└── migration/         # Data migration scripts
    └── migrate_to_openfga.py
```

## 🎯 Current Status

### ✅ Phase 1: Basic Integration (COMPLETE)
- [x] OpenFGA SDK installed and working
- [x] Connection to OpenFGA Docker instance (localhost:8080)
- [x] Service wrapper with HTTP API calls
- [x] Basic CRUD operations (write/read/check/delete tuples)
- [x] Integration tests passing

### 🚧 Phase 2: RelationshipDAL Integration (NEXT)
- [ ] Transform RelationshipDAL to use OpenFGA backend
- [ ] Maintain existing API compatibility
- [ ] Add hybrid mode (OpenFGA + local DB for audit)

### 📋 Phase 3: Data Migration (FUTURE)
- [ ] Script to migrate existing relationships to OpenFGA
- [ ] Validation and rollback capabilities

## 🔧 OpenFGA Setup

**Store ID:** `01JYYK7BG878R7NVQRECYFT5C4`
**Authorization Model ID:** `01JYYK7D1CY0KMVPJV6HVYZMEH`

**Object Types in Model:**
- `user` - Individual users
- `group` - User groups with members  
- `folder` - Folders with hierarchical permissions
- `doc` - Documents with owner/viewer permissions

## 🚀 Quick Test

```bash
cd openfga
python test_integration.py
```

## 📝 Next Steps for Tomorrow

1. **Transform RelationshipDAL**: Update the existing DAL to use OpenFGA backend
2. **API Integration**: Connect Flask endpoints to OpenFGA
3. **Data Migration**: Move existing SQLite data to OpenFGA
4. **Testing**: Comprehensive testing of the integrated system

## 💡 Notes

- Using direct HTTP API calls instead of SDK (more reliable)
- Maintaining backward compatibility with existing Rebecca API
- OpenFGA running in Docker container on port 8080
- Authorization model supports complex hierarchical permissions
