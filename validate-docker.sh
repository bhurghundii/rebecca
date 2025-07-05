#!/bin/bash
# Simple validation script for Docker setup

echo "🔍 Validating Docker setup..."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

# Check if Dockerfiles exist
if [ ! -f "back-end/Dockerfile" ]; then
    echo "❌ back-end/Dockerfile not found"
    exit 1
fi

if [ ! -f "front-end/Dockerfile" ]; then
    echo "❌ front-end/Dockerfile not found"
    exit 1
fi

# Check if required files exist
if [ ! -f "back-end/requirements.txt" ]; then
    echo "❌ back-end/requirements.txt not found"
    exit 1
fi

if [ ! -f "front-end/package.json" ]; then
    echo "❌ front-end/package.json not found"
    exit 1
fi

# Check if management script exists and is executable
if [ ! -x "docker-manage.sh" ]; then
    echo "❌ docker-manage.sh not found or not executable"
    exit 1
fi

echo "✅ All required files found"
echo "✅ Docker setup validation passed"
echo ""
echo "To start the application:"
echo "  1. Make sure Docker Desktop is running"
echo "  2. Run: ./docker-manage.sh dev"
echo ""
echo "Services will be available at:"
echo "  - Frontend: http://localhost"
echo "  - Backend: http://localhost:5000"
echo "  - OpenFGA: http://localhost:8080"
echo "  - OpenFGA Playground: http://localhost:3000"
