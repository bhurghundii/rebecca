import { useState, useEffect } from 'react'
import { relationshipService, userService, resourceService, resourceGroupService, userGroupService } from '../../services'
import type { 
  Relationship, 
  CreateRelationshipRequest,
  User, 
  Resource,
  ResourceGroup,
  UserGroup 
} from '../../types/api'

export function Relationships() {
  const [relationships, setRelationships] = useState<Relationship[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [userGroups, setUserGroups] = useState<UserGroup[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [resourceGroups, setResourceGroups] = useState<ResourceGroup[]>([])
  const [selectedResourceGroupId, setSelectedResourceGroupId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [viewMode, setViewMode] = useState<'matrix' | 'table'>('matrix')
  const [userSelectionMode, setUserSelectionMode] = useState<'users' | 'groups'>('users')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<CreateRelationshipRequest>({
    user: '',
    relation: 'viewer',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [relationshipsData, usersData, userGroupsData, resourcesData, resourceGroupsData] = await Promise.all([
        relationshipService.getRelationships(),
        userService.getUsers(),
        userGroupService.getUserGroups(),
        resourceService.getResources(),
        resourceGroupService.getResourceGroups()
      ])
      
      setRelationships(relationshipsData)
      setUsers(usersData)
      setUserGroups(userGroupsData)
      setResources(resourcesData)
      setResourceGroups(resourceGroupsData)
      
      // Set first resource group as default if none selected
      if (!selectedResourceGroupId && resourceGroupsData.length > 0) {
        setSelectedResourceGroupId(resourceGroupsData[0].id)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createRelationship = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingId) {
        // Update existing relationship
        await relationshipService.updateRelationship(editingId, formData)
        setEditingId(null)
      } else {
        // Create new relationship
        await relationshipService.createRelationship(formData)
      }
      setFormData({ user: '', relation: 'viewer', object: '' })
      setShowForm(false)
      loadData()
    } catch (error) {
      console.error('Failed to save relationship:', error)
    }
  }

  const startEdit = (relationship: Relationship) => {
    setFormData({
      user: relationship.user,
      relation: relationship.relation,
      object: relationship.object
    })
    setEditingId(relationship.id)
    setShowForm(true)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setFormData({ user: '', relation: 'viewer', object: '' })
    setShowForm(false)
  }

  const deleteRelationship = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this relationship?')) {
      try {
        await relationshipService.deleteRelationship(id)
        loadData()
      } catch (error) {
        console.error('Failed to delete relationship:', error)
      }
    }
  }

  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId)
    return user ? user.name : userId
  }

  const getResourceName = (resourceId: string) => {
    const resource = resources.find(r => r.id === resourceId)
    return resource ? resource.name : resourceId
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading relationships...</div>
  }

  const getRelationBadge = (relation: string) => {
    const colors = {
      owner: 'bg-blue-100 text-blue-800',
      editor: 'bg-orange-100 text-orange-800',
      viewer: 'bg-emerald-100 text-emerald-800',
      member: 'bg-purple-100 text-purple-800'
    }
    return colors[relation as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  // Helper function to get relationship between user and resource
  const getUserResourceRelation = (userId: string, resourceId: string) => {
    // Find the resource to get its type for the OpenFGA format
    const resource = resources.find(r => r.id === resourceId)
    const resourceType = resource ? resource.type : 'resource'
    
    return relationships.find(rel => 
      rel.user === `user:${userId}` && 
      rel.object === `${resourceType}:${resourceId}`
    )
  }

  // Helper function to get relationship between group and resource
  const getGroupResourceRelation = (groupId: string, resourceId: string) => {
    // Find the resource to get its type for the OpenFGA format
    const resource = resources.find(r => r.id === resourceId)
    const resourceType = resource ? resource.type : 'resource'
    
    return relationships.find(rel => 
      rel.user === `group:${groupId}` && 
      rel.object === `${resourceType}:${resourceId}`
    )
  }

  // Helper function to update or create relationship
  const updateMatrixRelation = async (userId: string, resourceId: string, newRelation: string) => {
    const existingRelation = getUserResourceRelation(userId, resourceId)
    
    // Find the resource to get its type for the OpenFGA format
    const resource = resources.find(r => r.id === resourceId)
    const resourceType = resource ? resource.type : 'resource'
    
    try {
      if (existingRelation) {
        if (newRelation === 'none') {
          // Delete relationship
          await relationshipService.deleteRelationship(existingRelation.id)
        } else {
          // Update relationship
          await relationshipService.updateRelationship(existingRelation.id, { relation: newRelation })
        }
      } else if (newRelation !== 'none') {
        // Create new relationship with OpenFGA format
        await relationshipService.createRelationship({
          user: `user:${userId}`,
          relation: newRelation,
          object: `${resourceType}:${resourceId}`
        })
      }
      loadData()
    } catch (error) {
      console.error('Failed to update relationship:', error)
    }
  }

  // Helper function to update or create group relationship
  const updateMatrixGroupRelation = async (groupId: string, resourceId: string, newRelation: string) => {
    const existingRelation = getGroupResourceRelation(groupId, resourceId)
    
    // Find the resource to get its type for the OpenFGA format
    const resource = resources.find(r => r.id === resourceId)
    const resourceType = resource ? resource.type : 'resource'
    
    try {
      if (existingRelation) {
        if (newRelation === 'none') {
          // Delete relationship
          await relationshipService.deleteRelationship(existingRelation.id)
        } else {
          // Update relationship
          await relationshipService.updateRelationship(existingRelation.id, { relation: newRelation })
        }
      } else if (newRelation !== 'none') {
        // Create new relationship with OpenFGA format
        await relationshipService.createRelationship({
          user: `group:${groupId}`,
          relation: newRelation,
          object: `${resourceType}:${resourceId}`
        })
      }
      loadData()
    } catch (error) {
      console.error('Failed to update group relationship:', error)
    }
  }

  // Helper function to get resources for the selected resource group
  const getCurrentResources = () => {
    if (!selectedResourceGroupId) return resources
    const selectedGroup = resourceGroups.find(group => group.id === selectedResourceGroupId)
    return selectedGroup ? selectedGroup.resources : resources
  }

  // Matrix View Component
  const MatrixView = () => {
    const currentResources = getCurrentResources()
    const selectedGroup = resourceGroups.find(group => group.id === selectedResourceGroupId)
    
    return (
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Permissions Matrix</h3>
              <p className="text-sm text-gray-600 mt-1">
                {selectedGroup ? `Showing resources from: ${selectedGroup.name}` : 'Showing all resources'}
              </p>
            </div>
            <div className="flex items-center space-x-6">
              <div className="relative">
                <label className="block text-xs font-medium text-gray-700 mb-1">Show:</label>
                <div className="flex rounded-md overflow-hidden bg-gray-100 p-1">
                  <button
                    type="button"
                    onClick={() => setUserSelectionMode('users')}
                    className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                      userSelectionMode === 'users'
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    👤 Users
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserSelectionMode('groups')}
                    className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                      userSelectionMode === 'groups'
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    👥 Groups
                  </button>
                </div>
              </div>
              <div className="relative">
                <label className="block text-xs font-medium text-gray-700 mb-1">Resource Group:</label>
                <select
                  value={selectedResourceGroupId || ''}
                  onChange={(e) => setSelectedResourceGroupId(e.target.value || null)}
                  className="appearance-none bg-white border border-gray-300 rounded-md px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[200px]"
                >
                  <option value="">All Resources ({resources.length})</option>
                  {resourceGroups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name} ({group.resources.length} resources)
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none top-6">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 border-r border-gray-300 sticky left-0 bg-gray-50 z-10 min-w-[200px]">
                  {userSelectionMode === 'users' ? 'User' : 'User Group'}
                </th>
                {currentResources.map((resource) => (
                  <th key={resource.id} className="px-4 py-3 text-center text-sm font-medium text-gray-700 border-r border-gray-300 min-w-[120px]">
                    <div className="truncate" title={resource.name}>
                      {resource.name}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {userSelectionMode === 'users' ? (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 border-r border-gray-300 sticky left-0 bg-white hover:bg-gray-50 z-10">
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </div>
                    </td>
                    {currentResources.map((resource) => {
                      const relation = getUserResourceRelation(user.id, resource.id)
                      return (
                        <td key={resource.id} className="px-4 py-3 text-center border-r border-gray-300">
                          {relation ? (
                            <select
                              value={relation.relation}
                              onChange={(e) => updateMatrixRelation(user.id, resource.id, e.target.value)}
                              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-[80px]"
                              title={`${user.name} → ${resource.name}`}
                            >
                              <option value="viewer">Viewer</option>
                              <option value="editor">Editor</option>
                              <option value="owner">Owner</option>
                              <option value="member">Member</option>
                            </select>
                          ) : (
                            <select
                              value="none"
                              onChange={(e) => updateMatrixRelation(user.id, resource.id, e.target.value)}
                              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-[80px] text-gray-400"
                              title={`${user.name} → ${resource.name}`}
                            >
                              <option value="none">-</option>
                              <option value="viewer">Viewer</option>
                              <option value="editor">Editor</option>
                              <option value="owner">Owner</option>
                              <option value="member">Member</option>
                            </select>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))
              ) : (
                userGroups.map((group) => (
                  <tr key={group.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 border-r border-gray-300 sticky left-0 bg-white hover:bg-gray-50 z-10">
                      <div>
                        <div className="font-medium">{group.name}</div>
                        <div className="text-xs text-gray-500">{group.user_count} members</div>
                      </div>
                    </td>
                    {currentResources.map((resource) => {
                      const relation = getGroupResourceRelation(group.id, resource.id)
                      return (
                        <td key={resource.id} className="px-4 py-3 text-center border-r border-gray-300">
                          {relation ? (
                            <select
                              value={relation.relation}
                              onChange={(e) => updateMatrixGroupRelation(group.id, resource.id, e.target.value)}
                              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-[80px]"
                              title={`${group.name} → ${resource.name}`}
                            >
                              <option value="viewer">Viewer</option>
                              <option value="editor">Editor</option>
                              <option value="owner">Owner</option>
                              <option value="member">Member</option>
                            </select>
                          ) : (
                            <select
                              value="none"
                              onChange={(e) => updateMatrixGroupRelation(group.id, resource.id, e.target.value)}
                              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white min-w-[80px] text-gray-400"
                              title={`${group.name} → ${resource.name}`}
                            >
                              <option value="none">-</option>
                              <option value="viewer">Viewer</option>
                              <option value="editor">Editor</option>
                              <option value="owner">Owner</option>
                              <option value="member">Member</option>
                            </select>
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center pb-4 border-b-2 border-gray-200">
        <h2 className="text-3xl font-bold text-gray-800">🔗 Relationships Management</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('matrix')}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                viewMode === 'matrix' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Matrix View
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                viewMode === 'table' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Table View
            </button>
          </div>
          <button 
            onClick={() => editingId ? cancelEdit() : setShowForm(!showForm)} 
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            {showForm ? 'Cancel' : '+ Add Relationship'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">
            {editingId ? 'Edit Relationship' : 'Create New Relationship'}
          </h3>
          <form onSubmit={createRelationship} className="space-y-4 max-w-md">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">User:</label>
                <div className="flex rounded-md overflow-hidden bg-gray-100 p-1">
                  <button
                    type="button"
                    onClick={() => setUserSelectionMode('users')}
                    className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                      userSelectionMode === 'users'
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    👤 Users
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserSelectionMode('groups')}
                    className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                      userSelectionMode === 'groups'
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    👥 Groups
                  </button>
                </div>
              </div>
              <select
                value={formData.user}
                onChange={(e) => setFormData({ ...formData, user: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">
                  {userSelectionMode === 'users' ? 'Select a user...' : 'Select a group...'}
                </option>
                {userSelectionMode === 'users' ? (
                  users.map((user) => (
                    <option key={user.id} value={`user:${user.id}`}>
                      {user.name} ({user.email})
                    </option>
                  ))
                ) : (
                  userGroups.map((group) => (
                    <option key={group.id} value={`group:${group.id}`}>
                      {group.name} ({group.user_count} members)
                    </option>
                  ))
                )}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Relation:</label>
              <select
                value={formData.relation}
                onChange={(e) => setFormData({ ...formData, relation: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="viewer">Viewer</option>
                <option value="editor">Editor</option>
                <option value="owner">Owner</option>
                <option value="member">Member</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Resource:</label>
              <select
                value={formData.object}
                onChange={(e) => setFormData({ ...formData, object: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a resource...</option>
                {resources.map((resource) => (
                  <option key={resource.id} value={resource.id}>
                    {resource.name} ({resource.id})
                  </option>
                ))}
              </select>
            </div>
            
            <button type="submit" className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium">
              {editingId ? 'Update Relationship' : 'Create Relationship'}
            </button>
          </form>
        </div>
      )}

      {/* Conditional rendering based on view mode */}
      {viewMode === 'matrix' ? (
        <MatrixView />
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">Relationships ({relationships.length})</h3>
          </div>
          
          {relationships.length === 0 ? (
            <div className="text-center py-12 text-gray-500 italic">No relationships found. Create your first relationship!</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Relation</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resource</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {relationships.map((rel) => (
                    <tr key={rel.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{getUserName(rel.user)}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span 
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded-full cursor-pointer hover:opacity-80 transition-opacity ${getRelationBadge(rel.relation)}`}
                          onClick={() => startEdit(rel)}
                          title="Click to edit"
                        >
                          {rel.relation}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{getResourceName(rel.object)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(rel.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => startEdit(rel)}
                          className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                          title="Edit relationship"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => deleteRelationship(rel.id)}
                          className="inline-flex items-center px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                          title="Delete relationship"
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
