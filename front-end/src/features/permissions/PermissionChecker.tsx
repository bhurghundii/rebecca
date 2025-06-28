import { useState, useEffect } from 'react'
import { relationshipService, userService, resourceService } from '../../services'
import type { 
  User, 
  Resource, 
  PermissionCheckRequest, 
  PermissionCheckResponse 
} from '../../types/api'

export function PermissionChecker() {
  const [users, setUsers] = useState<User[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)
  const [result, setResult] = useState<PermissionCheckResponse | { error: string } | null>(null)
  const [formData, setFormData] = useState<PermissionCheckRequest>({
    user: '',
    relation: 'can_read',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [usersData, resourcesData] = await Promise.all([
        userService.getUsers(),
        resourceService.getResources()
      ])
      
      setUsers(usersData)
      setResources(resourcesData)
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

  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId)
    return user ? user.name : userId
  }

  const getResourceName = (resourceId: string) => {
    const resource = resources.find(r => r.id === resourceId)
    return resource ? resource.name : resourceId
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading permission checker...</div>
  }

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b-2 border-gray-200">
        <h2 className="text-3xl font-bold text-gray-800">🔒 Permission Checker</h2>
        <p className="text-gray-600 mt-2">Check if a user has permission to perform an action on a resource.</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={checkPermission} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">User:</label>
            <select
              value={formData.user}
              onChange={(e) => setFormData({ ...formData, user: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select a user...</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Permission:</label>
            <select
              value={formData.relation}
              onChange={(e) => setFormData({ ...formData, relation: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="can_read">Can Read</option>
              <option value="can_write">Can Write</option>
              <option value="can_delete">Can Delete</option>
              <option value="owner">Owner</option>
              <option value="admin">Admin</option>
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
                  <p><strong>User:</strong> {getUserName(formData.user)}</p>
                  <p><strong>Permission:</strong> {formData.relation}</p>
                  <p><strong>Resource:</strong> {getResourceName(formData.object)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">How it works</h3>
        <ul className="space-y-2 text-gray-600 ml-6 list-disc">
          <li>Select a user from your user list</li>
          <li>Choose the permission you want to check</li>
          <li>Select the resource to check against</li>
          <li>Click "Check Permission" to see if access is allowed</li>
        </ul>
      </div>
    </div>
  )
}
