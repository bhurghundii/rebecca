import { useState, useEffect } from 'react'
import { userGroupService, userService } from '../../services'
import type { UserGroup, CreateUserGroupRequest, User } from '../../types/api'

export function UserGroups() {
  const [userGroups, setUserGroups] = useState<UserGroup[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateUserGroupRequest>({
    name: '',
    description: '',
    user_ids: []
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [groupsData, usersData] = await Promise.all([
        userGroupService.getUserGroups(),
        userService.getUsers()
      ])
      setUserGroups(groupsData)
      setUsers(usersData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createUserGroup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await userGroupService.createUserGroup(formData)
      setFormData({ name: '', description: '', user_ids: [] })
      setShowForm(false)
      loadData()
    } catch (error) {
      console.error('Failed to create user group:', error)
    }
  }

  const deleteUserGroup = async (id: string) => {
    if (confirm('Are you sure you want to delete this user group?')) {
      try {
        await userGroupService.deleteUserGroup(id)
        loadData()
      } catch (error) {
        console.error('Failed to delete user group:', error)
      }
    }
  }

  const handleUserSelection = (userId: string, isSelected: boolean) => {
    if (isSelected) {
      setFormData({
        ...formData,
        user_ids: [...formData.user_ids, userId]
      })
    } else {
      setFormData({
        ...formData,
        user_ids: formData.user_ids.filter(id => id !== userId)
      })
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading user groups...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center pb-4 border-b-2 border-gray-200">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">👥 User Groups Management</h2>
          <p className="text-sm text-gray-600 mt-1">
            🔗 Adding users to groups automatically creates OpenFGA "member" relationships
          </p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          {showForm ? 'Cancel' : '+ Add User Group'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">Create New User Group</h3>
          <form onSubmit={createUserGroup} className="space-y-6 max-w-2xl">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Group Name:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g. Engineering Team"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                placeholder="Describe the purpose of this group..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Users:</label>
              <div className="border border-gray-300 rounded-md p-4 max-h-80 overflow-y-auto bg-gray-50">
                {users.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 italic">No users available. Create some users first!</div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {users.map((user) => (
                      <label key={user.id} className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-md hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all">
                        <input
                          type="checkbox"
                          checked={formData.user_ids.includes(user.id)}
                          onChange={(e) => handleUserSelection(user.id, e.target.checked)}
                          className="mt-1"
                        />
                        <div className="flex flex-col gap-1 min-w-0 flex-1">
                          <span className="font-medium text-gray-900">{user.name}</span>
                          <span className="text-sm text-gray-500">{user.email}</span>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Selected: {formData.user_ids.length} user(s)
              </div>
            </div>
            
            <button 
              type="submit" 
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={formData.user_ids.length === 0}
            >
              Create User Group
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">User Groups ({userGroups.length})</h3>
        </div>
        
        {userGroups.length === 0 ? (
          <div className="text-center py-12 text-gray-500 italic">No user groups found. Create your first user group!</div>
        ) : (
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {userGroups.map((group) => (
                <div key={group.id} className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-lg font-semibold text-gray-800">{group.name}</h4>
                    <button
                      onClick={() => deleteUserGroup(group.id)}
                      className="inline-flex items-center px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                  
                  {group.description && (
                    <p className="text-gray-600 mb-4 italic">{group.description}</p>
                  )}
                  
                  <div className="flex flex-col gap-2 mb-4 pb-4 border-b border-gray-300">
                    <span className="text-sm text-gray-600">
                      👥 {group.user_count} member(s)
                    </span>
                    <span className="text-sm text-gray-600">
                      📅 Created {new Date(group.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium text-gray-800 mb-2">Members:</h5>
                    {group.users.length === 0 ? (
                      <div className="text-center py-4 text-gray-500 italic bg-white rounded border">No members</div>
                    ) : (
                      <div className="space-y-2">
                        {group.users.map((user) => (
                          <div key={user.id} className="flex flex-col p-2 bg-white rounded border-l-4 border-blue-400">
                            <span className="font-medium text-gray-900">{user.name}</span>
                            <span className="text-xs text-gray-500">{user.email}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
