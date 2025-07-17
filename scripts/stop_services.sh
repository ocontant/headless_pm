#!/bin/bash

# Headless PM Service Management - Stop Services
# Arrête tous les services et nettoie les pidfiles

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PIDS_DIR="$PROJECT_ROOT/run"

log_info "Stopping Headless PM Services"
echo "=============================="

# Check if pids directory exists
if [ ! -d "$PIDS_DIR" ]; then
    log_warning "No PID directory found ($PIDS_DIR)"
    log_info "Services may not be running or were started manually"
    exit 0
fi

# Function to check if process is running
is_process_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local pidfile="$PIDS_DIR/${service_name}.pid"
    local logfile="$PIDS_DIR/${service_name}.log"
    
    if [ ! -f "$pidfile" ]; then
        log_info "$service_name: No PID file found"
        return 0
    fi
    
    local pid=$(cat "$pidfile")
    
    if ! is_process_running "$pid"; then
        log_warning "$service_name: Process not running (stale PID: $pid)"
        rm -f "$pidfile"
        return 0
    fi
    
    log_info "Stopping $service_name (PID: $pid)..."
    
    # Try graceful shutdown first (SIGTERM)
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local attempts=0
    local max_attempts=15
    while [ $attempts -lt $max_attempts ]; do
        if ! is_process_running "$pid"; then
            log_success "$service_name stopped gracefully"
            rm -f "$pidfile"
            return 0
        fi
        sleep 1
        attempts=$((attempts + 1))
        echo -n "."
    done
    
    echo ""
    log_warning "$service_name did not stop gracefully, forcing shutdown..."
    
    # Force kill (SIGKILL)
    kill -9 "$pid" 2>/dev/null || true
    
    # Wait a bit more
    sleep 2
    
    if ! is_process_running "$pid"; then
        log_success "$service_name forcefully stopped"
        rm -f "$pidfile"
        return 0
    else
        log_error "Failed to stop $service_name (PID: $pid)"
        return 1
    fi
}

# Function to stop service by name with additional cleanup
stop_service_extended() {
    local service_name=$1
    local service_description=$2
    local extra_cleanup=$3
    
    log_info "Stopping $service_description..."
    
    stop_service "$service_name"
    local result=$?
    
    # Run extra cleanup if provided
    if [ ! -z "$extra_cleanup" ] && [ $result -eq 0 ]; then
        eval "$extra_cleanup"
    fi
    
    return $result
}

# Parse command line arguments
FORCE=false
SPECIFIC_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE=true
            shift
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -f, --force     Force kill processes immediately"
            echo "  -s, --service   Stop specific service (api|mcp|dashboard)"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Stop all services gracefully"
            echo "  $0 --force           # Force stop all services"
            echo "  $0 --service api     # Stop only API service"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Override graceful shutdown if force is requested
if [ "$FORCE" = true ]; then
    log_warning "Force mode enabled - will use SIGKILL immediately"
fi

# List of services to stop
SERVICES=("api" "mcp" "dashboard")

# If specific service requested, only stop that one
if [ ! -z "$SPECIFIC_SERVICE" ]; then
    case "$SPECIFIC_SERVICE" in
        api|mcp|dashboard)
            SERVICES=("$SPECIFIC_SERVICE")
            ;;
        *)
            log_error "Unknown service: $SPECIFIC_SERVICE"
            log_info "Available services: api, mcp, dashboard"
            exit 1
            ;;
    esac
fi

# Stop services
stopped_count=0
failed_count=0

for service in "${SERVICES[@]}"; do
    case "$service" in
        "api")
            stop_service_extended "api" "API Server"
            ;;
        "mcp")
            stop_service_extended "mcp" "MCP SSE Server"
            ;;
        "dashboard")
            # Dashboard might have Node.js processes, clean them up
            stop_service_extended "dashboard" "Web Dashboard" \
                "pkill -f 'next dev' 2>/dev/null || true"
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        stopped_count=$((stopped_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
done

# Clean up any remaining Node.js processes related to the dashboard
if [ -z "$SPECIFIC_SERVICE" ] || [ "$SPECIFIC_SERVICE" = "dashboard" ]; then
    log_info "Cleaning up any remaining Node.js processes..."
    pkill -f "next dev.*$DASHBOARD_PORT" 2>/dev/null || true
    pkill -f "dashboard.*turbopack" 2>/dev/null || true
fi

# Clean up any orphaned processes by port
if [ -z "$SPECIFIC_SERVICE" ]; then
    log_info "Checking for processes on configured ports..."
    
    # Load environment to get ports
    if [ -f "$PROJECT_ROOT/.env" ]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
        
        # Kill processes on our ports if they exist
        for port in "$SERVICE_PORT" "$MCP_PORT" "$DASHBOARD_PORT"; do
            if [ ! -z "$port" ]; then
                pids=$(lsof -t -i:$port 2>/dev/null || true)
                if [ ! -z "$pids" ]; then
                    log_warning "Found processes on port $port, cleaning up..."
                    echo "$pids" | xargs kill 2>/dev/null || true
                fi
            fi
        done
    fi
fi

# Summary
echo ""
echo -e "${GREEN}🛑 Service Shutdown Complete!${NC}"
echo "=============================="

if [ $stopped_count -gt 0 ]; then
    log_success "Successfully stopped $stopped_count service(s)"
fi

if [ $failed_count -gt 0 ]; then
    log_error "Failed to stop $failed_count service(s)"
fi

# Clean up empty run directory
if [ -d "$PIDS_DIR" ]; then
    # Remove any remaining empty log files
    find "$PIDS_DIR" -name "*.log" -size 0 -delete 2>/dev/null || true
    
    # If directory is empty, suggest removing it
    if [ -z "$(ls -A $PIDS_DIR 2>/dev/null)" ]; then
        log_info "Removing empty run directory"
        rmdir "$PIDS_DIR" 2>/dev/null || true
    else
        log_info "Log files preserved in: $PIDS_DIR"
    fi
fi

# Exit with appropriate code
if [ $failed_count -gt 0 ]; then
    exit 1
else
    exit 0
fi