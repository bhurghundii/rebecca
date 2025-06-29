# Permission Checker Examples

The Permission Checker now supports checking permissions for both users and user groups on resources.

## Current Test Relationships

### Individual User Permissions
- **Alice Johnson** (`user:928377db-e663-4ef8-9339-9f115e84c684`)
  - `owner` of document "Project Plan"
  - `member` of group "Admin Team"

- **Bob Smith** (`user:345e43a7-995c-46be-92dc-194409766043`)
  - `editor` of document "Project Plan"

- **Charlie Brown** (`user:34f0fd36-48e0-47d3-8fc4-154da1fa86a0`)
  - `viewer` of project "Rebecca API"

### User Group Permissions
- **Admin Team** (`group:cf2ae26a-d298-4ada-8605-3f13f936351b`)
  - `owner` of project "Rebecca API"

- **Project Team** (`group:450285a3-316e-4c5c-ba10-3fe17ca33da5`)
  - `viewer` of document "Project Plan"

## Test Cases to Try

### ✅ Expected to Return `allowed: true`
1. **User Alice** has `owner` relation to **document:Project Plan**
2. **User Bob** has `editor` relation to **document:Project Plan**
3. **User Charlie** has `viewer` relation to **project:Rebecca API**
4. **Admin Team group** has `owner` relation to **project:Rebecca API**
5. **Project Team group** has `viewer` relation to **document:Project Plan**
6. **User Alice** has `member` relation to **group:Admin Team**

### ❌ Expected to Return `allowed: false`
1. **User Alice** has `editor` relation to **project:Rebecca API** (she's owner of document, not project)
2. **Project Team group** has `owner` relation to **document:Project Plan** (they're viewers, not owners)
3. **User Bob** has `member` relation to **group:Admin Team** (only Alice is a member)
4. **Admin Team group** has `editor` relation to **project:Rebecca API** (they're owners, not editors)

## UI Usage

1. **Select Subject**: Choose either a user from the "👤 Users" section or a user group from the "👥 User Groups" section
2. **Select Relation**: Choose from viewer, reader, editor, owner, or member
3. **Select Object**: Choose either a resource from "📄 Resources" or a user group from "👥 User Groups"
4. **Check Permission**: Click the button to see if the relationship exists

## OpenFGA Format

The Permission Checker uses proper OpenFGA format:
- **Subjects**: `user:ID` or `group:ID`
- **Relations**: `viewer`, `reader`, `editor`, `owner`, `member`
- **Objects**: `document:ID`, `project:ID`, `folder:ID`, `file:ID`, `organization:ID`, `group:ID`

This allows for flexible permission checking including:
- User permissions on resources
- User group permissions on resources  
- User membership in groups
- Future: Nested groups and inherited permissions
