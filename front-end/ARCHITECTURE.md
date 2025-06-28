# Project Structure

This project follows a clean MVC-style architecture with separation of concerns.

## 📁 Directory Structure

```
src/
├── features/               # Feature-based organization (View layer)
│   ├── dashboard/         # Dashboard feature
│   ├── users/            # User management feature
│   ├── resources/        # Resource management feature
│   ├── relationships/    # Relationship management feature
│   ├── permissions/      # Permission checking feature
│   └── index.ts          # Feature exports
├── services/             # API layer (Model/Controller)
│   ├── api.ts           # Base API configuration
│   ├── healthService.ts # Health check API
│   ├── userService.ts   # User API operations
│   ├── resourceService.ts # Resource API operations
│   ├── relationshipService.ts # Relationship API operations
│   └── index.ts         # Service exports
├── types/               # Type definitions
│   └── api.ts          # API-related types
├── App.tsx             # Main application component
├── App.css             # Global styles
└── main.tsx            # Application entry point
```

## 🏗️ Architecture Principles

### Features (View Layer)
- Each feature is self-contained in its own folder
- Components handle UI logic and user interactions
- No direct API calls - uses services instead
- Proper TypeScript typing throughout

### Services (Model/Controller Layer)
- Centralized API logic
- Reusable across different features
- Error handling and response transformation
- Easy to mock for testing

### Types
- Shared type definitions
- API request/response interfaces
- Ensures type safety across the application

## 🔧 Benefits of This Structure

1. **Separation of Concerns**: UI logic separate from business logic
2. **Reusability**: Services can be used by multiple features
3. **Testability**: Easy to unit test services and components
4. **Maintainability**: Clear organization makes code easy to find and modify
5. **Scalability**: New features can be added without affecting existing code
6. **Enterprise-Ready**: Structure that enterprise teams understand and appreciate

## 🚀 Adding New Features

1. Create a new folder in `src/features/`
2. Add your component(s)
3. Create an `index.ts` file for exports
4. Add to `src/features/index.ts`
5. If you need new API calls, add them to the appropriate service

## 📝 Example: Adding a New Feature

```typescript
// src/features/reports/Reports.tsx
import { useState, useEffect } from 'react'
import { reportService } from '../../services'

export function Reports() {
  // Component logic here
}

// src/features/reports/index.ts
export { Reports } from './Reports'

// src/features/index.ts
export { Reports } from './reports'

// src/services/reportService.ts
export const reportService = {
  async getReports() {
    // API logic here
  }
}
```

This structure keeps everything organized and makes the codebase boring and predictable - exactly what enterprise teams love! 🏢
