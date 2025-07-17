# Service Management Guide

This guide explains how to use the service management scripts for Headless PM.

## Overview

Headless PM uses a pidfile-based service management system to monitor and control processes. The system includes several scripts in the `scripts/` folder:

- `manage_services.sh` - Main management script
- `start_services.sh` - Start services with pidfile management
- `stop_services.sh` - Stop services and cleanup
- `check_services.sh` - Monitoring and health checks

## Available Services

### 📚 API Server
- **Port**: 6969 (configurable via `SERVICE_PORT`)
- **Description**: Main REST API for Headless PM
- **Health Check**: `http://localhost:6969/health`
- **Documentation**: `http://localhost:6969/api/v1/docs`

### 🔌 MCP Server
- **Port**: 6968 (configurable via `MCP_PORT`)
- **Description**: Integration server for Claude Code
- **Health Check**: `http://localhost:6968`
- **Protocol**: SSE (Server-Sent Events)

### 🖥️ Dashboard
- **Port**: 3001 (configurable via `DASHBOARD_PORT`)
- **Description**: Web interface for project management
- **Health Check**: `http://localhost:3001`
- **Framework**: Next.js with Turbopack

## Configuration

### Environment Variables (.env)

```bash
# Service ports
SERVICE_PORT=6969      # API Server
MCP_PORT=6968         # MCP Server
DASHBOARD_PORT=3001   # Web Dashboard

# Database configuration
DB_CONNECTION="sqlite"
DATABASE_URL="sqlite:///headless-pm.db"

# API Security
API_KEY="your-secret-key"
```

**Important**: Services only start if their port is defined in `.env`. To disable a service, comment out or remove its port variable.

## Using the Scripts

### Main Script - manage_services.sh

The main script provides a unified interface for all services:

```bash
# Start all configured services
./scripts/manage_services.sh start

# Stop all services
./scripts/manage_services.sh stop

# Check service status
./scripts/manage_services.sh status

# Restart all services
./scripts/manage_services.sh restart

# View logs
./scripts/manage_services.sh logs
```

### Managing Specific Services

```bash
# Start a specific service
./scripts/manage_services.sh start api
./scripts/manage_services.sh start mcp
./scripts/manage_services.sh start dashboard

# Stop a specific service
./scripts/manage_services.sh stop api

# Check a specific service
./scripts/manage_services.sh status api

# Restart a specific service
./scripts/manage_services.sh restart mcp

# View service logs
./scripts/manage_services.sh logs dashboard
```

### Advanced Options

#### Continuous Monitoring
```bash
# Real-time monitoring
./scripts/manage_services.sh status --watch

# Custom monitoring interval
./scripts/check_services.sh --watch --interval 10

# Detailed status
./scripts/manage_services.sh status --detailed
```

#### Force Stop
```bash
# Force stop (immediate SIGKILL)
./scripts/manage_services.sh stop --force

# Force stop specific service
./scripts/stop_services.sh --service api --force
```

#### Quiet Mode
```bash
# Silent check (for scripts)
./scripts/check_services.sh --quiet
```

## File Management

### File Structure
```
headless-pm/
├── run/                    # Auto-created directory
│   ├── api.pid            # API server PID
│   ├── api.log            # API server logs
│   ├── mcp.pid            # MCP server PID
│   ├── mcp.log            # MCP server logs
│   ├── dashboard.pid      # Dashboard PID
│   └── dashboard.log      # Dashboard logs
└── scripts/
    ├── manage_services.sh  # Main script
    ├── start_services.sh   # Start services
    ├── stop_services.sh    # Stop services
    └── check_services.sh   # Monitoring
```

### Pidfiles
- **Location**: `run/*.pid`
- **Format**: Single PID number per file
- **Cleanup**: Automatic during normal shutdown
- **Validation**: Scripts verify processes exist

### Logs
- **Location**: `run/*.log`
- **Format**: stdout/stderr from services
- **Rotation**: No automatic rotation (implement if needed)
- **Access**: `tail -f run/service.log` or `./scripts/manage_services.sh logs service`

## Monitoring and Health Checks

### Health Verification

The `check_services.sh` script performs several checks:

1. **Process Check**: Active PID and process details
2. **Port Check**: Port listening or closed
3. **HTTP Health Checks**: Health endpoint status
4. **Log Analysis**: Size, recent errors
5. **Resource Usage**: CPU and memory

### Status Codes

#### Processes
- ✅ **RUNNING**: Active process with valid PID
- ❌ **STOPPED**: Process not found
- ⚠️ **STALE PID**: PID file exists but process dead

#### Ports
- ✅ **LISTENING**: Port is listening
- ❌ **CLOSED**: Port is closed
- ℹ️ **N/A**: Port not configured

#### Health Checks
- ✅ **HEALTHY**: HTTP 200/204
- ❌ **UNHEALTHY**: HTTP other than 200/204
- ❌ **UNREACHABLE**: No response
- ℹ️ **N/A**: No endpoint configured

## Integration with Existing System

### Compatibility with start.sh
The new system is compatible with the existing `start.sh` script:

- `start.sh` - Interactive startup with checks
- `scripts/start_services.sh` - Background startup with pidfiles

### Migration
To migrate from the existing system:

1. Stop current services (`Ctrl+C` on `start.sh`)
2. Use new scripts: `./scripts/manage_services.sh start`

## Troubleshooting

### Common Issues

#### Service won't start
```bash
# Check configuration
cat .env

# Check prerequisites
./setup/universal_setup.sh

# Check ports
lsof -i :6969
```

#### Stale PID file
```bash
# Manual cleanup
rm run/*.pid

# Clean restart
./scripts/manage_services.sh restart
```

#### Errors in logs
```bash
# See recent errors
./scripts/check_services.sh --detailed

# View full logs
./scripts/manage_services.sh logs api
```

### Debugging

#### Verbose Mode
```bash
# Enable debug traces in scripts
export DEBUG=1
./scripts/start_services.sh
```

#### Manual Checks
```bash
# Test API directly
curl http://localhost:6969/health

# Check processes
ps aux | grep -E "(uvicorn|node.*next)"

# Check ports
netstat -tlnp | grep -E ":(6969|6968|3001)"
```

## Usage Examples

### Complete Startup
```bash
# 1. Configuration
cp env-example .env
# Edit .env with your settings

# 2. Installation
./setup/universal_setup.sh

# 3. Start services
./scripts/manage_services.sh start

# 4. Verify
./scripts/manage_services.sh status --detailed
```

### Development Workflow
```bash
# Start monitoring mode
./scripts/manage_services.sh status --watch &

# Restart after changes
./scripts/manage_services.sh restart api

# Follow logs in real-time
./scripts/manage_services.sh logs api
```

### Production
```bash
# Start services
./scripts/manage_services.sh start

# Periodic monitoring (cron)
*/5 * * * * /path/to/headless-pm/scripts/check_services.sh --quiet

# Clean shutdown
./scripts/manage_services.sh stop
```

## Security

### Permissions
- Executable scripts: `chmod +x scripts/*.sh`
- PID files: read/write for service user
- Logs: accessible to service user

### Isolation
- Each service has its own PID and log
- Stopping one service doesn't affect others
- Automatic resource cleanup

## Performance

### Optimizations
- Parallel service startup
- Health checks with timeout
- Automatic cleanup of obsolete files

### Resource Monitoring
```bash
# Continuous monitoring
./scripts/check_services.sh --watch --detailed

# System information
./scripts/check_services.sh --detailed | grep -E "(Memory|CPU|Load)"
```

## Support

### Help
```bash
# General help
./scripts/manage_services.sh help

# Specific help
./scripts/check_services.sh --help
./scripts/stop_services.sh --help
```

### Debug Logs
- Service logs: `run/*.log`
- System errors: Check `dmesg` or `/var/log/syslog`
- Script errors: Add `set -x` to scripts for verbose output

## Script Reference

### manage_services.sh
Main control script with unified interface for all operations.

**Usage**: `./scripts/manage_services.sh <command> [options]`

**Commands**:
- `start [service]` - Start all or specific service
- `stop [service]` - Stop all or specific service  
- `status [service]` - Check status
- `restart [service]` - Restart services
- `logs [service]` - View logs
- `help` - Show help

### start_services.sh
Starts services in background with pidfile management.

**Features**:
- Environment validation
- Port availability checks
- Health check waiting
- Parallel service startup
- PID and log file creation

### stop_services.sh
Stops services and performs cleanup.

**Options**:
- `--force` - Immediate SIGKILL
- `--service <name>` - Stop specific service

**Features**:
- Graceful shutdown (SIGTERM first)
- Force kill if needed
- PID file cleanup
- Orphaned process cleanup

### check_services.sh
Comprehensive service monitoring and health checks.

**Options**:
- `--detailed` - Show detailed information
- `--watch` - Continuous monitoring
- `--interval N` - Watch interval (seconds)
- `--service <name>` - Check specific service
- `--quiet` - Minimal output

**Features**:
- Process validation
- Port status checking
- HTTP health checks
- Log analysis
- Resource usage monitoring