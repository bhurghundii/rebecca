# Rebecca API Dashboard

A simple, enterprise-friendly React frontend for the Rebecca API authorization system.

## Features

- 📊 **Dashboard** - Overview of users, resources, relationships, and groups
- 👥 **User Management** - Create and view users
- 👫 **User Groups** - Create and manage user groups (collections of users)
- 📁 **Resource Management** - Create and manage resources
- 📚 **Resource Groups** - Create and manage resource groups (collections of resources)
- 🔗 **Relationship Management** - Create user-resource relationships
- 🔒 **Permission Checker** - Test authorization permissions in real-time

## Tech Stack

- **React 19** with TypeScript
- **Vite** for build tooling
- **React Router** for navigation
- **Axios** for API calls
- **Vanilla CSS** (no fancy frameworks)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker Deployment

```bash
# Build the Docker image
docker build -t rebecca-ui .

# Run the container
docker run -p 3000:80 rebecca-ui
```

## API Configuration

The frontend expects the Rebecca API to be running at `http://localhost:8000`.

To change this, update the `API_BASE_URL` constant in `src/services/api.ts`.

## Enterprise Features

- ✅ Clean, boring UI that IT departments love
- ✅ No build complexity - just `npm run build`
- ✅ Static file deployment (works anywhere)
- ✅ Docker ready
- ✅ Responsive design
- ✅ Error handling
- ✅ Loading states
- ✅ Group management for scalable permissions

## Project Structure

```
src/
├── features/           # React components organized by feature
│   ├── dashboard/     # Main dashboard with stats
│   ├── users/         # User management
│   ├── user-groups/   # User group management
│   ├── resources/     # Resource management
│   ├── resource-groups/ # Resource group management
│   ├── relationships/ # Relationship management
│   └── permissions/   # Permission testing
├── services/          # API layer (all HTTP calls)
│   ├── api.ts        # Base API configuration
│   ├── userService.ts # User operations
│   ├── userGroupService.ts # User group operations
│   ├── resourceService.ts # Resource operations
│   ├── resourceGroupService.ts # Resource group operations
│   ├── relationshipService.ts # Relationship operations
│   └── healthService.ts # Health checks
├── types/             # TypeScript definitions
│   └── api.ts        # API-related types
├── App.tsx           # Main app component
├── App.css           # Styling
└── main.tsx          # Entry point
```

## User & Resource Groups

### User Groups
- Create groups of users (e.g., "Engineering Team", "Marketing Team")
- Easily manage permissions for entire teams
- Visual interface to select users and see group membership

### Resource Groups  
- Create groups of resources (e.g., "Project Documents", "System Files")
- Apply permissions to entire groups of resources
- Filter and select resources by type and metadata

This is designed to be the most boring, reliable frontend possible. Perfect for enterprise use! 🏢
