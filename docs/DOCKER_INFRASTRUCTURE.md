# Docker Infrastructure Guide

This guide explains how to deploy and manage Headless PM using Docker containers.

## Overview

The Headless PM application uses a **component-based containerized architecture** with each major component having its own Dockerfile and deployment context:

- **API Component** (`api/`) - FastAPI backend server with individual Dockerfile
- **MCP Component** (`mcp/`) - Model Context Protocol server with individual Dockerfile  
- **Dashboard Component** (`dashboard/`) - Next.js web interface with individual Dockerfile
- **Shared Core** (`shared/`) - Common models, services, and schemas mounted to all containers
- **Database** (`database/`) - Persistent storage outside container scope

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Ports 3001, 6968, 6969 available

### Development Deployment
```bash
# Clone and setup
git clone <repository-url>
cd headless-pm

# Use the Docker management script
./scripts/docker_manage.sh start

# Or manually with docker-compose
docker-compose up -d

# View logs
./scripts/docker_manage.sh logs
# or: docker-compose logs -f

# Access services
# - API: http://localhost:6969
# - Dashboard: http://localhost:3001  
# - MCP: http://localhost:6968
```

### Production Deployment
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or build with specific tags
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Architecture

### Service Dependencies
```
Dashboard (3001) → API (6969) → Database
MCP (6968) → API (6969)
```

### Network Configuration
- All services communicate via `headless-pm-network` bridge network
- External access via published ports
- Internal service discovery via container names

### Data Persistence
- **Database**: SQLite file stored in `database/` directory (mounted to containers)
- **Projects**: Project files stored in `projects/` directory (mounted to containers)
- **Agents**: Agent instructions and tools in `agents/` directory (mounted to containers)
- **Shared Code**: Common models and services in `shared/` directory (mounted to containers)
- **Logs**: Container logs managed by Docker

## Service Details

### API Service (headless-pm-api)
**Image**: Built from `api/Dockerfile`
**Port**: 6969
**Health Check**: `GET /health`

**Environment Variables**:
- `PORT=6969` - Server port
- `DATABASE_URL=sqlite:///app/database/headless-pm.db` - Database location
- `PYTHONPATH=/app` - Python module path

**Volumes**:
- `./database:/app/database` - Database persistence
- `./projects:/app/projects` - Project files
- `./agents:/app/agents` - Agent tools and instructions
- `./shared:/app/shared` - Shared core components

### MCP Service (headless-pm-mcp)
**Image**: Built from `mcp/Dockerfile`
**Port**: 6968
**Health Check**: Process check for `mcp.src`

**Environment Variables**:
- `MCP_PORT=6968` - MCP server port
- `API_BASE_URL=http://api:6969` - Internal API URL
- `PYTHONPATH=/app` - Python module path

**Volumes**:
- `./projects:/app/projects` - Project files
- `./agents:/app/agents` - Agent tools and instructions
- `./shared:/app/shared` - Shared core components

**Dependencies**: Waits for API service health check

### Dashboard Service (headless-pm-dashboard)
**Image**: Built from `dashboard/Dockerfile`
**Port**: 3001
**Health Check**: `GET /api/health`

**Environment Variables**:
- `PORT=3001` - Dashboard port
- `NEXT_PUBLIC_API_URL=http://localhost:6969` - External API URL for browser
- `NODE_ENV=production` - Next.js environment

**Dependencies**: Waits for API service health check

**Note**: Dashboard is self-contained and doesn't need shared volumes as it communicates with the API via HTTP.

## Management Commands

### Basic Operations

**Using Docker Management Script (Recommended):**
```bash
# Start all services
./scripts/docker_manage.sh start

# Stop all services
./scripts/docker_manage.sh stop

# Restart specific service
./scripts/docker_manage.sh restart api

# View service logs
./scripts/docker_manage.sh logs api
./scripts/docker_manage.sh logs -f dashboard

# Check service health
./scripts/docker_manage.sh health

# Open shell in container
./scripts/docker_manage.sh shell api
```

**Using Docker Compose Directly:**
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart api

# View service logs
docker-compose logs api
docker-compose logs -f dashboard
```

### Development Workflow
```bash
# Rebuild after code changes
docker-compose build api
docker-compose up -d api

# Rebuild all services
docker-compose build
docker-compose up -d

# Development with live reload (mount source)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Health Monitoring
```bash
# Check service health
docker-compose ps

# Detailed health status
docker inspect headless-pm-api --format='{{.State.Health.Status}}'

# View health check logs
docker inspect headless-pm-api --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

### Data Management

**Using Docker Management Script (Recommended):**
```bash
# Backup database
./scripts/docker_manage.sh backup

# Restore database
./scripts/docker_manage.sh restore backup_20250717_123456.db

# Reset all data (WARNING: destructive)
./scripts/docker_manage.sh reset
```

**Manual Operations:**
```bash
# Backup database
docker cp headless-pm-api:/app/database/headless-pm.db ./backup-$(date +%Y%m%d).db

# Restore database
docker cp ./backup.db headless-pm-api:/app/database/headless-pm.db
docker-compose restart api

# Clear all data (WARNING: destructive)
docker-compose down -v
rm -rf database/* projects/*
mkdir -p database projects
docker-compose up -d
```

## Configuration

### Environment Files
Create `.env` file in project root:
```bash
# API Configuration
PORT=6969
DATABASE_URL=sqlite:///app/data/headless-pm.db

# MCP Configuration  
MCP_PORT=6968

# Dashboard Configuration
DASHBOARD_PORT=3001
NEXT_PUBLIC_API_URL=http://localhost:6969

# Optional: API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Custom Networks
```yaml
# docker-compose.override.yml
networks:
  headless-pm-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Resource Limits
Production deployment includes resource limits:
- **API**: 512M RAM, 0.5 CPU
- **MCP**: 256M RAM, 0.25 CPU  
- **Dashboard**: 256M RAM, 0.25 CPU

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :6969

# Use different ports
PORT=7000 docker-compose up -d
```

#### Service Won't Start
```bash
# Check logs
docker-compose logs api

# Check health
docker-compose ps

# Restart with clean state
docker-compose down
docker system prune -f
docker-compose up -d
```

#### Database Issues
```bash
# Check database file permissions
ls -la data/

# Reset database
docker-compose exec api python -m src.cli.main init
```

#### Network Connectivity
```bash
# Test internal connectivity
docker-compose exec dashboard wget -qO- http://api:6969/health

# Check network
docker network ls
docker network inspect headless-pm_headless-pm-network
```

### Performance Optimization

#### Build Optimization
```bash
# Use build cache
docker-compose build --parallel

# Multi-stage builds
docker build --target production -f Dockerfile.api .
```

#### Runtime Optimization
```bash
# Enable health checks
# Already configured in docker-compose.yml

# Monitor resource usage
docker stats headless-pm-api headless-pm-mcp headless-pm-dashboard
```

## Security Considerations

### Container Security
- Services run as non-root users where possible
- No privileged containers
- Read-only root filesystems where applicable
- Resource limits prevent resource exhaustion

### Network Security
- Internal network isolation
- Only required ports exposed
- No unnecessary network privileges

### Data Security
- Database files in dedicated volumes
- Project files isolated per container
- No secrets in environment variables (use Docker secrets in production)

## Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml headless-pm

# Scale services
docker service scale headless-pm_api=2
```

### Using Kubernetes
```bash
# Generate Kubernetes manifests (requires kompose)
kompose convert -f docker-compose.yml -f docker-compose.prod.yml

# Deploy to cluster
kubectl apply -f .
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring and Logging

### Log Management
```bash
# Configure log rotation
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d

# View aggregated logs
docker-compose logs --tail=100 -f
```

### Metrics Collection
```bash
# Add monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3000
# Access Prometheus: http://localhost:9090
```

### Health Monitoring
All services include health checks that report:
- Service availability
- Resource usage
- Response times
- Error rates

## Backup and Recovery

### Automated Backups
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker cp headless-pm-api:/app/data/headless-pm.db ./backups/backup_$DATE.db
```

### Disaster Recovery
```bash
# Full system restore
docker-compose down
# Restore data volume
docker-compose up -d
```

## Development Setup

### Development Override
Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  api:
    volumes:
      - ./src:/app/src:ro
    command: python -m src.main --reload
    
  dashboard:
    volumes:
      - ./dashboard/src:/app/src:ro
    command: npm run dev
```

### Testing
```bash
# Run tests in containers
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Interactive testing
docker-compose exec api python -m pytest
```

This infrastructure provides a robust, scalable foundation for deploying Headless PM in any environment from development to production.