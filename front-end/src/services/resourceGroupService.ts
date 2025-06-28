import { apiClient } from './api'
import type { 
  ResourceGroup, 
  CreateResourceGroupRequest, 
  UpdateResourceGroupRequest 
} from '../types/api'

export const resourceGroupService = {
  async getResourceGroups(): Promise<ResourceGroup[]> {
    const response = await apiClient.get<ResourceGroup[]>('/resource-groups')
    return response.data
  },

  async getResourceGroupById(id: string): Promise<ResourceGroup> {
    const response = await apiClient.get<ResourceGroup>(`/resource-groups/${id}`)
    return response.data
  },

  async createResourceGroup(groupData: CreateResourceGroupRequest): Promise<ResourceGroup> {
    const response = await apiClient.post<ResourceGroup>('/resource-groups', groupData)
    return response.data
  },

  async updateResourceGroup(id: string, groupData: UpdateResourceGroupRequest): Promise<ResourceGroup> {
    const response = await apiClient.put<ResourceGroup>(`/resource-groups/${id}`, groupData)
    return response.data
  },

  async deleteResourceGroup(id: string): Promise<void> {
    await apiClient.delete(`/resource-groups/${id}`)
  }
}
