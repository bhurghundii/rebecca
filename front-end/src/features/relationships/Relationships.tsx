import { useState, useEffect } from 'react'
import { relationshipService, userService, resourceService } from '../../services'
import type { 
  Relationship, 
  CreateRelationshipRequest, 
  User, 
  Resource 
} from '../../types/api'

export function Relationships() {
  const [relationships, setRelationships] = useState<Relationship[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateRelationshipRequest>({
    user: '',
    relation: 'can_read',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [relationshipsData, usersData, resourcesData] = await Promise.all([
        relationshipService.getRelationships(),
        userService.getUsers(),
        resourceService.getResources()
      ])
      
      setRelationships(relationshipsData)
      setUsers(usersData)
      setResources(resourcesData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createRelationship = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await relationshipService.createRelationship(formData)
      setFormData({ user: '', relation: 'can_read', object: '' })
      setShowForm(false)
      loadData()
    } catch (error) {
      console.error('Failed to create relationship:', error)
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
    return <div className="loading">Loading relationships...</div>
  }

  return (
    <div className="relationships">
      <div className="page-header">
        <h2>🔗 Relationships Management</h2>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : '+ Add Relationship'}
        </button>
      </div>

      {showForm && (
        <div className="form-section">
          <h3>Create New Relationship</h3>
          <form onSubmit={createRelationship} className="simple-form">
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
              <label>Relation:</label>
              <select
                value={formData.relation}
                onChange={(e) => setFormData({ ...formData, relation: e.target.value })}
              >
                <option value="can_read">Can Read</option>
                <option value="can_write">Can Write</option>
                <option value="can_delete">Can Delete</option>
                <option value="owner">Owner</option>
                <option value="admin">Admin</option>
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
            
            <button type="submit" className="btn btn-success">Create Relationship</button>
          </form>
        </div>
      )}

      <div className="table-section">
        <h3>Relationships ({relationships.length})</h3>
        
        {relationships.length === 0 ? (
          <div className="empty-state">No relationships found. Create your first relationship!</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Relation</th>
                <th>Resource</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((rel) => (
                <tr key={rel.id}>
                  <td>{getUserName(rel.user)}</td>
                  <td>
                    <span className={`badge badge-${rel.relation.replace('can_', '')}`}>
                      {rel.relation}
                    </span>
                  </td>
                  <td>{getResourceName(rel.object)}</td>
                  <td>{new Date(rel.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
