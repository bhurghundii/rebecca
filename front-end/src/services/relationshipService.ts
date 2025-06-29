import { apiClient } from './api'
import type { 
  Relationship, 
  CreateRelationshipRequest,
  UpdateRelationshipRequest,
  PermissionCheckRequest, 
  PermissionCheckResponse 
} from '../types/api'

export const relationshipService = {
  async getRelationships(): Promise<Relationship[]> {
    const response = await apiClient.get<Relationship[]>('/relationships')
    return response.data
  },

  async getRelationshipById(id: string): Promise<Relationship> {
    const response = await apiClient.get<Relationship>(`/relationships/${id}`)
    return response.data
  },

  async createRelationship(relationshipData: CreateRelationshipRequest): Promise<Relationship> {
    const response = await apiClient.post<Relationship>('/relationships', relationshipData)
    return response.data
  },

  async deleteRelationship(id: string): Promise<void> {
    await apiClient.delete(`/relationships/${id}`)
  },

  async checkPermission(permissionData: PermissionCheckRequest): Promise<PermissionCheckResponse> {
    const response = await apiClient.post<PermissionCheckResponse>('/relationships/check', permissionData)
    return response.data
  },

  async updateRelationship(id: string, relationshipData: UpdateRelationshipRequest): Promise<Relationship> {
    const response = await apiClient.put<Relationship>(`/relationships/${id}`, relationshipData)
    return response.data
  },
}
