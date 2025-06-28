import { apiClient } from './api'
import type { Resource, CreateResourceRequest } from '../types/api'

export const resourceService = {
  async getResources(): Promise<Resource[]> {
    const response = await apiClient.get<Resource[]>('/resources')
    return response.data
  },

  async getResourceById(id: string): Promise<Resource> {
    const response = await apiClient.get<Resource>(`/resources/${id}`)
    return response.data
  },

  async createResource(resourceData: CreateResourceRequest): Promise<Resource> {
    const response = await apiClient.post<Resource>('/resources', resourceData)
    return response.data
  },

  async updateResource(id: string, resourceData: Partial<CreateResourceRequest>): Promise<Resource> {
    const response = await apiClient.put<Resource>(`/resources/${id}`, resourceData)
    return response.data
  },

  async deleteResource(id: string): Promise<void> {
    await apiClient.delete(`/resources/${id}`)
  }
}
