import { useState, useEffect } from 'react'
import { resourceGroupService, resourceService } from '../../services'
import type { ResourceGroup, CreateResourceGroupRequest, Resource } from '../../types/api'

export function ResourceGroups() {
  const [resourceGroups, setResourceGroups] = useState<ResourceGroup[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<CreateResourceGroupRequest>({
    name: '',
    description: '',
    resource_ids: []
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [groupsData, resourcesData] = await Promise.all([
        resourceGroupService.getResourceGroups(),
        resourceService.getResources()
      ])
      setResourceGroups(groupsData)
      setResources(resourcesData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createResourceGroup = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await resourceGroupService.createResourceGroup(formData)
      setFormData({ name: '', description: '', resource_ids: [] })
      setShowForm(false)
      loadData()
    } catch (error) {
      console.error('Failed to create resource group:', error)
    }
  }

  const deleteResourceGroup = async (id: string) => {
    if (confirm('Are you sure you want to delete this resource group?')) {
      try {
        await resourceGroupService.deleteResourceGroup(id)
        loadData()
      } catch (error) {
        console.error('Failed to delete resource group:', error)
      }
    }
  }

  const handleResourceSelection = (resourceId: string, isSelected: boolean) => {
    if (isSelected) {
      setFormData({
        ...formData,
        resource_ids: [...formData.resource_ids, resourceId]
      })
    } else {
      setFormData({
        ...formData,
        resource_ids: formData.resource_ids.filter(id => id !== resourceId)
      })
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-500 text-lg">Loading resource groups...</div>
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center pb-4 border-b-2 border-gray-200">
        <h2 className="text-3xl font-bold text-gray-800">📁 Resource Groups Management</h2>
        <button 
          onClick={() => setShowForm(!showForm)} 
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          {showForm ? 'Cancel' : '+ Add Resource Group'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-6">Create New Resource Group</h3>
          <form onSubmit={createResourceGroup} className="space-y-6 max-w-2xl">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Group Name:</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                placeholder="e.g. Project Documents"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description:</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                placeholder="Describe the purpose of this group..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Resources:</label>
              <div className="border border-gray-300 rounded-md p-4 max-h-80 overflow-y-auto bg-gray-50">
                {resources.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 italic">No resources available. Create some resources first!</div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {resources.map((resource) => (
                      <label key={resource.id} className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-md hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all">
                        <input
                          type="checkbox"
                          checked={formData.resource_ids.includes(resource.id)}
                          onChange={(e) => handleResourceSelection(resource.id, e.target.checked)}
                          className="mt-1"
                        />
                        <div className="flex flex-col gap-1 min-w-0 flex-1">
                          <span className="font-medium text-gray-900">{resource.name}</span>
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full self-start ${getResourceTypeBadge(resource.resource_type)}`}>
                            {resource.resource_type}
                          </span>
                          {resource.metadata?.description && (
                            <span className="text-sm text-gray-500">{resource.metadata.description}</span>
                          )}
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Selected: {formData.resource_ids.length} resource(s)
              </div>
            </div>
            
            <button 
              type="submit" 
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={formData.resource_ids.length === 0}
            >
              Create Resource Group
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">Resource Groups ({resourceGroups.length})</h3>
        </div>
        
        {resourceGroups.length === 0 ? (
          <div className="text-center py-12 text-gray-500 italic">No resource groups found. Create your first resource group!</div>
        ) : (
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {resourceGroups.map((group) => (
                <div key={group.id} className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="text-lg font-semibold text-gray-800">{group.name}</h4>
                    <button
                      onClick={() => deleteResourceGroup(group.id)}
                      className="inline-flex items-center px-2 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 transition-colors"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                  
                  {group.description && (
                    <p className="text-gray-600 mb-4 italic">{group.description}</p>
                  )}
                  
                  <div className="flex flex-col gap-2 mb-4 pb-4 border-b border-gray-300">
                    <span className="text-sm text-gray-600">
                      📁 {group.resource_count} resource(s)
                    </span>
                    <span className="text-sm text-gray-600">
                      📅 Created {new Date(group.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium text-gray-800 mb-2">Resources:</h5>
                    {group.resources.length === 0 ? (
                      <div className="text-center py-4 text-gray-500 italic bg-white rounded border">No resources</div>
                    ) : (
                      <div className="space-y-2">
                        {group.resources.map((resource) => (
                          <div key={resource.id} className="flex flex-col gap-2 p-3 bg-white rounded border-l-4 border-blue-400">
                            <span className="font-medium text-gray-900">{resource.name}</span>
                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full self-start ${getResourceTypeBadge(resource.resource_type)}`}>
                              {resource.resource_type}
                            </span>
                            {resource.metadata?.description && (
                              <span className="text-xs text-gray-500">{resource.metadata.description}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
