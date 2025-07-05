#!/bin/bash
# Docker management script for Rebecca

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build all services
build_services() {
    print_status "Building all services..."
    docker-compose build --no-cache
    print_success "All services built successfully!"
}

# Function to start all services
start_services() {
    print_status "Starting all services..."
    docker-compose up -d
    print_success "All services started!"
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    print_status "Checking service health..."
    
    # Check OpenFGA
    if curl -f http://localhost:8080/healthz > /dev/null 2>&1; then
        print_success "OpenFGA is healthy"
    else
        print_warning "OpenFGA may not be ready yet"
    fi
    
    # Check Backend
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Backend API is healthy"
    else
        print_warning "Backend API may not be ready yet"
    fi
    
    # Check Frontend
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend may not be ready yet"
    fi
    
    echo ""
    print_success "🚀 Rebecca is now running!"
    echo ""
    echo "  📱 Frontend:    http://localhost"
    echo "  🔧 Backend API: http://localhost:5000"
    echo "  🔐 OpenFGA:     http://localhost:8080"
    echo "  🎮 OpenFGA UI:  http://localhost:3000"
    echo ""
}

# Function to stop all services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped!"
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose logs -f
    else
        print_status "Showing logs for $1..."
        docker-compose logs -f "$1"
    fi
}

# Function to restart services
restart_services() {
    print_status "Restarting all services..."
    docker-compose restart
    print_success "All services restarted!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
}

# Main script logic
case "$1" in
    build)
        check_docker
        build_services
        ;;
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    logs)
        check_docker
        show_logs "$2"
        ;;
    status)
        check_docker
        show_status
        ;;
    clean)
        check_docker
        cleanup
        ;;
    dev)
        check_docker
        print_status "Starting development environment..."
        build_services
        start_services
        ;;
    *)
        echo "Usage: $0 {build|start|stop|restart|logs|status|clean|dev}"
        echo ""
        echo "Commands:"
        echo "  build    - Build all Docker images"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show logs (optional: specify service name)"
        echo "  status   - Show service status"
        echo "  clean    - Clean up Docker resources"
        echo "  dev      - Build and start development environment"
        echo ""
        echo "Examples:"
        echo "  $0 dev                 # Start development environment"
        echo "  $0 logs backend        # Show backend logs"
        echo "  $0 logs frontend       # Show frontend logs"
        echo "  $0 logs openfga        # Show OpenFGA logs"
        exit 1
        ;;
esac
