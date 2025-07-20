#!/bin/bash

# Headless PM Service Management - Start Services
# Utilise pidfiles pour surveiller les processus
# Compatible avec la configuration existante

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

# Create pids directory if it doesn't exist
mkdir -p "$PIDS_DIR"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    log_success "Environment variables loaded from .env"
else
    log_error "No .env file found in $PROJECT_ROOT"
    log_info "Please create .env file from env-example first"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Detect architecture and virtual environment
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    EXPECTED_VENV="venv"
else
    EXPECTED_VENV="claude_venv"
fi

log_info "Starting Headless PM Services"
echo "==============================="

# Check virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    log_success "Virtual environment active: $VIRTUAL_ENV"
else
    log_warning "No virtual environment detected!"
    log_info "Trying to activate $EXPECTED_VENV..."
    if [ -d "$EXPECTED_VENV" ]; then
        source "$EXPECTED_VENV/bin/activate"
        log_success "Activated $EXPECTED_VENV"
    else
        log_error "Virtual environment $EXPECTED_VENV not found"
        log_info "Please run: ./setup/universal_setup.sh"
        exit 1
    fi
fi

# Function to check if service is already running via health endpoint
is_service_healthy() {
    local service_name=$1
    local health_url=$2
    
    if [ -z "$health_url" ]; then
        return 1  # No health URL provided, assume not healthy
    fi
    
    # Check if service responds to health endpoint
    if curl -s -f "$health_url" >/dev/null 2>&1; then
        return 0  # Service is healthy
    else
        return 1  # Service not healthy or not responding
    fi
}

# Function to check if service is already running via pidfile
is_service_running() {
    local service_name=$1
    local pidfile="$PIDS_DIR/${service_name}.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            return 0  # Service is running
        else
            # Stale pidfile, remove it
            rm -f "$pidfile"
            return 1  # Service not running
        fi
    fi
    return 1  # No pidfile, service not running
}

# Function to start a service with pidfile
start_service() {
    local service_name=$1
    local service_command=$2
    local service_port=$3
    local service_description=$4
    local health_url=$5
    
    local pidfile="$PIDS_DIR/${service_name}.pid"
    local logfile="$PIDS_DIR/${service_name}.log"
    
    # First check if service is already healthy via health endpoint
    if [ ! -z "$health_url" ] && is_service_healthy "$service_name" "$health_url"; then
        log_success "$service_description is already running and healthy"
        log_info "Health check: $health_url ✅"
        return 0
    fi
    
    # Check if service is running via pidfile
    if is_service_running "$service_name"; then
        local pid=$(cat "$pidfile")
        log_warning "$service_description already running (PID: $pid) but health check failed"
        log_info "You may want to restart this service"
        return 0
    fi
    
    # Check if port is available (if provided)
    if [ ! -z "$service_port" ]; then
        if lsof -i ":$service_port" >/dev/null 2>&1; then
            log_error "Port $service_port is already in use for $service_description"
            log_info "Another process may be using this port. Try stopping existing services first."
            return 1
        fi
    fi
    
    log_info "Starting $service_description..."
    
    # Start the service in background and capture PID
    # Ensure virtual environment is activated in the service command
    local full_command="source $PROJECT_ROOT/$EXPECTED_VENV/bin/activate && $service_command"
    nohup bash -c "$full_command" > "$logfile" 2>&1 &
    local pid=$!
    
    # Save PID to file
    echo "$pid" > "$pidfile"
    
    # Wait a moment to check if service started successfully
    sleep 2
    
    if kill -0 "$pid" 2>/dev/null; then
        log_success "$service_description started successfully (PID: $pid)"
        if [ ! -z "$service_port" ]; then
            log_info "Service available on port $service_port"
        fi
        return 0
    else
        log_error "$service_description failed to start"
        rm -f "$pidfile"
        log_info "Check log file: $logfile"
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local check_url=$2
    local max_attempts=30
    local attempt=1
    
    if [ -z "$check_url" ]; then
        return 0  # Skip health check if no URL provided
    fi
    
    log_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$check_url" >/dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_warning "$service_name health check timeout"
    return 1
}

# Start services based on configuration

# 1. API Server (always start if SERVICE_PORT is defined or default)
if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
    PORT=${SERVICE_PORT:-6969}
    start_service "api" \
        "uvicorn src.main:app --reload --port $PORT --host 0.0.0.0" \
        "$PORT" \
        "API Server" \
        "http://localhost:$PORT/health"
    
    if [ $? -eq 0 ]; then
        wait_for_service "api" "http://localhost:$PORT/health"
        log_info "API Documentation: http://localhost:$PORT/api/v1/docs"
    fi
else
    log_info "SERVICE_PORT not defined, skipping API server"
fi

# 2. MCP Server (if MCP_PORT is defined)
if [ ! -z "$MCP_PORT" ]; then
    start_service "mcp" \
        "uvicorn src.mcp.simple_sse_server:app --port $MCP_PORT --host 0.0.0.0" \
        "$MCP_PORT" \
        "MCP SSE Server" \
        "http://localhost:$MCP_PORT/health"
    
    if [ $? -eq 0 ]; then
        wait_for_service "mcp" "http://localhost:$MCP_PORT/health"
        log_info "MCP Server: http://localhost:$MCP_PORT"
    fi
else
    log_info "MCP_PORT not defined, skipping MCP server"
fi

# 3. Dashboard (if DASHBOARD_PORT is defined and Node.js available)
if [ ! -z "$DASHBOARD_PORT" ]; then
    if command -v node >/dev/null 2>&1; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge 18 ] && [ -d "dashboard" ]; then
            # Check if dependencies are installed
            if [ ! -d "dashboard/node_modules" ]; then
                log_info "Installing dashboard dependencies..."
                cd dashboard && npm install >/dev/null 2>&1 && cd ..
            fi
            
            start_service "dashboard" \
                "cd dashboard && npx next dev --port $DASHBOARD_PORT --turbopack" \
                "$DASHBOARD_PORT" \
                "Web Dashboard" \
                "http://localhost:$DASHBOARD_PORT/health"
            
            if [ $? -eq 0 ]; then
                wait_for_service "dashboard" "http://localhost:$DASHBOARD_PORT/health"
                log_info "Web Dashboard: http://localhost:$DASHBOARD_PORT"
            fi
        else
            log_warning "Node.js 18+ required for dashboard or dashboard directory missing"
        fi
    else
        log_warning "Node.js not found, skipping dashboard"
    fi
else
    log_info "DASHBOARD_PORT not defined, skipping dashboard"
fi

# Show summary
echo ""
echo -e "${GREEN}🌟 Service Startup Complete!${NC}"
echo "==============================="

# List running services
running_services=0
healthy_services=0
for service in api mcp dashboard; do
    # First check if service is healthy
    case $service in
        api)
            health_url="http://localhost:${SERVICE_PORT:-6969}/health"
            ;;
        mcp)
            health_url="http://localhost:${MCP_PORT}/health"
            ;;
        dashboard)
            health_url="http://localhost:${DASHBOARD_PORT}/health"
            ;;
        *)
            health_url=""
            ;;
    esac
    
    if [ ! -z "$health_url" ] && is_service_healthy "$service" "$health_url"; then
        log_success "$service is healthy and responsive"
        healthy_services=$((healthy_services + 1))
    elif is_service_running "$service"; then
        pid=$(cat "$PIDS_DIR/${service}.pid")
        log_success "$service running (PID: $pid)"
        running_services=$((running_services + 1))
    fi
done

total_services=$((running_services + healthy_services))
if [ $total_services -eq 0 ]; then
    log_warning "No services found running. Check your .env configuration."
    exit 1
else
    echo ""
    log_info "Use './scripts/check_services.sh' to monitor services"
    log_info "Use './scripts/stop_services.sh' to stop all services"
    echo ""
    log_info "PID files stored in: $PIDS_DIR"
    log_info "Log files stored in: $PIDS_DIR"
fi