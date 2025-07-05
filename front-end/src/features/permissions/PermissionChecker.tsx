import { useState, useEffect } from 'react'
import { relationshipService, userService, resourceService, userGroupService } from '../../services'
import type { 
  User, 
  Resource,
  UserGroup, 
  PermissionCheckRequest, 
  PermissionCheckResponse 
} from '../../types/api'

export function PermissionChecker() {
  const [users, setUsers] = useState<User[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [userGroups, setUserGroups] = useState<UserGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)
  const [result, setResult] = useState<PermissionCheckResponse | { error: string } | null>(null)
  const [formData, setFormData] = useState<PermissionCheckRequest>({
    user: '',
    relation: 'viewer',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [usersData, resourcesData, userGroupsData] = await Promise.all([
        userService.getUsers(),
        resourceService.getResources(),
        userGroupService.getUserGroups()
      ])
      
      setUsers(usersData)
      setResources(resourcesData)
      setUserGroups(userGroupsData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const checkPermission = async (e: React.FormEvent) => {
    e.preventDefault()
    setChecking(true)
    setResult(null)
    
    try {
      const response = await relationshipService.checkPermission(formData)
      setResult(response)
    } catch (error) {
      console.error('Failed to check permission:', error)
      setResult({ error: 'Failed to check permission' })
    } finally {
      setChecking(false)
    }
  }

  const getSubjectName = (subjectRef: string) => {
    // Extract subject ID and type from "type:id" format
    const parts = subjectRef.split(':')
    if (parts.length === 2) {
      const [subjectType, subjectId] = parts
      
      if (subjectType === 'user') {
        const user = users.find(u => u.id === subjectId)
        return user ? user.name : subjectId
      } else if (subjectType === 'group') {
        const group = userGroups.find(g => g.id === subjectId)
        return group ? `${group.name} (group)` : subjectId
      }
    }
    
    // Fallback: handle subjects without type prefix (legacy format)
    // Try to find as user ID first
    const user = users.find(u => u.id === subjectRef)
    if (user) {
      return user.name
    }
    
    // Try to find as group ID
    const group = userGroups.find(g => g.id === subjectRef)
    if (group) {
      return `${group.name} (group)`
    }
    
    // If not found, return the raw reference
    return subjectRef
  }

  const getResourceName = (objectRef: string) => {
    // Extract resource ID from "type:id" format
    const parts = objectRef.split(':')
    if (parts.length === 2) {
      const [objectType, resourceId] = parts
      
      if (objectType === 'group') {
        const group = userGroups.find(g => g.id === resourceId)
        return group ? `${group.name} (user group)` : `group:${resourceId}`
      } else {
        const resource = resources.find(r => r.id === resourceId)
        return resource ? `${resource.name} (${objectType})` : `${objectType}:${resourceId}`
      }
    }
    
    // Fallback: handle objects without type prefix (legacy format)
    // Try to find the object in resources first
    const resource = resources.find(r => r.id === objectRef)
    if (resource) {
      return `${resource.name} (${resource.type})`
    }
    
    // Try to find the object in user groups
    const group = userGroups.find(g => g.id === objectRef)
    if (group) {
      return `${group.name} (user group)`
    }
    
    // If not found, return the raw reference
    return objectRef
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading permission checker...</div>
  }

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b-2 border-gray-200">
        <h2 className="text-3xl font-bold text-gray-800">🔒 Permission Checker</h2>
        <p className="text-gray-600 mt-2">Check if a user or user group has permission to perform an action on a resource.</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={checkPermission} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subject (User or Group):</label>
            <select
              value={formData.user}
              onChange={(e) => setFormData({ ...formData, user: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a subject...</option>
              <optgroup label="👤 Users">
                {users.map((user) => (
                  <option key={user.id} value={`user:${user.id}`}>
                    {user.name} ({user.email})
                  </option>
                ))}
              </optgroup>
              <optgroup label="👥 User Groups">
                {userGroups.map((group) => (
                  <option key={group.id} value={`group:${group.id}`}>
                    {group.name} ({group.user_count} members)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Relation:</label>
            <select
              value={formData.relation}
              onChange={(e) => setFormData({ ...formData, relation: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="viewer">👁️ Viewer (can view/read)</option>
              <option value="editor">✏️ Editor (can modify/edit)</option>
              <option value="owner">👑 Owner (full access)</option>
              <option value="member">👥 Member (group membership)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Object:</label>
            <select
              value={formData.object}
              onChange={(e) => setFormData({ ...formData, object: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select an object...</option>
              <optgroup label="📄 Resources">
                {resources.map((resource) => (
                  <option key={resource.id} value={`${resource.type}:${resource.id}`}>
                    {resource.name} ({resource.type})
                  </option>
                ))}
              </optgroup>
              <optgroup label="👥 User Groups">
                {userGroups.map((group) => (
                  <option key={group.id} value={`group:${group.id}`}>
                    {group.name} (user group)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
          
          <button 
            type="submit" 
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed" 
            disabled={checking}
          >
            {checking ? '⏳ Checking...' : '🔍 Check Permission'}
          </button>
        </form>
      </div>

      {result && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-800">Permission Check Result</h3>
          
          {'error' in result ? (
            <div className="flex items-center gap-4 p-6 bg-orange-50 border-l-4 border-orange-400 rounded-lg">
              <div className="text-2xl">❌</div>
              <div>
                <h4 className="text-lg font-medium text-gray-800 mb-2">Error</h4>
                <p className="text-gray-600">{result.error}</p>
              </div>
            </div>
          ) : (
            <div className={`flex items-center gap-4 p-6 border-l-4 rounded-lg ${
              result.allowed 
                ? 'bg-green-50 border-green-400' 
                : 'bg-red-50 border-red-400'
            }`}>
              <div className="text-2xl">
                {result.allowed ? '✅' : '🚫'}
              </div>
              <div>
                <h4 className="text-lg font-medium text-gray-800 mb-2">
                  {result.allowed ? 'Permission Granted' : 'Permission Denied'}
                </h4>
                <div className="space-y-1 text-sm text-gray-600">
                  <p><strong>Subject:</strong> {getSubjectName(formData.user)}</p>
                  <p><strong>Relation:</strong> {formData.relation}</p>
                  <p><strong>Object:</strong> {getResourceName(formData.object)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">How OpenFGA Permissions Work</h3>
        <ul className="space-y-2 text-gray-600 ml-6 list-disc">
          <li>Select a subject (user or user group)</li>
          <li>Choose the relation type you want to check:
            <ul className="ml-6 mt-1 list-disc text-sm">
              <li><strong>viewer:</strong> Can view or read the object</li>
              <li><strong>editor:</strong> Can modify or edit the object</li>
              <li><strong>owner:</strong> Has full access to the object</li>
              <li><strong>member:</strong> Is a member of a group</li>
            </ul>
          </li>
          <li>Select the object (resource or user group)</li>
          <li>Click "Check Permission" to verify the relationship exists</li>
        </ul>
        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <p className="text-sm text-blue-700">
            <strong>Examples:</strong>
          </p>
          <ul className="text-sm text-blue-700 mt-1 ml-4 list-disc">
            <li>Check if a user is an "owner" of a "document"</li>
            <li>Check if a user group has "viewer" access to a "project"</li>
            <li>Check if a user is a "member" of a "group"</li>
          </ul>
        </div>
        <div className="mt-2 p-3 bg-amber-50 rounded-md">
          <p className="text-sm text-amber-700">
            <strong>Note:</strong> This checks for direct relationships. In a full OpenFGA implementation, 
            indirect permissions through group membership and inheritance would also be evaluated.
          </p>
        </div>
      </div>
    </div>
  )
}
