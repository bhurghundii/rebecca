import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface User {
  id: string
  name: string
  email: string
}

interface Resource {
  id: string
  name: string
}

function PermissionChecker() {
  const [users, setUsers] = useState<User[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [checking, setChecking] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [formData, setFormData] = useState({
    user: '',
    relation: 'viewer',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [usersRes, resourcesRes] = await Promise.all([
        axios.get(`${API_BASE}/users`),
        axios.get(`${API_BASE}/resources`)
      ])
      
      setUsers(usersRes.data)
      setResources(resourcesRes.data)
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
      const response = await axios.post(`${API_BASE}/relationships/check`, formData)
      setResult(response.data)
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
    return <div className="loading">Loading permission checker...</div>
  }

  return (
    <div className="permission-checker">
      <h2>🔒 Permission Checker</h2>
      <p>Check if a user has permission to perform an action on a resource.</p>

      <div className="checker-form">
        <form onSubmit={checkPermission} className="simple-form">
          <div className="form-group">
            <label>User:</label>
            <select
              value={formData.user}
              onChange={(e) => setFormData({ ...formData, user: e.target.value })}
              required
            >
              <option value="">Select a user...</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Permission:</label>
            <select
              value={formData.relation}
              onChange={(e) => setFormData({ ...formData, relation: e.target.value })}
            >
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
              <option value="owner">Owner</option>
              <option value="member">Member</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Resource:</label>
            <select
              value={formData.object}
              onChange={(e) => setFormData({ ...formData, object: e.target.value })}
              required
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
            className="btn btn-primary" 
            disabled={checking}
          >
            {checking ? '⏳ Checking...' : '🔍 Check Permission'}
          </button>
        </form>
      </div>

      {result && (
        <div className="result-section">
          <h3>Permission Check Result</h3>
          
          {result.error ? (
            <div className="result-card error">
              <div className="result-icon">❌</div>
              <div className="result-content">
                <h4>Error</h4>
                <p>{result.error}</p>
              </div>
            </div>
          ) : (
            <div className={`result-card ${result.allowed ? 'success' : 'denied'}`}>
              <div className="result-icon">
                {result.allowed ? '✅' : '🚫'}
              </div>
              <div className="result-content">
                <h4>{result.allowed ? 'Permission Granted' : 'Permission Denied'}</h4>
                <div className="permission-details">
                  <p><strong>User:</strong> {getUserName(formData.user)}</p>
                  <p><strong>Permission:</strong> {formData.relation}</p>
                  <p><strong>Resource:</strong> {getResourceName(formData.object)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="info-section">
        <h3>How it works</h3>
        <ul>
          <li>Select a user from your user list</li>
          <li>Choose the permission you want to check</li>
          <li>Select the resource to check against</li>
          <li>Click "Check Permission" to see if access is allowed</li>
        </ul>
      </div>
    </div>
  )
}

export default PermissionChecker
