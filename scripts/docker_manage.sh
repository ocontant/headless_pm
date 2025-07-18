#!/bin/bash

# Docker Management Script for Headless PM
# Provides easy commands for managing containerized deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="headless-pm"
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if docker-compose is available
check_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        log_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Create required directories
setup_directories() {
    log_info "Creating required directories..."
    mkdir -p database
    mkdir -p projects
    log_success "Directories created"
}

# Show usage information
show_usage() {
    echo "Docker Management Script for Headless PM"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [dev|prod]     Start all services (default: development)"
    echo "  stop                 Stop all services"
    echo "  restart [service]    Restart all services or specific service"
    echo "  status               Show service status"
    echo "  logs [service]       Show logs for all services or specific service"
    echo "  build [service]      Build all images or specific service"
    echo "  clean               Clean up containers, images, and volumes"
    echo "  health              Check service health"
    echo "  backup              Backup database"
    echo "  restore [file]      Restore database from backup"
    echo "  shell [service]     Open shell in running container"
    echo "  reset               Reset all data (WARNING: destructive)"
    echo ""
    echo "Services: api, mcp, dashboard"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start in development mode"
    echo "  $0 start prod         # Start in production mode"
    echo "  $0 logs api           # Show API service logs"
    echo "  $0 restart dashboard  # Restart dashboard service"
    echo "  $0 shell api          # Open shell in API container"
}

# Start services
start_services() {
    local mode=${1:-dev}
    
    check_docker
    check_compose
    setup_directories
    
    log_info "Starting Headless PM services in $mode mode..."
    
    case $mode in
        "prod"|"production")
            docker-compose -f $COMPOSE_FILE -f $PROD_COMPOSE_FILE up -d
            ;;
        "dev"|"development")
            docker-compose -f $COMPOSE_FILE -f $DEV_COMPOSE_FILE up -d
            ;;
        *)
            docker-compose up -d
            ;;
    esac
    
    log_success "Services started successfully"
    log_info "Dashboard: http://localhost:3001"
    log_info "API: http://localhost:6969"
    log_info "MCP: http://localhost:6968"
}

# Stop services
stop_services() {
    log_info "Stopping Headless PM services..."
    docker-compose down
    log_success "Services stopped successfully"
}

# Restart services
restart_services() {
    local service=$1
    
    if [ -n "$service" ]; then
        log_info "Restarting $service service..."
        docker-compose restart "$service"
        log_success "$service service restarted"
    else
        log_info "Restarting all services..."
        docker-compose restart
        log_success "All services restarted"
    fi
}

# Show service status
show_status() {
    log_info "Service status:"
    docker-compose ps
    echo ""
    log_info "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        headless-pm-api headless-pm-mcp headless-pm-dashboard 2>/dev/null || true
}

# Show logs
show_logs() {
    local service=$1
    
    if [ -n "$service" ]; then
        log_info "Showing logs for $service service..."
        docker-compose logs -f "$service"
    else
        log_info "Showing logs for all services..."
        docker-compose logs -f
    fi
}

# Build images
build_images() {
    local service=$1
    
    if [ -n "$service" ]; then
        log_info "Building $service image..."
        docker-compose build "$service"
        log_success "$service image built"
    else
        log_info "Building all images..."
        docker-compose build
        log_success "All images built"
    fi
}

# Clean up
cleanup() {
    log_warning "This will remove all containers, images, and volumes for Headless PM"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Check service health
check_health() {
    log_info "Checking service health..."
    
    services=("headless-pm-api" "headless-pm-mcp" "headless-pm-dashboard")
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            health=$(docker inspect "$service" --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-healthcheck")
            if [ "$health" = "healthy" ]; then
                log_success "$service: healthy"
            elif [ "$health" = "no-healthcheck" ]; then
                log_info "$service: running (no health check)"
            else
                log_warning "$service: $health"
            fi
        else
            log_error "$service: not running"
        fi
    done
}

# Backup database
backup_database() {
    log_info "Creating database backup..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_${timestamp}.db"
    
    if docker cp headless-pm-api:/app/database/headless-pm.db "./$backup_file" 2>/dev/null; then
        log_success "Database backed up to $backup_file"
    else
        log_error "Failed to backup database. Is the API container running?"
        exit 1
    fi
}

# Restore database
restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Please specify backup file to restore"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file $backup_file not found"
        exit 1
    fi
    
    log_warning "This will replace the current database"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restoring database from $backup_file..."
        docker cp "$backup_file" headless-pm-api:/app/database/headless-pm.db
        docker-compose restart api
        log_success "Database restored successfully"
    else
        log_info "Restore cancelled"
    fi
}

# Open shell in container
open_shell() {
    local service=${1:-api}
    local container="headless-pm-$service"
    
    log_info "Opening shell in $service container..."
    
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        docker exec -it "$container" /bin/bash
    else
        log_error "$service container is not running"
        exit 1
    fi
}

# Reset all data
reset_data() {
    log_warning "This will DELETE ALL DATA including database and projects"
    read -p "Are you sure? Type 'DELETE' to confirm: " confirmation
    
    if [ "$confirmation" = "DELETE" ]; then
        log_info "Resetting all data..."
        docker-compose down -v
        rm -rf database/* projects/*
        setup_directories
        docker-compose up -d
        log_success "Data reset completed"
    else
        log_info "Reset cancelled"
    fi
}

# Main command handler
case "${1:-}" in
    "start")
        start_services "$2"
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services "$2"
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "build")
        build_images "$2"
        ;;
    "clean")
        cleanup
        ;;
    "health")
        check_health
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        restore_database "$2"
        ;;
    "shell")
        open_shell "$2"
        ;;
    "reset")
        reset_data
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        echo ""
        show_usage
        exit 1
        ;;
esac