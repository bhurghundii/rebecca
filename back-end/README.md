# Rebecca API - Flask Backend

A mock Flask API implementation for the Rebecca user management and OpenFGA authorization system.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd back-end
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python src/app.py
```

The server will start on `http://localhost:8000` with sample data already loaded.

### 3. Test the API

**Quick Test:**
```bash
python tests/test_api.py
```

**Full Test Suite (Pytest):**
```bash
python tests/run_tests.py
```

**Or run pytest directly:**
```bash
pytest tests/ -v
```

## 📋 Available Endpoints

### Health Check
- `GET /health` - Check API health and OpenFGA connection

### Users
- `GET /users` - Get all users
- `POST /users` - Create a new user
- `GET /users/{userId}` - Get user by ID
- `PUT /users/{userId}` - Update user
- `DELETE /users/{userId}` - Delete user

### Resources
- `GET /resources` - Get all resources
- `POST /resources` - Create a new resource
- `GET /resources/{resourceId}` - Get resource by ID
- `PUT /resources/{resourceId}` - Update resource
- `DELETE /resources/{resourceId}` - Delete resource

### User Groups
- `GET /user-groups` - Get all user groups
- `POST /user-groups` - Create a new user group
- `GET /user-groups/{groupId}` - Get user group by ID
- `PUT /user-groups/{groupId}` - Update user group
- `DELETE /user-groups/{groupId}` - Delete user group

### Resource Groups
- `GET /resource-groups` - Get all resource groups
- `POST /resource-groups` - Create a new resource group
- `GET /resource-groups/{groupId}` - Get resource group by ID
- `PUT /resource-groups/{groupId}` - Update resource group
- `DELETE /resource-groups/{groupId}` - Delete resource group

### Relationships
- `GET /relationships` - Get all relationships (with optional filters)
- `POST /relationships` - Create a new relationship
- `GET /relationships/{relationshipId}` - Get relationship by ID
- `PUT /relationships/{relationshipId}` - Update relationship
- `DELETE /relationships/{relationshipId}` - Delete relationship
- `POST /relationships/check` - Check if user has permission

## 📝 Sample Data

The server starts with sample data:
- 3 users (Alice, Bob, Charlie)
- 3 resources (Project Plan, Rebecca API, Shared Documents)
- 3 relationships showing different permission levels

## 🧪 Testing Examples

### Create a User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Create a Resource
```bash
curl -X POST http://localhost:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "document", "resource_name": "My Document", "metadata": {"category": "work"}}'
```

### Check Permission
```bash
curl -X POST http://localhost:8000/relationships/check \
  -H "Content-Type: application/json" \
  -d '{"user": "user:123", "relation": "viewer", "object": "document:456"}'
```

## 📊 Data Storage

This is a mock implementation using in-memory storage. Data is reset when the server restarts. Perfect for development and testing!

## 🔄 CORS Enabled

The API has CORS enabled for development, so you can call it from any frontend application.

---

Ready to build something awesome! 🎉
