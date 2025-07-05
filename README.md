# Rebecca
Open-source user management platform with fine-grained authorization

## What is Rebecca?

Rebecca is a plug-and-play user management platform you can drop into your internal network to provide user management services to your internal applications. 

Rebecca comes with a modern React UI which allows product owners and developers to create and manage authorization models that map their business needs.

Backed by OpenFGA, it provides ReBAC (Relationship-Based Access Control) modeling with an intuitive UI to help you manage common use cases such as managing group permissions, resource access, and row-level permissions.

## 🏗️ Architecture

Rebecca consists of three main components:

- **Frontend**: React/TypeScript web application with Tailwind CSS (Port 80)
- **Backend**: Flask API server with SQLite database (Port 5000)
- **OpenFGA**: Authorization service with playground UI (Ports 8080, 8081, 3000)

## 🚀 Quick Start with Docker

### Prerequisites
- Docker Desktop installed and running
- Git installed
- At least 4GB RAM available for containers

### 1. Clone the Repository
```bash
git clone https://github.com/bhurghundii/rebecca.git
cd rebecca
```

### 2. Start the Application
```bash
# Start the complete development environment
./docker-manage.sh dev
```

### 3. Access Rebecca
Once all services are running, access the application at:

- 🖥️ **Frontend**: http://localhost
- 🔧 **Backend API**: http://localhost:5000
- 🔐 **OpenFGA API**: http://localhost:8080
- 🎮 **OpenFGA Playground**: http://localhost:3000

## 🛠️ Docker Management Commands

The included `docker-manage.sh` script provides easy management:

```bash
# Build all Docker images
./docker-manage.sh build

# Start all services
./docker-manage.sh start

# Stop all services
./docker-manage.sh stop

# View logs for all services
./docker-manage.sh logs

# View logs for a specific service
./docker-manage.sh logs backend
./docker-manage.sh logs frontend
./docker-manage.sh logs openfga

# Check service status
./docker-manage.sh status

# Clean up Docker resources
./docker-manage.sh clean

# Full development setup (build + start)
./docker-manage.sh dev
```

## 🔧 Manual Docker Setup

If you prefer to use Docker Compose directly:

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

## 🌐 Service Endpoints

### Frontend Application
- **URL**: http://localhost
- **Features**: User management, resource groups, permissions management
- **Technology**: React 19 + TypeScript + Vite + Tailwind CSS

### Backend API
- **URL**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **Swagger Documentation**: Available in `/swagger.yaml`
- **Technology**: Flask + SQLite + OpenFGA integration

### OpenFGA Authorization
- **API**: http://localhost:8080
- **Playground**: http://localhost:3000
- **Health Check**: http://localhost:8080/healthz
- **Purpose**: Fine-grained authorization service

## 📋 API Endpoints

The Rebecca API provides comprehensive endpoints for:

- **Users**: Create, read, update, delete users
- **Resources**: Manage application resources
- **Resource Groups**: Organize resources into logical groups
- **User Groups**: Create and manage user groups
- **Relationships**: Define fine-grained permissions
- **Authorization**: Check user permissions

Check out the `swagger.yaml` file for detailed API documentation.

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :80
   lsof -i :5000
   lsof -i :8080
   
   # Stop the conflicting service or change ports in docker-compose.yml
   ```

2. **Services Not Starting**
   ```bash
   # Check service logs
   ./docker-manage.sh logs
   
   # Check specific service
   ./docker-manage.sh logs backend
   ```

3. **Database Issues**
   ```bash
   # Clean up and restart
   ./docker-manage.sh clean
   ./docker-manage.sh dev
   ```

4. **Frontend Can't Connect to Backend**
   - Verify backend service is healthy: `curl http://localhost:5000/health`
   - Check Docker network connectivity
   - Ensure all services are running: `./docker-manage.sh status`

### Health Checks

```bash
# Check all services
curl http://localhost:80           # Frontend
curl http://localhost:5000/health  # Backend
curl http://localhost:8080/healthz # OpenFGA
```

## 🛡️ Security Features

- **CORS**: Properly configured for cross-origin requests
- **Container Isolation**: Services run in isolated Docker containers
- **Fine-grained Authorization**: OpenFGA-powered permission system
- **Environment-based Configuration**: Secure configuration management
- **Health Monitoring**: Built-in health checks for all services

## 🔄 Development Workflow

### Making Changes

1. **Edit Code**: Make changes to frontend or backend code
2. **Rebuild**: `./docker-manage.sh build` (if needed)
3. **Test**: Services automatically reload in development mode
4. **Deploy**: Use production environment settings

### Running Tests

```bash
# Backend tests
docker-compose exec backend python -m pytest

# Check test coverage
docker-compose exec backend python -m pytest --cov
```

## 📚 Documentation

- **`DOCKER_README.md`**: Comprehensive Docker deployment guide
- **`DOCKER_SETUP_SUMMARY.md`**: Technical implementation details
- **`swagger.yaml`**: API documentation
- **`back-end/README.md`**: Backend-specific documentation
- **`front-end/README.md`**: Frontend-specific documentation

## 🎯 Use Cases

Rebecca is perfect for:

- **Internal Applications**: Drop-in user management for internal tools
- **Multi-tenant Applications**: Manage users across different organizations
- **Fine-grained Permissions**: Complex authorization requirements
- **Resource Management**: Control access to documents, projects, and data
- **Group-based Access**: Manage permissions through user and resource groups

## 🚢 Production Deployment

For production deployment:

1. **Update Environment**: Copy `.env.production` to `.env`
2. **Configure Database**: Use PostgreSQL or MySQL for production
3. **Set Up SSL**: Configure reverse proxy with SSL certificates
4. **Scale Services**: Use Docker Swarm or Kubernetes for scaling
5. **Monitor**: Set up logging and monitoring solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using `./docker-manage.sh dev`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Check the `/docs` directory for detailed guides
- **Community**: Join our discussions for help and feedback

---

**Get started in 2 minutes**: `git clone <repo> && cd rebecca && ./docker-manage.sh dev` 