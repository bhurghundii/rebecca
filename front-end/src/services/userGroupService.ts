import { apiClient } from './api'
import type { 
  UserGroup, 
  CreateUserGroupRequest, 
  UpdateUserGroupRequest 
} from '../types/api'

export const userGroupService = {
  async getUserGroups(): Promise<UserGroup[]> {
    const response = await apiClient.get<UserGroup[]>('/user-groups')
    return response.data
  },

  async getUserGroupById(id: string): Promise<UserGroup> {
    const response = await apiClient.get<UserGroup>(`/user-groups/${id}`)
    return response.data
  },

  async createUserGroup(groupData: CreateUserGroupRequest): Promise<UserGroup> {
    const response = await apiClient.post<UserGroup>('/user-groups', groupData)
    return response.data
  },

  async updateUserGroup(id: string, groupData: UpdateUserGroupRequest): Promise<UserGroup> {
    const response = await apiClient.put<UserGroup>(`/user-groups/${id}`, groupData)
    return response.data
  },

  async deleteUserGroup(id: string): Promise<void> {
    await apiClient.delete(`/user-groups/${id}`)
  }
}
