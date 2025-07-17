#!/bin/bash

# Quick Health Check Script - Non-blocking health checks for all services
# Returns status codes and provides fast feedback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Function to check health endpoint with timeout
check_health_endpoint() {
    local service_name=$1
    local url=$2
    local timeout=${3:-3}
    
    # Use timeout to prevent hanging
    local http_code=$(timeout "$timeout" curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$timeout" "$url" 2>/dev/null || echo "000")
    
    case "$http_code" in
        200)
            echo -e "${GREEN}✅ $service_name: HEALTHY${NC}"
            return 0
            ;;
        000)
            echo -e "${RED}❌ $service_name: UNREACHABLE${NC}"
            return 1
            ;;
        *)
            echo -e "${YELLOW}⚠️  $service_name: UNHEALTHY (HTTP $http_code)${NC}"
            return 1
            ;;
    esac
}

# Function to get detailed health info (JSON)
get_health_details() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    local response=$(timeout "$timeout" curl -s --connect-timeout "$timeout" "$url" 2>/dev/null || echo "")
    
    if [ -n "$response" ] && echo "$response" | jq . >/dev/null 2>&1; then
        echo "$response"
    else
        echo '{"status": "error", "message": "No response or invalid JSON"}'
    fi
}

# Function to show service overview
show_service_overview() {
    local api_port=${SERVICE_PORT:-6969}
    local mcp_port=${MCP_PORT:-6968}
    local dashboard_port=${DASHBOARD_PORT:-3001}
    
    local total_services=0
    local healthy_services=0
    local results=()
    
    # Check API server
    if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
        total_services=$((total_services + 1))
        if check_health_endpoint "API Server" "http://localhost:$api_port/health" 2; then
            healthy_services=$((healthy_services + 1))
        fi
    fi
    
    # Check MCP server
    if [ ! -z "$MCP_PORT" ]; then
        total_services=$((total_services + 1))
        if check_health_endpoint "MCP Server" "http://localhost:$mcp_port/health" 2; then
            healthy_services=$((healthy_services + 1))
        fi
    fi
    
    # Check Dashboard
    if [ ! -z "$DASHBOARD_PORT" ]; then
        total_services=$((total_services + 1))
        if check_health_endpoint "Dashboard" "http://localhost:$dashboard_port/api/health" 2; then
            healthy_services=$((healthy_services + 1))
        fi
    fi
    
    echo ""
    echo -e "${CYAN}📊 Overall Status: $healthy_services/$total_services services healthy${NC}"
    
    if [ $healthy_services -eq $total_services ] && [ $total_services -gt 0 ]; then
        echo -e "${GREEN}🎉 All services are running properly!${NC}"
        return 0
    elif [ $healthy_services -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some services are having issues.${NC}"
        return 1
    else
        echo -e "${RED}🚨 No services are responding to health checks.${NC}"
        return 2
    fi
}

# Function to check if services are configured
check_configuration() {
    local configured_services=0
    
    echo -e "${BLUE}🔧 Service Configuration:${NC}"
    
    if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
        echo -e "${GREEN}✅ API Server: Configured (port ${SERVICE_PORT:-6969})${NC}"
        configured_services=$((configured_services + 1))
    else
        echo -e "${YELLOW}⚠️  API Server: Not configured${NC}"
    fi
    
    if [ ! -z "$MCP_PORT" ]; then
        echo -e "${GREEN}✅ MCP Server: Configured (port $MCP_PORT)${NC}"
        configured_services=$((configured_services + 1))
    else
        echo -e "${YELLOW}⚠️  MCP Server: Not configured${NC}"
    fi
    
    if [ ! -z "$DASHBOARD_PORT" ]; then
        echo -e "${GREEN}✅ Dashboard: Configured (port $DASHBOARD_PORT)${NC}"
        configured_services=$((configured_services + 1))
    else
        echo -e "${YELLOW}⚠️  Dashboard: Not configured${NC}"
    fi
    
    echo -e "${CYAN}📋 Total configured services: $configured_services${NC}"
    echo ""
}

# Function to show detailed health info
show_detailed_health() {
    local api_port=${SERVICE_PORT:-6969}
    local mcp_port=${MCP_PORT:-6968}
    local dashboard_port=${DASHBOARD_PORT:-3001}
    
    echo -e "${BLUE}📋 Detailed Health Information:${NC}"
    echo "================================="
    
    # Check if jq is available
    if ! command -v jq >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  jq not available - showing basic health checks only${NC}"
        echo ""
        show_service_overview
        return
    fi
    
    # API Server details
    if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
        echo ""
        echo -e "${CYAN}🔍 API Server Details:${NC}"
        local api_health=$(get_health_details "api" "http://localhost:$api_port/health" 5)
        echo "$api_health" | jq -r '
            "Status: " + (.status // "unknown") + 
            " | Version: " + (.version // "unknown") + 
            " | Database: " + (.database // "unknown")
        ' 2>/dev/null || echo "Failed to parse API health response"
    fi
    
    # MCP Server details
    if [ ! -z "$MCP_PORT" ]; then
        echo ""
        echo -e "${CYAN}🔍 MCP Server Details:${NC}"
        local mcp_health=$(get_health_details "mcp" "http://localhost:$mcp_port/health" 5)
        echo "$mcp_health" | jq -r '
            "Status: " + (.status // "unknown") + 
            " | Version: " + (.version // "unknown") + 
            " | Active Sessions: " + (.active_sessions // "unknown" | tostring) + 
            " | Backend API: " + (.api_backend // "unknown")
        ' 2>/dev/null || echo "Failed to parse MCP health response"
    fi
    
    # Dashboard details
    if [ ! -z "$DASHBOARD_PORT" ]; then
        echo ""
        echo -e "${CYAN}🔍 Dashboard Details:${NC}"
        local dashboard_health=$(get_health_details "dashboard" "http://localhost:$dashboard_port/api/health" 5)
        echo "$dashboard_health" | jq -r '
            "Status: " + (.status // "unknown") + 
            " | Version: " + (.version // "unknown") + 
            " | Backend API: " + (.api_backend // "unknown")
        ' 2>/dev/null || echo "Failed to parse Dashboard health response"
    fi
}

# Parse command line arguments
DETAILED=false
QUIET=false
JSON_OUTPUT=false
WATCH=false
WATCH_INTERVAL=5

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--detailed)
            DETAILED=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -j|--json)
            JSON_OUTPUT=true
            QUIET=true
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
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Quick health check for Headless PM services"
            echo ""
            echo "Options:"
            echo "  -d, --detailed      Show detailed health information"
            echo "  -q, --quiet         Minimal output"
            echo "  -j, --json          Output as JSON"
            echo "  -w, --watch         Watch mode (continuous checking)"
            echo "  -i, --interval N    Watch interval in seconds (default: 5)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Quick health check"
            echo "  $0 --detailed       # Detailed health information"
            echo "  $0 --json           # JSON output for scripting"
            echo "  $0 --watch          # Continuous monitoring"
            echo ""
            echo "Exit codes:"
            echo "  0 - All services healthy"
            echo "  1 - Some services unhealthy"
            echo "  2 - No services responding"
            echo "  3 - Configuration issues"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main function
main() {
    if [ "$JSON_OUTPUT" = true ]; then
        # JSON output for scripting
        local api_port=${SERVICE_PORT:-6969}
        local mcp_port=${MCP_PORT:-6968}
        local dashboard_port=${DASHBOARD_PORT:-3001}
        
        echo "{"
        echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
        echo "  \"services\": {"
        
        local first=true
        if [ ! -z "$SERVICE_PORT" ] || [ "$SERVICE_PORT" = "6969" ]; then
            [ "$first" = false ] && echo ","
            local api_health=$(get_health_details "api" "http://localhost:$api_port/health" 3)
            echo -n "    \"api\": $api_health"
            first=false
        fi
        
        if [ ! -z "$MCP_PORT" ]; then
            [ "$first" = false ] && echo ","
            local mcp_health=$(get_health_details "mcp" "http://localhost:$mcp_port/health" 3)
            echo -n "    \"mcp\": $mcp_health"
            first=false
        fi
        
        if [ ! -z "$DASHBOARD_PORT" ]; then
            [ "$first" = false ] && echo ","
            local dashboard_health=$(get_health_details "dashboard" "http://localhost:$dashboard_port/api/health" 3)
            echo -n "    \"dashboard\": $dashboard_health"
            first=false
        fi
        
        echo ""
        echo "  }"
        echo "}"
        return 0
    fi
    
    if [ "$QUIET" = false ]; then
        echo -e "${BLUE}🏥 Headless PM Health Check${NC}"
        echo "============================"
        echo "Timestamp: $(date)"
        echo ""
        
        check_configuration
    fi
    
    if [ "$DETAILED" = true ]; then
        show_detailed_health
    else
        show_service_overview
    fi
}

# Watch mode
if [ "$WATCH" = true ]; then
    trap 'echo ""; echo "Health monitoring stopped."; exit 0' INT TERM
    
    while true; do
        clear
        main
        echo ""
        echo "Refreshing in ${WATCH_INTERVAL}s... (Press Ctrl+C to stop)"
        sleep "$WATCH_INTERVAL"
    done
else
    main
fi