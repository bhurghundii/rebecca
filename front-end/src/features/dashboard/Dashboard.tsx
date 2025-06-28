import { useState, useEffect } from 'react'
import { userService, resourceService, relationshipService } from '../../services'

interface DashboardStats {
  users: number
  resources: number
  relationships: number
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({ users: 0, resources: 0, relationships: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [users, resources, relationships] = await Promise.all([
        userService.getUsers(),
        resourceService.getResources(),
        relationshipService.getRelationships()
      ])

      setStats({
        users: users.length,
        resources: resources.length,
        relationships: relationships.length
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard">
      <h2>Dashboard Overview</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>👥 Users</h3>
          <div className="stat-number">{stats.users}</div>
        </div>
        
        <div className="stat-card">
          <h3>📁 Resources</h3>
          <div className="stat-number">{stats.resources}</div>
        </div>
        
        <div className="stat-card">
          <h3>🔗 Relationships</h3>
          <div className="stat-number">{stats.relationships}</div>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <button onClick={loadStats} className="btn btn-primary">
          🔄 Refresh Stats
        </button>
      </div>
    </div>
  )
}
