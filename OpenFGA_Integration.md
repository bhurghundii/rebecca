# OpenFGA Integration for User Groups

## Overview

The Rebecca API now automatically manages OpenFGA relationship tuples when users are added to or removed from user groups. This ensures that the OpenFGA authorization model stays in sync with the user group membership.

## How It Works

### When a User Group is Created
- For each user in the `user_ids` array, a relationship tuple is created:
  - **User**: `user:{user_id}`
  - **Relation**: `member`
  - **Object**: `group:{group_id}`

### When a User Group is Updated
- **Adding users**: New member relationships are created for newly added users
- **Removing users**: Existing member relationships are deleted for removed users
- **No change**: Users that remain in the group keep their existing relationships

### When a User Group is Deleted
- All member relationships for that group are automatically removed

## Example OpenFGA Tuples

When user `123` is added to group `abc`, the following tuple is created:
```
user:123 member group:abc
```

## API Endpoints

### Create User Group
```http
POST /user-groups
Content-Type: application/json

{
  "name": "Engineering Team",
  "description": "Software engineering team members",
  "user_ids": ["user-1", "user-2", "user-3"]
}
```

This will automatically create 3 member relationships in OpenFGA.

### Update User Group
```http
PUT /user-groups/{group-id}
Content-Type: application/json

{
  "name": "Engineering Team",
  "description": "Updated description",
  "user_ids": ["user-1", "user-4"]  // Removed user-2, user-3; Added user-4
}
```

This will:
- Remove member relationships for `user-2` and `user-3`
- Create a new member relationship for `user-4`
- Keep the existing relationship for `user-1`

## Frontend Integration

The frontend now displays:
- **User Groups**: Shows which groups each user belongs to
- **OpenFGA Relationships**: Shows the actual OpenFGA member relationships created
- **Visual Indicators**: Green badges indicate active OpenFGA relationships

## Testing

Run the OpenFGA integration tests:
```bash
cd back-end
python -m pytest test_rebecca_api.py::test_user_group_creates_member_relationships -v
python -m pytest test_rebecca_api.py::test_user_group_deletion_removes_member_relationships -v
```

## Benefits

1. **Automatic Sync**: No manual relationship management needed
2. **Consistency**: User group membership always matches OpenFGA relationships
3. **Audit Trail**: All relationships have timestamps and can be tracked
4. **Zero Drift**: No possibility of groups and relationships getting out of sync

## Future Enhancements

- Support for hierarchical groups (group membership inheritance)
- Custom relation types beyond "member"
- Batch relationship operations for better performance
- Integration with external OpenFGA servers
