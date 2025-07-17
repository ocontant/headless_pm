#!/bin/bash

# Headless PM Service Management - Master Control Script
# Script principal pour gérer tous les services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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

show_banner() {
    echo -e "${CYAN}"
    echo "🚀 Headless PM Service Manager"
    echo "==============================="
    echo -e "${NC}"
}

show_help() {
    show_banner
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}start${NC}      Start all configured services"
    echo -e "  ${RED}stop${NC}       Stop all services"
    echo -e "  ${CYAN}status${NC}     Check service status"
    echo -e "  ${YELLOW}restart${NC}    Restart all services"
    echo -e "  ${BLUE}logs${NC}       Show service logs"
    echo ""
    echo "Service-specific commands:"
    echo "  start <service>    Start specific service (api|mcp|dashboard)"
    echo "  stop <service>     Stop specific service"
    echo "  status <service>   Check specific service status"
    echo "  restart <service>  Restart specific service"
    echo "  logs <service>     Show specific service logs"
    echo ""
    echo "Status options:"
    echo "  status --detailed  Show detailed status information"
    echo "  status --watch     Watch mode (refresh every 5s)"
    echo "  status --quiet     Minimal output"
    echo ""
    echo "Stop options:"
    echo "  stop --force       Force kill processes immediately"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 stop                     # Stop all services"
    echo "  $0 status --watch           # Monitor services in real-time"
    echo "  $0 restart api              # Restart only API service"
    echo "  $0 logs dashboard           # Show dashboard logs"
    echo "  $0 stop --force             # Force stop all services"
    echo ""
    echo "Project Services:"
    echo "  📚 API Server    - Main REST API (port 6969)"
    echo "  🔌 MCP Server    - Claude Code integration (port 6968)"
    echo "  🖥️  Dashboard     - Web interface (port 3001)"
    echo ""
}

# Function to execute service scripts with proper error handling
execute_script() {
    local script_name=$1
    shift
    local script_path="$SCRIPT_DIR/${script_name}.sh"
    
    if [ ! -f "$script_path" ]; then
        log_error "Script not found: $script_path"
        return 1
    fi
    
    if [ ! -x "$script_path" ]; then
        log_error "Script not executable: $script_path"
        log_info "Run: chmod +x $script_path"
        return 1
    fi
    
    "$script_path" "$@"
}

# Main command processing
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND=$1
shift

case "$COMMAND" in
    "start")
        show_banner
        if [ $# -gt 0 ]; then
            # Start specific service
            SERVICE=$1
            case "$SERVICE" in
                api|mcp|dashboard)
                    log_info "Starting $SERVICE service..."
                    execute_script "start_services" # Will be enhanced to support single service
                    ;;
                *)
                    log_error "Unknown service: $SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        else
            # Start all services
            log_info "Starting all configured services..."
            execute_script "start_services"
        fi
        ;;
        
    "stop")
        show_banner
        if [ $# -gt 0 ] && [ "$1" != "--force" ]; then
            # Stop specific service
            SERVICE=$1
            case "$SERVICE" in
                api|mcp|dashboard)
                    log_info "Stopping $SERVICE service..."
                    execute_script "stop_services" --service "$SERVICE"
                    ;;
                *)
                    log_error "Unknown service: $SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        else
            # Stop all services
            log_info "Stopping all services..."
            execute_script "stop_services" "$@"
        fi
        ;;
        
    "status"|"check")
        if [ $# -gt 0 ] && [[ "$1" != -* ]]; then
            # Check specific service
            SERVICE=$1
            shift
            case "$SERVICE" in
                api|mcp|dashboard)
                    execute_script "check_services" --service "$SERVICE" "$@"
                    ;;
                *)
                    log_error "Unknown service: $SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        else
            # Check all services
            execute_script "check_services" "$@"
        fi
        ;;
        
    "restart")
        show_banner
        if [ $# -gt 0 ]; then
            # Restart specific service
            SERVICE=$1
            case "$SERVICE" in
                api|mcp|dashboard)
                    log_info "Restarting $SERVICE service..."
                    execute_script "stop_services" --service "$SERVICE"
                    sleep 2
                    execute_script "start_services" # Will be enhanced for single service
                    ;;
                *)
                    log_error "Unknown service: $SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        else
            # Restart all services
            log_info "Restarting all services..."
            execute_script "stop_services"
            sleep 3
            execute_script "start_services"
        fi
        ;;
        
    "logs"|"log")
        PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
        PIDS_DIR="$PROJECT_ROOT/run"
        
        if [ $# -gt 0 ]; then
            # Show specific service logs
            SERVICE=$1
            LOGFILE="$PIDS_DIR/${SERVICE}.log"
            
            case "$SERVICE" in
                api|mcp|dashboard)
                    if [ -f "$LOGFILE" ]; then
                        log_info "Showing logs for $SERVICE service:"
                        echo "Log file: $LOGFILE"
                        echo "----------------------------------------"
                        tail -f "$LOGFILE"
                    else
                        log_error "Log file not found: $LOGFILE"
                        log_info "Service may not be running or no logs generated yet"
                    fi
                    ;;
                *)
                    log_error "Unknown service: $SERVICE"
                    log_info "Available services: api, mcp, dashboard"
                    exit 1
                    ;;
            esac
        else
            # Show all logs
            if [ -d "$PIDS_DIR" ]; then
                log_info "Available log files:"
                ls -la "$PIDS_DIR"/*.log 2>/dev/null || log_warning "No log files found"
                echo ""
                log_info "Use '$0 logs <service>' to follow a specific service log"
            else
                log_warning "No log directory found ($PIDS_DIR)"
                log_info "Services may not be running"
            fi
        fi
        ;;
        
    "help"|"-h"|"--help")
        show_help
        ;;
        
    *)
        log_error "Unknown command: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac