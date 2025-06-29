import { useState, useEffect } from 'react'
import { relationshipService } from '../services/relationshipService'
import { userService } from '../services/userService'
import { resourceService } from '../services/resourceService'
import type { Relationship, User, Resource } from '../types/api'

function Relationships() {
  const [relationships, setRelationships] = useState<Relationship[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    user: '',
    relation: 'can_read',
    object: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [relationshipsRes, usersRes, resourcesRes] = await Promise.all([
        relationshipService.getRelationships(),
        userService.getUsers(),
        resourceService.getResources()
      ])
      
      setRelationships(relationshipsRes)
      setUsers(usersRes)
      setResources(resourcesRes)
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
      setFormData({ user: '', relation: 'can_read', object: '' })
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
    setFormData({ user: '', relation: 'can_read', object: '' })
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
    return <div className="loading">Loading relationships...</div>
  }

  return (
    <div className="relationships">
      <div className="page-header">
        <h2>🔗 Relationships Management</h2>
        <button 
          onClick={() => editingId ? cancelEdit() : setShowForm(!showForm)} 
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : '+ Add Relationship'}
        </button>
      </div>

      {showForm && (
        <div className="form-section">
          <h3>{editingId ? 'Edit Relationship' : 'Create New Relationship'}</h3>
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
            
            <button type="submit" className="btn btn-success">
              {editingId ? 'Update Relationship' : 'Create Relationship'}
            </button>
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((rel) => (
                <tr key={rel.id}>
                  <td>{getUserName(rel.user)}</td>
                  <td>
                    <span 
                      className={`badge badge-${rel.relation.replace('can_', '')}`}
                      onClick={() => startEdit(rel)}
                      title="Click to edit"
                      style={{ 
                        cursor: 'pointer',
                        transition: 'opacity 0.2s'
                      }}
                      onMouseEnter={(e) => (e.target as HTMLSpanElement).style.opacity = '0.8'}
                      onMouseLeave={(e) => (e.target as HTMLSpanElement).style.opacity = '1'}
                    >
                      {rel.relation}
                    </span>
                  </td>
                  <td>{getResourceName(rel.object)}</td>
                  <td>{new Date(rel.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      onClick={() => startEdit(rel)}
                      style={{ 
                        marginRight: '8px', 
                        padding: '4px 8px', 
                        border: '1px solid #ccc', 
                        background: 'white', 
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                      title="Edit relationship"
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => deleteRelationship(rel.id)}
                      style={{ 
                        padding: '4px 8px', 
                        border: '1px solid #dc3545', 
                        background: '#dc3545', 
                        color: 'white', 
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                      title="Delete relationship"
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Relationships
