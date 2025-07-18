# Component Architecture Guide

This document explains the component-based architecture of Headless PM and how the restructured codebase works.

## Overview

Headless PM uses a **component-based containerized architecture** where each major functionality is separated into independent, deployable components. This design provides:

- **Clear separation of concerns**
- **Independent deployment and scaling**
- **Better maintainability and development workflow**
- **Flexible deployment options (Docker or traditional)**

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Headless PM System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Dashboard     │    │   API Server    │    │   MCP Server    │ │
│  │   (Port 3001)   │────│   (Port 6969)   │────│   (Port 6968)   │ │
│  │   Next.js UI    │    │   FastAPI Core  │    │   Claude Code   │ │
│  │   dashboard/    │    │   api/          │    │   mcp/          │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│           │                       │                       │       │
│           └───────────────────────┼───────────────────────┘       │
│                                   │                               │
│               ┌─────────────────────────────────────┐             │
│               │           Shared Core               │             │
│               │      Models • Services • Schemas   │             │
│               │           shared/                   │             │
│               └─────────────────────────────────────┘             │
│                                   │                               │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │    Database     │    │    Projects     │    │     Agents      │ │
│  │  database/      │    │   projects/     │    │    agents/      │ │
│  │  SQLite/MySQL   │    │  Workspaces     │    │ Instructions    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 🏗️ Component Structure

Each component follows a consistent structure:

```
component_name/
├── src/                    # Source code
├── Dockerfile             # Container definition
└── README.md              # Component-specific documentation
```

### 📚 API Component (`api/`)

**Purpose**: Core REST API server providing all business functionality

**Structure**:
```
api/
├── src/
│   ├── routes/            # API route handlers
│   │   ├── routes.py      # Core agent/task endpoints
│   │   ├── project_routes.py # Project management
│   │   ├── document_routes.py # Communication
│   │   └── [other routes...] # Additional endpoints
│   └── main.py           # FastAPI application entry point
├── Dockerfile            # API container definition
└── README.md            # API-specific documentation
```

**Dependencies**:
- `shared/models` - Database models and enums
- `shared/services` - Business logic services
- `shared/schemas` - Request/response schemas

**Key Features**:
- FastAPI with automatic OpenAPI documentation
- Comprehensive REST endpoints for all functionality
- Health monitoring and status reporting
- Database session management
- CORS configuration for web access

### 🔌 MCP Component (`mcp/`)

**Purpose**: Model Context Protocol server for Claude Code integration

**Structure**:
```
mcp/
├── src/
│   ├── server.py                    # Main MCP server implementation
│   ├── http_server.py              # HTTP transport
│   ├── sse_server.py               # Server-Sent Events transport
│   ├── websocket_server.py         # WebSocket transport
│   ├── stdio_bridge.py             # STDIO transport bridge
│   ├── token_tracker.py            # Usage tracking
│   └── [other transports...]       # Additional protocols
├── Dockerfile                      # MCP container definition
└── README.md                      # MCP-specific documentation
```

**Dependencies**:
- Makes HTTP calls to API component
- No direct shared code dependencies (loosely coupled)

**Key Features**:
- Multiple transport protocols (HTTP, SSE, WebSocket, STDIO)
- Natural language interface for Claude Code
- Token usage tracking and monitoring
- Automatic agent registration with "mcp" connection type
- Bridge between MCP protocol and REST API

### 🖥️ Dashboard Component (`dashboard/`)

**Purpose**: Next.js web interface for project management and monitoring

**Structure**:
```
dashboard/
├── src/
│   ├── app/              # Next.js 15 app directory
│   ├── components/       # React components
│   └── lib/              # Utilities and API client
├── public/               # Static assets
├── Dockerfile           # Dashboard container definition
├── package.json         # Node.js dependencies
└── README.md           # Dashboard-specific documentation
```

**Dependencies**:
- Makes HTTP calls to API component
- Independent Node.js application
- No shared Python code dependencies

**Key Features**:
- Next.js 15 with React 19
- Real-time project monitoring
- Task management interface
- Agent activity tracking
- Service health dashboard
- Responsive design for mobile/desktop

### 🔧 CLI Component (`cli/`)

**Purpose**: Command-line tools for database management and utilities

**Structure**:
```
cli/
├── src/
│   ├── main.py          # Main CLI commands
│   ├── dashboard.py     # Dashboard utilities
│   └── sanity_check.py  # Health diagnostics
└── README.md           # CLI-specific documentation
```

**Dependencies**:
- `shared/models` - Database models for direct access
- `shared/services` - Business logic for operations

**Key Features**:
- Database initialization and seeding
- Health checks and diagnostics
- Administrative operations
- Development utilities

### 🗂️ Shared Core (`shared/`)

**Purpose**: Common code shared across Python components

**Structure**:
```
shared/
├── models/              # Database models and enums
│   ├── database.py      # SQLModel setup and sessions
│   ├── models.py        # Core data models
│   ├── enums.py         # Task status, roles, etc.
│   └── document_enums.py # Document types
├── services/            # Business logic services
│   ├── agent_service.py # Agent management
│   ├── task_service.py  # Task operations
│   ├── project_service.py # Project management
│   └── [other services...] # Additional business logic
└── schemas/             # API request/response schemas
    ├── schemas.py       # Pydantic models
    └── dependencies.py  # Auth and middleware
```

**Key Features**:
- SQLModel database models with type safety
- Comprehensive business logic services
- Pydantic schemas for API validation
- Shared utilities and helpers
- Database session management
- Enum definitions for consistency

## Data Flow and Communication

### 🔄 Component Communication

1. **Dashboard ↔ API**: HTTP REST calls
2. **MCP ↔ API**: HTTP REST calls  
3. **CLI ↔ Shared**: Direct Python imports
4. **API ↔ Shared**: Direct Python imports

### 📊 Data Persistence

```
Database (database/)
├── headless-pm.db       # SQLite database file
└── [backups...]         # Database backups

Projects (projects/)     # Project workspaces
├── project-name/        # Individual project directories
│   ├── docs/           # Project documentation
│   ├── shared/         # Shared project files
│   └── instructions/   # Agent instructions
└── [other projects...]

Agents (agents/)         # Agent tools and instructions
├── client/             # Client tools
├── claude/             # Claude Code integration
└── mcp/                # MCP-specific instructions
```

### 🔗 Dependency Relationships

```
┌─────────────────┐         ┌─────────────────┐
│   Dashboard     │──HTTP──→│   API Server    │
│   (Independent) │         │   (Core)        │
└─────────────────┘         └─────────────────┘
                                       │
┌─────────────────┐                    │ Imports
│   MCP Server    │──HTTP──────────────┘
│   (Independent) │                    │
└─────────────────┘                    ▼
                                ┌─────────────────┐
┌─────────────────┐             │   Shared Core   │
│   CLI Tools     │──Imports──→│   (Foundation)  │
│   (Admin)       │             └─────────────────┘
└─────────────────┘                     │
                                        ▼
                                ┌─────────────────┐
                                │    Database     │
                                │   (Storage)     │
                                └─────────────────┘
```

## Deployment Strategies

### 🐳 Docker Deployment (Recommended)

**Advantages**:
- Complete isolation between components
- Consistent environment across platforms
- Easy scaling and orchestration
- Production-ready configuration
- Simplified dependency management

**Container Architecture**:
```bash
# Each component runs in its own container
docker-compose up -d

# Containers:
# - headless-pm-api (API Component)
# - headless-pm-mcp (MCP Component)  
# - headless-pm-dashboard (Dashboard Component)

# Shared volumes:
# - ./shared:/app/shared (mounted to Python containers)
# - ./database:/app/database (persistent database)
# - ./projects:/app/projects (project workspaces)
# - ./agents:/app/agents (agent instructions)
```

### 🔧 Traditional Deployment

**Advantages**:
- Direct process control
- Easier debugging during development
- Lower resource overhead
- Simpler log management

**Process Architecture**:
```bash
# Each component runs as a separate Python/Node process
./scripts/manage_services.sh start

# Processes:
# - python -m api.src.main (API Server)
# - python -m mcp.src.http_server (MCP Server)
# - npm run start (Dashboard)
```

## Development Workflow

### 🔨 Component Development

1. **Identify the component** you need to modify
2. **Navigate to component directory** (`api/`, `mcp/`, `dashboard/`, `cli/`)
3. **Make changes** to component-specific code
4. **Update shared code** if needed (`shared/`)
5. **Test component** individually
6. **Build and deploy** the component

### 🧪 Testing Strategy

```bash
# Test individual components
docker-compose build api
docker-compose up api

# Test component integration
docker-compose up -d
./scripts/docker_manage.sh health

# Run full test suite
python -m pytest tests/
```

### 📦 Build Process

```bash
# Build all components
docker-compose build

# Build specific component
docker-compose build api

# Use management script
./scripts/docker_manage.sh build mcp
```

## Scaling and Performance

### 🚀 Horizontal Scaling

Components can be scaled independently:

```bash
# Scale API component for high load
docker-compose up -d --scale api=3

# Add load balancer for multiple instances
# (External load balancer configuration required)
```

### 📈 Resource Allocation

Each component has different resource requirements:

- **API Component**: CPU-intensive (business logic)
- **MCP Component**: Low resource usage
- **Dashboard Component**: Memory for Node.js
- **Shared Core**: No runtime overhead (mounted volumes)

### 🎯 Performance Optimization

1. **Database**: Optimize shared models and queries
2. **API**: Cache responses, optimize endpoints
3. **MCP**: Lightweight token tracking
4. **Dashboard**: Next.js optimizations, static generation

## Security Considerations

### 🔒 Component Isolation

- Each component runs in isolated container environment
- Network communication only via defined ports
- No direct file system access between components
- Shared code mounted read-only where possible

### 🛡️ Data Security

- Database files outside container scope
- Secrets managed via environment variables
- API authentication via headers
- Input validation in shared schemas

### 🚪 Network Security

- Internal network for component communication
- Only required ports exposed externally
- Health checks for monitoring
- No privileged container access

## Migration and Updates

### 🔄 Component Updates

1. **Build new component version**
2. **Test in isolation**
3. **Deploy with rolling update**
4. **Verify health checks**
5. **Rollback if needed**

### 📋 Database Migrations

```bash
# Database migrations handled via CLI component
docker-compose exec api python -m cli.src.main migrate

# Or run migration scripts directly
python migrations/run_migrations.py
```

### ⚡ Zero-Downtime Deployments

1. **Blue-green deployment** for API component
2. **Rolling updates** for stateless components
3. **Database migrations** during maintenance windows
4. **Health check verification** before traffic routing

## Monitoring and Observability

### 📊 Health Monitoring

Each component provides health endpoints:
- **API**: `GET /health` with database status
- **MCP**: Process-based health checks
- **Dashboard**: `GET /api/health`

### 📈 Metrics Collection

```bash
# Component resource usage
docker stats headless-pm-api headless-pm-mcp headless-pm-dashboard

# Application metrics
./scripts/docker_manage.sh health

# Service registry monitoring
curl http://localhost:6969/api/v1/services
```

### 🔍 Logging

- **Centralized logging** via Docker log drivers
- **Component-specific logs** accessible via management scripts
- **Structured logging** in JSON format
- **Log rotation** and retention policies

## Best Practices

### 🎯 Component Design

1. **Single Responsibility**: Each component has one clear purpose
2. **Loose Coupling**: Components communicate via well-defined APIs
3. **High Cohesion**: Related functionality grouped together
4. **Shared Foundation**: Common code in shared core

### 🔧 Development

1. **Component-First**: Start with the component you're modifying
2. **Shared Updates**: Update shared code when multiple components benefit
3. **Testing**: Test components individually and in integration
4. **Documentation**: Keep component READMEs updated

### 🚀 Deployment

1. **Docker-First**: Use Docker for consistency
2. **Environment Parity**: Same configuration across environments
3. **Health Checks**: Verify all components before deployment
4. **Backup Strategy**: Regular database and configuration backups

## Troubleshooting

### 🐛 Common Issues

1. **Import Path Errors**: Ensure correct `shared.*` imports
2. **Container Communication**: Verify network configuration
3. **Mount Point Issues**: Check volume paths in docker-compose
4. **Port Conflicts**: Ensure ports are available and configured

### 🔍 Debugging

```bash
# Check component health
./scripts/docker_manage.sh health

# View component logs
./scripts/docker_manage.sh logs api

# Open shell in component
./scripts/docker_manage.sh shell api

# Test component connectivity
curl http://localhost:6969/health
```

### 🛠️ Recovery

```bash
# Restart problematic component
./scripts/docker_manage.sh restart mcp

# Rebuild component from scratch
./scripts/docker_manage.sh build --no-cache api

# Reset entire system
./scripts/docker_manage.sh reset
```

This component-based architecture provides a solid foundation for scaling, maintaining, and extending Headless PM while keeping the codebase organized and manageable.