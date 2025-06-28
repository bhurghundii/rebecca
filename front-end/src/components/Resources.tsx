import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

interface Resource {
  id: string
  name: string
  resource_type: string
  metadata: any
  created_at: string
}

function Resources() {
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    resource_name: '',
    resource_type: 'document',
    description: '',
    category: ''
  })

  useEffect(() => {
    loadResources()
  }, [])

  const loadResources = async () => {
    try {
      const response = await axios.get(`${API_BASE}/resources`)
      setResources(response.data)
    } catch (error) {
      console.error('Failed to load resources:', error)
    } finally {
      setLoading(false)
    }
  }

  const createResource = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload = {
        resource_name: formData.resource_name,
        resource_type: formData.resource_type,
        metadata: {
          description: formData.description,
          category: formData.category
        }
      }
      await axios.post(`${API_BASE}/resources`, payload)
      setFormData({ resource_name: '', resource_type: 'document', description: '', category: '' })
      setShowForm(false)
      loadResources()
    } catch (error) {
      console.error('Failed to create resource:', error)
    }
  }

  if (loading) {
    return <div className="loading">Loading resources...</div>
  }

  return (
    <div className="resources">
      <div className="page-header">
        <h2>📁 Resources Management</h2>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : '+ Add Resource'}
        </button>
      </div>

      {showForm && (
        <div className="form-section">
          <h3>Create New Resource</h3>
          <form onSubmit={createResource} className="simple-form">
            <div className="form-group">
              <label>Resource Name:</label>
              <input
                type="text"
                value={formData.resource_name}
                onChange={(e) => setFormData({ ...formData, resource_name: e.target.value })}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Type:</label>
              <select
                value={formData.resource_type}
                onChange={(e) => setFormData({ ...formData, resource_type: e.target.value })}
              >
                <option value="document">Document</option>
                <option value="folder">Folder</option>
                <option value="file">File</option>
                <option value="system">System</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Description:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
              />
            </div>
            
            <div className="form-group">
              <label>Category:</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g. reports, documents, etc."
              />
            </div>
            
            <button type="submit" className="btn btn-success">Create Resource</button>
          </form>
        </div>
      )}

      <div className="table-section">
        <h3>Resources ({resources.length})</h3>
        
        {resources.length === 0 ? (
          <div className="empty-state">No resources found. Create your first resource!</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {resources.map((resource) => (
                <tr key={resource.id}>
                  <td className="mono">{resource.id}</td>
                  <td>{resource.name}</td>
                  <td>
                    <span className={`badge badge-${resource.resource_type}`}>
                      {resource.resource_type}
                    </span>
                  </td>
                  <td>{resource.metadata?.description || '-'}</td>
                  <td>{new Date(resource.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Resources
