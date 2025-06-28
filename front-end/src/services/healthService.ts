import { apiClient } from './api'
import type { HealthCheckResponse } from '../types/api'

export const healthService = {
  async checkHealth(): Promise<HealthCheckResponse> {
    const response = await apiClient.get<HealthCheckResponse>('/health')
    return response.data
  }
}
