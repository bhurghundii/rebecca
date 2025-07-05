# Rebecca - Docker Deployment Guide

This guide explains how to run the complete Rebecca application stack using Docker, including the frontend, backend, and OpenFGA authorization service.

## 🏗️ Architecture

The Docker setup includes three main services:

- **Frontend**: React/TypeScript web application (port 80)
- **Backend**: Flask API server (port 5000)
- **OpenFGA**: Authorization service (ports 8080, 8081, 3000)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- At least 4GB RAM available for containers

### 1. Clone and Setup

```bash
git clone <repository-url>
cd rebecca
```

### 2. Start the Application

Use the provided management script:

```bash
# Start the complete development environment
./docker-manage.sh dev
```

Or use Docker Compose directly:

```bash
# Build and start all services
docker-compose up --build
```

### 3. Access the Application

Once all services are running:

- 🖥️ **Frontend**: http://localhost
- 🔧 **Backend API**: http://localhost:5000
- 🔐 **OpenFGA API**: http://localhost:8080
- 🎮 **OpenFGA Playground**: http://localhost:3000

## 📋 Management Commands

The `docker-manage.sh` script provides easy management:

```bash
# Build all Docker images
./docker-manage.sh build

# Start all services
./docker-manage.sh start

# Stop all services
./docker-manage.sh stop

# Restart all services
./docker-manage.sh restart

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
```

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration:

#### Development (.env)
```env
FLASK_ENV=development
PORT=5000
OPENFGA_API_URL=http://localhost:8080
VITE_API_URL=http://localhost:5000
DATABASE_PATH=./rebecca.db
```

#### Production (.env.production)
```env
FLASK_ENV=production
PORT=5000
OPENFGA_API_URL=http://openfga:8080
VITE_API_URL=http://backend:5000
DATABASE_PATH=/app/rebecca.db
```

### Custom Configuration

You can override default settings by creating a `.env.local` file:

```env
# Custom API URL for development
VITE_API_URL=http://localhost:3001

# Custom OpenFGA URL
OPENFGA_API_URL=http://my-openfga:8080
```

## 🐳 Docker Services

### Frontend Service
- **Image**: Custom React/TypeScript build
- **Port**: 80
- **Technology**: Vite + React + TypeScript + Tailwind CSS
- **Nginx**: Serves static files and proxies API requests

### Backend Service
- **Image**: Custom Python Flask build
- **Port**: 5000
- **Technology**: Flask + SQLite + OpenFGA integration
- **Health Check**: `/health` endpoint

### OpenFGA Service
- **Image**: `openfga/openfga:latest`
- **Ports**: 8080 (API), 8081 (gRPC), 3000 (Playground)
- **Storage**: In-memory (for development)
- **Features**: Authorization service with playground UI

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :80
   lsof -i :5000
   lsof -i :8080
   
   # Kill process if needed
   kill -9 <PID>
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
   - Check that backend service is healthy: `curl http://localhost:5000/health`
   - Verify environment variables are set correctly
   - Check Docker network connectivity

### Health Checks

```bash
# Check OpenFGA
curl http://localhost:8080/healthz

# Check Backend
curl http://localhost:5000/health

# Check Frontend
curl http://localhost:80
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f openfga

# View container status
docker-compose ps
```

## 🚢 Production Deployment

### Using Docker Compose

1. **Update environment file**:
   ```bash
   cp .env.production .env
   ```

2. **Build and deploy**:
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

### Environment-Specific Overrides

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'
services:
  backend:
    environment:
      - FLASK_ENV=development
    ports:
      - "5001:5000"  # Custom port mapping
```

## 🔐 Security Considerations

### Production Security

1. **Environment Variables**: Use Docker secrets or external secret management
2. **Network Security**: Use custom Docker networks
3. **SSL/TLS**: Add reverse proxy with SSL certificates
4. **Database**: Use persistent volumes for production data
5. **OpenFGA**: Configure with persistent storage and proper authentication

### Development Security

- Default configuration uses in-memory storage
- No authentication required for development
- All services run with development settings

## 📊 Performance

### Resource Usage

- **Frontend**: ~50MB RAM, minimal CPU
- **Backend**: ~100MB RAM, moderate CPU
- **OpenFGA**: ~200MB RAM, moderate CPU

### Scaling

For production scaling:
1. Use multiple backend replicas
2. Add load balancer (nginx/traefik)
3. Use external database (PostgreSQL)
4. Configure OpenFGA with persistent storage

## 🔄 Updates and Maintenance

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
./docker-manage.sh build

# Restart with new images
./docker-manage.sh restart
```

### Backup and Recovery

```bash
# Backup database
docker-compose exec backend cp /app/rebecca.db /backup/

# Restore database
docker-compose exec backend cp /backup/rebecca.db /app/
```

## 🎯 Development Workflow

### Local Development

1. **Start services**: `./docker-manage.sh dev`
2. **View logs**: `./docker-manage.sh logs`
3. **Make changes**: Edit code in host filesystem
4. **Rebuild**: `./docker-manage.sh build` (if needed)
5. **Test**: Access application at http://localhost

### Testing

```bash
# Run backend tests
docker-compose exec backend python -m pytest

# Run frontend tests
docker-compose exec frontend npm test
```

### Hot Reload

For development with hot reload:
1. Use volume mounts for source code
2. Configure development servers appropriately
3. Use nodemon/watchdog for automatic restarts

## 🆘 Support

For issues and questions:
1. Check the logs: `./docker-manage.sh logs`
2. Verify service health: `./docker-manage.sh status`
3. Clean and restart: `./docker-manage.sh clean && ./docker-manage.sh dev`
4. Check Docker resources: `docker system df`

## 📋 Checklist

Before deploying:
- [ ] Docker Desktop is running
- [ ] All ports are available (80, 5000, 8080, 3000)
- [ ] Environment variables are configured
- [ ] Database is accessible
- [ ] Network connectivity is working
- [ ] Health checks are passing
