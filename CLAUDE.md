# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

### Docker Deployment (Recommended for Production)
```bash
# Quick start with Docker
./scripts/docker_manage.sh start

# Or manually with docker-compose
docker-compose up -d

# Access services:
# - API: http://localhost:6969
# - Dashboard: http://localhost:3001
# - MCP: http://localhost:6968

# View logs
./scripts/docker_manage.sh logs

# Stop services
./scripts/docker_manage.sh stop
```

For complete Docker documentation, see `docs/DOCKER_INFRASTRUCTURE.md`.

### Automated Setup (Recommended for Development)
```bash
# Run universal setup script - handles platform-specific requirements
./setup/universal_setup.sh

# This will:
# - Detect your architecture (ARM64 for native Mac, x86_64 for Claude Code)
# - Create the appropriate virtual environment (venv or claude_venv)
# - Install correct package versions for your platform
# - Create .env from env-example if needed
```

### Manual Setup (if needed)
```bash
# For Claude Code (x86_64), use claude_venv:
python -m venv claude_venv
source claude_venv/bin/activate
pip install pydantic==2.11.7 pydantic-core==2.33.2
pip install -r setup/requirements.txt

# For native Mac (ARM64), use standard venv:
python -m venv venv
source venv/bin/activate
pip install -r setup/requirements.txt

# Configure environment
cp env-example .env
# Edit .env with API keys and database configuration

# Initialize database
python -m src.cli.main init
python -m src.cli.main seed  # Optional: add sample data

# Database initialization automatically creates:
# - Default "Headless-PM" project (ID: 1)
# - dashboard-user agent (project_pm role, senior level)
```

### Running the Application

#### Quick Start (Recommended)
```bash
# Activate your virtual environment first
source venv/bin/activate  # or source claude_venv/bin/activate

# Use the service management system for full control
./scripts/manage_services.sh start
```

#### Alternative Start Methods
```bash
# Check service status before starting
./scripts/manage_services.sh status

# Start with real-time monitoring
./scripts/manage_services.sh start && ./scripts/manage_services.sh status --watch
```

The service management system automatically:
- ✅ Validates Python 3.11+ requirement  
- ✅ Checks required packages are installed
- ✅ Creates .env from env-example if needed
- ✅ Tests database connection and runs migrations
- ✅ Initializes database if needed
- ✅ Checks port availability
- ✅ Starts server with proper configuration
- ✅ Starts only services with defined ports in .env
- ✅ Creates PID files for process management
- ✅ Provides health monitoring and log management

**Service Port Configuration:**
- Services are only started if their port is defined in `.env`
- To skip a service, remove or comment out its port variable:
  - `SERVICE_PORT` - API server (default: 6969)
  - `MCP_PORT` - MCP server (default: 6968) 
  - `DASHBOARD_PORT` - Web dashboard (default: 3001)

**Note**: Activate your virtual environment before running the start script.

### Advanced Service Management

For production use or advanced control, use the service management scripts:

```bash
# Start all services with pidfile management
./scripts/manage_services.sh start

# Stop all services
./scripts/manage_services.sh stop

# Check service status and health
./scripts/manage_services.sh status --detailed

# Monitor services in real-time
./scripts/manage_services.sh status --watch

# Restart specific service
./scripts/manage_services.sh restart api

# View service logs
./scripts/manage_services.sh logs dashboard
```

**Service Management Features:**
- **PID Management**: Each service tracked with pidfiles in `run/` directory
- **Health Monitoring**: HTTP health checks and resource monitoring
- **Log Management**: Individual log files per service
- **Graceful Shutdown**: SIGTERM first, SIGKILL if needed
- **Force Operations**: `--force` flag for immediate termination
- **Service-Specific Control**: Start/stop individual services

See `docs/SERVICE_MANAGEMENT.md` for complete documentation.

## Testing

### Running Tests
```bash
# IMPORTANT: Use the appropriate virtual environment for your platform
# For Claude Code (x86_64):
source claude_venv/bin/activate

# For native Mac (ARM64):
source venv/bin/activate

# Run all tests with coverage
python -m pytest --cov=src --cov-report=term-missing

# Run specific test files
python -m pytest tests/test_api.py -v
python -m pytest tests/test_models.py -v

# Run tests without coverage (faster)
python -m pytest -q

# Run specific test patterns
python -m pytest -k "test_name_pattern"
```

### Test Coverage Status
- **Current Tests**: Client integration tests
- **Test Location**: `tests/test_headless_pm_client.py`
- **Additional Testing**: Comprehensive test suite planned

### Test Architecture Notes
- API tests use temporary file-based SQLite databases (not in-memory) to avoid connection issues
- All models, enums, and services have comprehensive test coverage
- Tests include document creation, mention detection, service registry, and task lifecycle

## Architecture Overview

Headless PM is a REST API for LLM agent task coordination with document-based communication. Key architectural decisions:

1. **Multi-Project Support**: Isolated project contexts with proper foreign key relationships
2. **Document-Based Communication**: Agents communicate via documents with @mention support
3. **Service Registry**: Track running services with heartbeat monitoring and ping URLs
4. **Git Workflow Integration**: Major tasks use feature branches with PRs, minor tasks commit directly to main
5. **Changes Polling**: Efficient polling endpoint for agents to get updates since last check
6. **Role-Based System**: Five roles (frontend_dev, backend_dev, qa, architect, pm) with multiple agents per role
7. **Task Complexity**: Major/minor classification determines Git workflow (PR vs direct commit)
8. **Database Migrations**: Schema evolution support with automated migration runner
9. **Comprehensive Testing**: 78 tests with 71% coverage including full API testing

### Enhanced Features
- **Multi-Project Architecture**: Complete project isolation with proper relationships
- **Epic/Feature/Task Hierarchy**: Three-level project organization within projects
- **Enhanced Task Creation UI**: Complete Epic → Feature → Task creation flow from single dialog
  - Modal-on-modal UI pattern with + icons beside dropdowns
  - Automatic selection of newly created parent entities
  - No pre-existing Epic/Feature requirement for task creation
- **Automatic Agent Initialization**: dashboard-user agent created during database setup
- **Documents Table**: Agent communication with mention detection
- **Service Registry**: Track microservices with heartbeat monitoring and ping URLs
- **Mentions System**: @username notifications across documents and tasks
- **Changes API**: Polling endpoint returning changes since timestamp
- **Task Complexity**: Major/minor enum driving branching strategies
- **Connection Types**: Distinguish between MCP and client connections
- **Task Comments**: Collaborative discussion on tasks with @mentions
- **Python Client Helper**: Complete CLI interface (`headless_pm_client.py`)
- **MCP Server**: Natural language interface for Claude Code with token tracking
- **Database Migrations**: Schema evolution support with automated runner
- **Web Dashboard**: Real-time project overview with analytics and monitoring (Next.js 15.4.1)
- **Service Management**: Comprehensive pidfile-based process management system
- **Port-based Service Control**: Services only start if their port is defined in .env

## Project Structure

```
headless-pm/
├── src/                    # Source code
│   ├── api/               # FastAPI routes
│   ├── models/            # SQLModel database models
│   ├── services/          # Business logic
│   ├── cli/               # CLI commands
│   ├── mcp/               # MCP server implementation
│   └── main.py            # FastAPI app entry point
├── dashboard/             # Next.js web dashboard
│   ├── src/               # Dashboard source code
│   └── package.json       # Dashboard dependencies
├── projects/              # Project-specific directories
│   └── {project_name}/    # Individual project workspace (sanitized name)
│       ├── docs/          # Project documentation (API-managed)
│       ├── shared/        # Shared project files
│       └── instructions/  # Agent instructions for project
├── tests/                 # Test files
├── migrations/            # Database migration scripts
│   ├── add_agent_status_column.py
│   ├── add_project_support.py
│   └── run_migrations.py  # Migration runner
├── agent_instructions/    # Per-role markdown instructions
├── agents/                # Agent tools and installers
│   ├── claude/            # Claude Code specific tools
│   ├── client/            # Client tools and utilities
│   └── mcp/               # MCP-specific agent instructions
├── scripts/               # Service management scripts
│   ├── manage_services.sh # Main service control
│   ├── start_services.sh  # Start with pidfiles
│   ├── stop_services.sh   # Stop and cleanup
│   └── check_services.sh  # Health monitoring
├── setup/                 # Installation and setup scripts
├── docs/                  # Application documentation
│   ├── dashboard/         # Dashboard-specific docs
│   └── images/            # Dashboard screenshots
└── headless_pm_client.py  # Python CLI client
```

## Key API Endpoints

### Project Management
- `POST /api/v1/projects` - Create new project (PM/Architect only)
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project (PM/Architect only)
- `DELETE /api/v1/projects/{id}` - Delete project (PM only)

### Core Task Management
- `POST /api/v1/register` - Register agent with role/skill level and connection type
- `GET /api/v1/context` - Get project context and paths
- `DELETE /api/v1/agents/{agent_id}` - Delete agent (PM only)

### Epic/Feature/Task Endpoints
- `POST /api/v1/epics` - Create epic (PM/Architect only)
- `GET /api/v1/epics` - List epics with progress tracking
- `DELETE /api/v1/epics/{id}` - Delete epic (PM only)
- `POST /api/v1/features` - Create feature under epic
- `GET /api/v1/features/{epic_id}` - List features for epic
- `DELETE /api/v1/features/{id}` - Delete feature
- `POST /api/v1/tasks/create` - Create new task with complexity (major/minor)
- `GET /api/v1/tasks/next` - Get next available task for role
- `POST /api/v1/tasks/{id}/lock` - Lock task to prevent duplicate work
- `PUT /api/v1/tasks/{id}/status` - Update task status
- `POST /api/v1/tasks/{id}/comment` - Add comment with @mention support

### Document Communication
- `POST /api/v1/documents` - Create document with auto @mention detection
- `GET /api/v1/documents` - List documents with filtering
- `GET /api/v1/mentions` - Get mentions for an agent

### Service Registry
- `POST /api/v1/services/register` - Register a service with optional ping URL
- `GET /api/v1/services` - List all services with health status
- `POST /api/v1/services/{name}/heartbeat` - Send service heartbeat
- `DELETE /api/v1/services/{name}` - Unregister service

### Project Documentation
- `GET /api/v1/projects/{id}/docs` - List project documentation files
- `GET /api/v1/projects/{id}/docs/{file_path}` - Get project documentation file  
- `POST /api/v1/projects/{id}/docs/{file_path}` - Create/update project documentation file

**Security Features:**
- All filenames and paths are sanitized for security
- Shell special characters are removed
- Path traversal attacks prevented
- Input validation prevents injection attacks

### Changes & Updates
- `GET /api/v1/changes` - Poll for changes since timestamp
- `GET /api/v1/changelog` - Get recent task status changes

## Technology Stack

- **FastAPI** - REST API framework
- **SQLModel** - ORM combining SQLAlchemy + Pydantic  
- **Pydantic 2.11.7** - Data validation (version-locked for compatibility)
- **SQLite/MySQL** - Database options with migration support
- **Next.js 15.4.1** - Web dashboard framework with Turbopack
- **React 19.1.0** - Frontend library
- **Python 3.11+** - Runtime requirement

## Database Migrations

The system includes automated migration support:

### Running Migrations
```bash
# Run all pending migrations
python migrations/run_migrations.py

# Run specific migration
python migrations/add_project_support.py

# Check database health
python -m src.cli.main sanity-check
```

### Available Migrations
- `add_agent_status_column.py` - Adds agent status tracking
- `add_project_support.py` - Adds multi-project architecture
- `run_migrations.py` - Orchestrates migration execution

### Migration Features
- **Foreign Key Constraint Handling** - Safe table modifications
- **Data Preservation** - Existing data maintained during schema changes  
- **Rollback Support** - Safe restoration capabilities
- **Validation** - Post-migration sanity checks

## Development Notes

### Implementation Status
- ✅ **Fully Implemented**: Complete REST API with all endpoints
- ✅ **Database Models**: SQLModel with proper relationships
- ✅ **CLI Interface**: Full command-line management tools
- ✅ **Web Dashboard**: Next.js dashboard with real-time updates
- ✅ **Testing**: 78 tests with 71% coverage
- ✅ **Documentation**: Agent instructions and workflow guides

### Key Implementation Details
- **Task Organization**: Epic → Feature → Task hierarchy with complete UI creation flow
- **Task Creation**: Enhanced UI allows creating entire hierarchy from single dialog
- **Task Difficulty Levels**: junior, senior, principal
- **Task Complexity**: major (requires PR), minor (direct commit)
- **Agent Communication**: Via documents with @mention detection
- **Agent Types**: Client connections and MCP connections
- **Agent Initialization**: dashboard-user automatically created during database setup
- **Project Support**: Dynamic project_id resolution, no hardcoded values
- **Service Monitoring**: Heartbeat-based health tracking with optional ping URLs
- **Change Detection**: Efficient polling since timestamp
- **Git Integration**: Automated workflow based on task complexity
- **Database**: SQLModel for type safety, supports SQLite and MySQL
- **API Validation**: Pydantic models for all request/response data
- **MCP Transport**: Multiple protocols (HTTP, SSE, WebSocket, STDIO)
- **Token Tracking**: Usage statistics for MCP sessions

### Testing Environment
- Use `claude_venv` for all testing to ensure compatibility
- API tests use temporary file-based SQLite databases
- Run `python -m pytest tests/` for running tests
- Client integration tests implemented in `test_headless_pm_client.py`

## Python Client Helper

The `headless_pm_client.py` provides a complete CLI interface to the API:

### Basic Usage
```bash
# Register an agent
./headless_pm_client.py register --agent-id "dev_001" --role "backend_dev" --level "senior"

# Work with epics/features/tasks
./headless_pm_client.py epics create --name "Authentication" --description "User auth system"
./headless_pm_client.py tasks next --role backend_dev --level senior
./headless_pm_client.py tasks lock 123 --agent-id "dev_001"
./headless_pm_client.py tasks status 123 --status "dev_done" --agent-id "dev_001"

# Communicate with team
./headless_pm_client.py documents create --type "update" --title "Progress" \
  --content "Completed login API @qa_001 please test" --author-id "dev_001"
  
# Check for updates
./headless_pm_client.py mentions --agent-id "dev_001"
./headless_pm_client.py changes --since 1736359200 --agent-id "dev_001"
```

### Client Features
- Automatic `.env` file loading for API keys
- Comprehensive help with `--help` flag
- Support for all API endpoints
- Embedded agent instructions
- Multiple API key sources (checks in priority order)

## Connection Types

Agents can register with two connection types:

### CLIENT Connection
- Default for agents using the API directly
- Use when registering via `headless_pm_client.py` or direct API calls
- Example: `./headless_pm_client.py register --agent-id "dev_001" --role "backend_dev"`

### MCP Connection  
- Automatically set when using MCP server
- Used by Claude Code integration
- Provides natural language interface
- Token usage tracking included

The connection type helps distinguish between different agent interfaces and enables appropriate features for each type.

### Memories
- 8000 port is for another service entirely, leave that alone!

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
NEVER use "Claude Code" references in commit messages or generated content. Use "ocontant <ocontant@users.noreply.github.com>" as the Co-Authored-By tag instead.
