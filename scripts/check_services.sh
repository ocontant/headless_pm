#!/bin/bash

# Headless PM Service Management - Check Services
# Vérifie l'état des services et leur santé

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_status() {
    echo -e "${CYAN}📊 $1${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PIDS_DIR="$PROJECT_ROOT/run"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    log_warning "No .env file found, using defaults"
fi

# Function to check if process is running
is_process_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

# Function to get process info
get_process_info() {
    local pid=$1
    if is_process_running "$pid"; then
        ps -p "$pid" -o pid,ppid,etime,pcpu,pmem,cmd --no-headers | head -1
    else
        echo "Process not found"
    fi
}

# Function to check service health via HTTP
check_service_health() {
    local service_name=$1
    local health_url=$2
    local timeout=${3:-5}
    
    if [ -z "$health_url" ]; then
        echo "N/A"
        return 2
    fi
    
    # Use timeout command to ensure non-blocking behavior
    local response=$(timeout "$timeout" curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$timeout" "$health_url" 2>/dev/null || echo "000")
    
    case "$response" in
        200|204)
            echo "HEALTHY"
            return 0
            ;;
        000)
            echo "UNREACHABLE"
            return 1
            ;;
        *)
            echo "UNHEALTHY ($response)"
            return 1
            ;;
    esac
}

# Function to get detailed health info (non-blocking)
get_service_health_details() {
    local service_name=$1
    local health_url=$2
    local timeout=${3:-5}
    
    if [ -z "$health_url" ]; then
        echo "N/A"
        return 2
    fi
    
    # Use timeout command and get JSON response
    local response=$(timeout "$timeout" curl -s --connect-timeout "$timeout" "$health_url" 2>/dev/null || echo '{"error": "timeout"}')
    
    # Check if response is valid JSON
    if echo "$response" | jq . >/dev/null 2>&1; then
        echo "$response"
        return 0
    else
        echo '{"error": "invalid_response", "raw": "'$response'"}'
        return 1
    fi
}

# Function to test multiple health endpoints quickly
test_all_health_endpoints() {
    local api_port=${SERVICE_PORT:-6969}
    local mcp_port=${MCP_PORT:-6968}
    local dashboard_port=${DASHBOARD_PORT:-3001}
    
    echo -e "${CYAN}🔍 Quick Health Check Results${NC}"
    echo "=================================="
    
    # Test all endpoints in parallel using background processes
    {
        if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
            api_status=$(check_service_health "api" "http://localhost:$api_port/health" 3)
            echo "API Server:      $api_status"
        fi
    } &
    
    {
        if [ ! -z "$MCP_PORT" ]; then
            mcp_status=$(check_service_health "mcp" "http://localhost:$mcp_port/health" 3)
            echo "MCP Server:      $mcp_status"
        fi
    } &
    
    {
        if [ ! -z "$DASHBOARD_PORT" ]; then
            dashboard_status=$(check_service_health "dashboard" "http://localhost:$dashboard_port/api/health" 3)
            echo "Dashboard:       $dashboard_status"
        fi
    } &
    
    # Wait for all background jobs to complete
    wait
    
    echo ""
}

# Function to get service port status
check_port_status() {
    local port=$1
    
    if [ -z "$port" ]; then
        echo "N/A"
        return 2
    fi
    
    if lsof -i ":$port" >/dev/null 2>&1; then
        echo "LISTENING"
        return 0
    else
        echo "CLOSED"
        return 1
    fi
}

# Function to get log file size and recent errors
get_log_info() {
    local logfile=$1
    
    if [ ! -f "$logfile" ]; then
        echo "No log file"
        return
    fi
    
    local size=$(du -h "$logfile" 2>/dev/null | cut -f1)
    local errors=$(grep -i "error\|exception\|failed\|traceback" "$logfile" 2>/dev/null | wc -l)
    local recent_errors=$(tail -n 100 "$logfile" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
    
    echo "${size} (${errors} errors, ${recent_errors} recent)"
}

# Function to check individual service
check_service() {
    local service_name=$1
    local service_description=$2
    local service_port=$3
    local health_endpoint=$4
    
    local pidfile="$PIDS_DIR/${service_name}.pid"
    local logfile="$PIDS_DIR/${service_name}.log"
    
    echo ""
    echo -e "${CYAN}🔍 $service_description Status${NC}"
    echo "----------------------------------------"
    
    # Check PID file
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        echo "PID File: $pidfile (PID: $pid)"
        
        # Check if process is running
        if is_process_running "$pid"; then
            log_success "Process: RUNNING (PID: $pid)"
            
            # Get process details
            local process_info=$(get_process_info "$pid")
            echo "Details: $process_info"
            
            # Check memory usage
            local mem_usage=$(ps -p "$pid" -o pmem --no-headers 2>/dev/null | tr -d ' ')
            if [ ! -z "$mem_usage" ]; then
                echo "Memory Usage: ${mem_usage}%"
            fi
            
            # Check CPU usage
            local cpu_usage=$(ps -p "$pid" -o pcpu --no-headers 2>/dev/null | tr -d ' ')
            if [ ! -z "$cpu_usage" ]; then
                echo "CPU Usage: ${cpu_usage}%"
            fi
            
        else
            log_error "Process: NOT RUNNING (stale PID: $pid)"
            echo "Recommendation: Remove stale PID file or restart service"
        fi
    else
        log_warning "PID File: NOT FOUND"
        echo "Service may not be running or was started manually"
    fi
    
    # Check port status
    if [ ! -z "$service_port" ]; then
        local port_status=$(check_port_status "$service_port")
        case "$port_status" in
            "LISTENING")
                log_success "Port $service_port: $port_status"
                ;;
            "CLOSED")
                log_error "Port $service_port: $port_status"
                ;;
            "N/A")
                log_info "Port: $port_status"
                ;;
        esac
    fi
    
    # Check service health
    if [ ! -z "$health_endpoint" ]; then
        local health_status=$(check_service_health "$service_name" "$health_endpoint")
        case "$health_status" in
            "HEALTHY")
                log_success "Health Check: $health_status"
                
                # Get detailed health information if available
                if command -v jq >/dev/null 2>&1; then
                    local health_details=$(get_service_health_details "$service_name" "$health_endpoint" 3)
                    if [ "$health_details" != "N/A" ]; then
                        local service_version=$(echo "$health_details" | jq -r '.version // "unknown"' 2>/dev/null || echo "unknown")
                        local service_status=$(echo "$health_details" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
                        echo "Service Status: $service_status (v$service_version)"
                        
                        # Show additional service-specific info
                        case "$service_name" in
                            "api")
                                local db_status=$(echo "$health_details" | jq -r '.database // "unknown"' 2>/dev/null || echo "unknown")
                                echo "Database: $db_status"
                                ;;
                            "mcp")
                                local sessions=$(echo "$health_details" | jq -r '.active_sessions // "unknown"' 2>/dev/null || echo "unknown")
                                local backend=$(echo "$health_details" | jq -r '.api_backend // "unknown"' 2>/dev/null || echo "unknown")
                                echo "Active Sessions: $sessions"
                                echo "Backend API: $backend"
                                ;;
                            "dashboard")
                                local backend=$(echo "$health_details" | jq -r '.api_backend // "unknown"' 2>/dev/null || echo "unknown")
                                echo "Backend API: $backend"
                                ;;
                        esac
                    fi
                fi
                ;;
            "UNHEALTHY"*|"UNREACHABLE")
                log_error "Health Check: $health_status"
                ;;
            "N/A")
                log_info "Health Check: $health_status"
                ;;
        esac
        
        if [ ! -z "$service_port" ]; then
            echo "Health URL: $health_endpoint"
        fi
    fi
    
    # Check log file
    if [ -f "$logfile" ]; then
        local log_info=$(get_log_info "$logfile")
        echo "Log File: $logfile"
        echo "Log Info: $log_info"
        
        # Show recent log entries
        echo ""
        echo "Recent Log Entries (last 5 lines):"
        tail -n 5 "$logfile" 2>/dev/null | sed 's/^/  /'
        
        # Check for recent errors
        local recent_errors=$(tail -n 50 "$logfile" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
        if [ "$recent_errors" -gt 0 ]; then
            log_warning "Found $recent_errors recent errors in log"
            echo "Recent Errors:"
            tail -n 50 "$logfile" 2>/dev/null | grep -i "error\|exception\|failed" | tail -n 3 | sed 's/^/  ❌ /'
        fi
    else
        log_warning "Log File: NOT FOUND"
    fi
}

# Function to show system overview
show_system_overview() {
    echo -e "${BLUE}🖥️  System Overview${NC}"
    echo "================================"
    
    # System load
    local load=$(uptime | sed 's/.*load average: //')
    echo "System Load: $load"
    
    # Memory usage
    local mem_info=$(free -h | grep "Mem:" | awk '{print $3 "/" $2 " (" $3/$2*100 "%)"}')
    echo "Memory Usage: $mem_info"
    
    # Disk usage for project directory
    local disk_usage=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')
    echo "Disk Usage: $disk_usage"
    
    # Check if run directory exists
    if [ -d "$PIDS_DIR" ]; then
        local pid_count=$(find "$PIDS_DIR" -name "*.pid" 2>/dev/null | wc -l)
        echo "PID Files: $pid_count"
    else
        echo "PID Files: 0 (directory not found)"
    fi
}

# Function to show quick status summary
show_quick_status() {
    echo -e "${CYAN}📋 Quick Status Summary${NC}"
    echo "========================="
    
    local services=("api" "mcp" "dashboard")
    local running_count=0
    local total_count=0
    
    for service in "${services[@]}"; do
        local pidfile="$PIDS_DIR/${service}.pid"
        
        # Check if service should be running based on config
        local should_run=false
        case "$service" in
            "api")
                if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
                    should_run=true
                fi
                ;;
            "mcp")
                if [ ! -z "$MCP_PORT" ]; then
                    should_run=true
                fi
                ;;
            "dashboard")
                if [ ! -z "$DASHBOARD_PORT" ]; then
                    should_run=true
                fi
                ;;
        esac
        
        if [ "$should_run" = true ]; then
            total_count=$((total_count + 1))
            
            if [ -f "$pidfile" ]; then
                local pid=$(cat "$pidfile")
                if is_process_running "$pid"; then
                    log_success "$service: RUNNING (PID: $pid)"
                    running_count=$((running_count + 1))
                else
                    log_error "$service: STOPPED (stale PID: $pid)"
                fi
            else
                log_error "$service: STOPPED (no PID file)"
            fi
        else
            log_info "$service: DISABLED (not configured)"
        fi
    done
    
    echo ""
    if [ $running_count -eq $total_count ] && [ $total_count -gt 0 ]; then
        log_success "All configured services are running ($running_count/$total_count)"
    elif [ $running_count -gt 0 ]; then
        log_warning "Some services are running ($running_count/$total_count)"
    else
        log_error "No services are running"
    fi
}

# Parse command line arguments
DETAILED=false
WATCH=false
WATCH_INTERVAL=5
SPECIFIC_SERVICE=""
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--detailed)
            DETAILED=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -i|--interval)
            WATCH_INTERVAL="$2"
            shift 2
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --detailed      Show detailed information for each service"
            echo "  -w, --watch         Watch mode (refresh every N seconds)"
            echo "  -i, --interval N    Watch interval in seconds (default: 5)"
            echo "  -s, --service NAME  Check specific service only (api|mcp|dashboard)"
            echo "  -q, --quiet         Quiet mode (minimal output)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Quick status check"
            echo "  $0 --detailed           # Detailed status for all services"
            echo "  $0 --watch              # Watch mode with 5s interval"
            echo "  $0 --watch --interval 10 # Watch mode with 10s interval"
            echo "  $0 --service api        # Check only API service"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main check function
run_check() {
    clear
    
    # Header
    echo -e "${BLUE}🔍 Headless PM Service Monitor${NC}"
    echo "================================"
    echo "Timestamp: $(date)"
    echo "Project: $PROJECT_ROOT"
    echo ""
    
    if [ "$QUIET" = false ]; then
        show_system_overview
        echo ""
    fi
    
    # Quick status (always show unless specific service requested)
    if [ -z "$SPECIFIC_SERVICE" ]; then
        show_quick_status
        echo ""
        test_all_health_endpoints
    fi
    
    # Detailed checks
    if [ "$DETAILED" = true ] || [ ! -z "$SPECIFIC_SERVICE" ]; then
        echo ""
        
        # Services to check
        local services_to_check=("api" "mcp" "dashboard")
        
        if [ ! -z "$SPECIFIC_SERVICE" ]; then
            case "$SPECIFIC_SERVICE" in
                api|mcp|dashboard)
                    services_to_check=("$SPECIFIC_SERVICE")
                    ;;
                *)
                    log_error "Unknown service: $SPECIFIC_SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        fi
        
        for service in "${services_to_check[@]}"; do
            case "$service" in
                "api")
                    local port=${SERVICE_PORT:-6969}
                    check_service "api" "API Server" "$port" "http://localhost:$port/health"
                    ;;
                "mcp")
                    if [ ! -z "$MCP_PORT" ]; then
                        check_service "mcp" "MCP SSE Server" "$MCP_PORT" "http://localhost:$MCP_PORT/health"
                    fi
                    ;;
                "dashboard")
                    if [ ! -z "$DASHBOARD_PORT" ]; then
                        check_service "dashboard" "Web Dashboard" "$DASHBOARD_PORT" "http://localhost:$DASHBOARD_PORT/api/health"
                    fi
                    ;;
            esac
        done
    fi
    
    if [ "$WATCH" = true ]; then
        echo ""
        echo "Refreshing in ${WATCH_INTERVAL}s... (Press Ctrl+C to stop)"
    fi
}

# Run check
if [ "$WATCH" = true ]; then
    # Watch mode
    trap 'echo ""; echo "Monitoring stopped."; exit 0' INT TERM
    
    while true; do
        run_check
        sleep "$WATCH_INTERVAL"
    done
else
    # Single check
    run_check
fi