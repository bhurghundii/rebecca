import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface Stats {
  users: number
  resources: number
  relationships: number
}

function Dashboard() {
  const [stats, setStats] = useState<Stats>({ users: 0, resources: 0, relationships: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const [usersRes, resourcesRes, relationshipsRes] = await Promise.all([
        axios.get(`${API_BASE}/users`),
        axios.get(`${API_BASE}/resources`),
        axios.get(`${API_BASE}/relationships`)
      ])

      setStats({
        users: usersRes.data.length,
        resources: resourcesRes.data.length,
        relationships: relationshipsRes.data.length
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

export default Dashboard
