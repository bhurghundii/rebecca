import axios from 'axios'

// Base configuration - use environment variable or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export { apiClient, API_BASE_URL }
