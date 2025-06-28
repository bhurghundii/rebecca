export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface CreateUserRequest {
  name: string
  email: string
}

export interface Resource {
  id: string
  name: string
  resource_type: string
  metadata: {
    description?: string
    category?: string
    [key: string]: any
  }
  created_at: string
}

export interface CreateResourceRequest {
  resource_name: string
  resource_type: string
  metadata: {
    description?: string
    category?: string
    [key: string]: any
  }
}

export interface Relationship {
  id: string
  user: string
  relation: string
  object: string
  created_at: string
}

export interface CreateRelationshipRequest {
  user: string
  relation: string
  object: string
}

export interface PermissionCheckRequest {
  user: string
  relation: string
  object: string
}

export interface PermissionCheckResponse {
  allowed: boolean
}

export interface HealthCheckResponse {
  status: string
  message: string
  openfga_status: string
  timestamp: string
}

export interface ApiError {
  error: string
}
