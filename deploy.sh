#!/bin/bash

# GC Estimator Deployment Script
set -e

echo "🚀 GC Estimator Deployment Script"
echo "=================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to build images
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    echo "✅ Images built successfully"
}

# Function to start services
start_services() {
    echo "🚀 Starting services..."
    docker-compose up -d
    echo "✅ Services started"
}

# Function to check service health
check_health() {
    echo "🏥 Checking service health..."
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is responding"
    else
        echo "❌ Frontend is not responding"
        return 1
    fi
    
    echo "✅ All services are healthy!"
}

# Function to show service status
show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
}

# Function to show logs
show_logs() {
    echo "📋 Recent logs:"
    docker-compose logs --tail=20
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped"
}

# Function to clean up
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down -v --rmi all --remove-orphans
    docker system prune -f
    echo "✅ Cleanup complete"
}

# Main deployment function
deploy() {
    check_docker
    build_images
    start_services
    check_health
    show_status
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "build")
        check_docker
        build_images
        ;;
    "start")
        check_docker
        start_services
        check_health
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        check_health
        show_status
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "cleanup")
        cleanup
        ;;
    "dev")
        echo "🔧 Starting development mode..."
        docker-compose up --build
        ;;
    "prod")
        echo "🏭 Starting production mode..."
        docker-compose -f docker-compose.yml up --build -d
        check_health
        show_status
        ;;
    *)
        echo "Usage: $0 {deploy|build|start|stop|restart|status|logs|cleanup|dev|prod}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Build and start all services (default)"
        echo "  build    - Build Docker images only"
        echo "  start    - Start services"
        echo "  stop     - Stop services"
        echo "  restart  - Restart services"
        echo "  status   - Show service status"
        echo "  logs     - Show recent logs"
        echo "  cleanup  - Stop and remove everything"
        echo "  dev      - Start development mode with hot reload"
        echo "  prod     - Start production mode"
        exit 1
        ;;
esac
