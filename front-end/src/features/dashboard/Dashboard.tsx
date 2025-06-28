import { useState, useEffect } from 'react'
import { 
  userService, 
  resourceService, 
  relationshipService, 
  userGroupService, 
  resourceGroupService 
} from '../../services'

interface DashboardStats {
  users: number
  resources: number
  relationships: number
  userGroups: number
  resourceGroups: number
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ 
    users: 0, 
    resources: 0, 
    relationships: 0, 
    userGroups: 0, 
    resourceGroups: 0 
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [users, resources, relationships, userGroups, resourceGroups] = await Promise.all([
        userService.getUsers(),
        resourceService.getResources(),
        relationshipService.getRelationships(),
        userGroupService.getUserGroups(),
        resourceGroupService.getResourceGroups()
      ])

      setStats({
        users: users.length,
        resources: resources.length,
        relationships: relationships.length,
        userGroups: userGroups.length,
        resourceGroups: resourceGroups.length
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading dashboard...</div>
  }

  return (
    <div className="space-y-8">
      <h2 className="text-3xl font-bold text-gray-800">Dashboard Overview</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">👥 Users</h3>
          <div className="text-3xl font-bold text-gray-800">{stats.users}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">📁 Resources</h3>
          <div className="text-3xl font-bold text-gray-800">{stats.resources}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">🔗 Relationships</h3>
          <div className="text-3xl font-bold text-gray-800">{stats.relationships}</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">👫 User Groups</h3>
          <div className="text-3xl font-bold text-gray-800">{stats.userGroups}</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">📚 Resource Groups</h3>
          <div className="text-3xl font-bold text-gray-800">{stats.resourceGroups}</div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <button 
          onClick={loadStats} 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          🔄 Refresh Stats
        </button>
      </div>
    </div>
  )
}
