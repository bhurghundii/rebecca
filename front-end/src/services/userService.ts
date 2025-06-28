import { apiClient } from './api'
import type { User, CreateUserRequest } from '../types/api'

export const userService = {
  async getUsers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users')
    return response.data
  },

  async getUserById(id: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${id}`)
    return response.data
  },

  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<User>('/users', userData)
    return response.data
  },

  async updateUser(id: string, userData: Partial<CreateUserRequest>): Promise<User> {
    const response = await apiClient.put<User>(`/users/${id}`, userData)
    return response.data
  },

  async deleteUser(id: string): Promise<void> {
    await apiClient.delete(`/users/${id}`)
  }
}
