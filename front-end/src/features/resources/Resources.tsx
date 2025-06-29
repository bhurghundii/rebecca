import { useState, useEffect } from 'react'
import { resourceService, resourceGroupService } from '../../services'
import type { Resource, CreateResourceRequest, ResourceGroup } from '../../types/api'

export function Resources() {
  const [resources, setResources] = useState<Resource[]>([])
  const [resourceGroups, setResourceGroups] = useState<ResourceGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    resource_name: '',
    resource_type: 'document',
    description: '',
    category: ''
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [resourcesData, resourceGroupsData] = await Promise.all([
        resourceService.getResources(),
        resourceGroupService.getResourceGroups()
      ])
      setResources(resourcesData)
      setResourceGroups(resourceGroupsData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createResource = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload: CreateResourceRequest = {
        resource_name: formData.resource_name,
        resource_type: formData.resource_type,
        metadata: {
          description: formData.description,
          category: formData.category
        }
      }
      await resourceService.createResource(payload)
      setFormData({ resource_name: '', resource_type: 'document', description: '', category: '' })
      setShowForm(false)
      loadData()
    } catch (error) {
      console.error('Failed to create resource:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading resources...</div>
  }

  const getResourceTypeBadge = (type: string) => {
    const colors = {
      document: 'bg-blue-100 text-blue-800',
      folder: 'bg-orange-100 text-orange-800',
      file: 'bg-purple-100 text-purple-800',
      system: 'bg-red-100 text-red-800'
    }
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  const getResourceGroupBadges = (resourceId: string) => {
    const groups = resourceGroups.filter(group => 
      group.resources.some(resource => resource.id === resourceId)
    )
    
    if (groups.length === 0) {
      return <span className="text-gray-400 italic">No groups</span>
    }
    
    return (
      <div className="flex flex-wrap gap-1">
        {groups.map(group => (
          <span 
            key={group.id}
            className="inline-flex px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
            title={group.description || group.name}
          >
            {group.name}
          </span>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center pb-4 border-b-2 border-gray-200">
        <h2 className="text-3xl font-bold text-gray-800">📁 Resources Management</h2>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          {showForm ? 'Cancel' : '+ Add Resource'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">Create New Resource</h3>
          <form onSubmit={createResource} className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Resource Name:</label>
              <input
                type="text"
                value={formData.resource_name}
                onChange={(e) => setFormData({ ...formData, resource_name: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type:</label>
              <select
                value={formData.resource_type}
                onChange={(e) => setFormData({ ...formData, resource_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="document">Document</option>
                <option value="folder">Folder</option>
                <option value="file">File</option>
                <option value="system">System</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category:</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g. reports, documents, etc."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <button type="submit" className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium">
              Create Resource
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">Resources ({resources.length})</h3>
        </div>
        
        {resources.length === 0 ? (
          <div className="text-center py-12 text-gray-500 italic">No resources found. Create your first resource!</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Groups</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {resources.map((resource) => (
                  <tr key={resource.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">{resource.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{resource.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getResourceTypeBadge(resource.resource_type)}`}>
                        {resource.resource_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {getResourceGroupBadges(resource.id)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{resource.metadata?.description || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(resource.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
