# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

### Claude Code Virtual Environment (REQUIRED!)
For Claude Code development, use the specialized virtual environment:

```bash
# Create Claude-specific virtual environment
./setup/create_claude_venv.sh

# Activate Claude virtual environment
source claude_venv/bin/activate

# Verify installation
python --version  # Should show Python 3.11.0
which python      # Should point to claude_venv/bin/python
```

### Standard Development Environment (outside Claude Code)
For general development:

```bash
# Setup virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r setup/requirements.txt

# Configure environment
cp env-example .env
# Edit .env with API keys and database configuration

# Initialize database
python -m src.cli.main init
python -m src.cli.main seed  # Optional: add sample data
```

### Running the Application

#### Quick Start (Recommended)
```bash
# Activate your virtual environment first
source venv/bin/activate  # or source claude_venv/bin/activate

# Use the automated start script (checks environment, DB, starts server)
./start.sh
```

#### Manual Start
```bash
# Run API server
uvicorn src.main:app --reload --port 6969

# Or use the CLI to start server
python -m src.cli.main serve --port 6969
```

The `start.sh` script automatically:
- ✅ Validates Python 3.11+ requirement  
- ✅ Checks required packages are installed
- ✅ Creates .env from env-example if needed
- ✅ Tests database connection
- ✅ Initializes database if needed
- ✅ Checks port availability
- ✅ Starts server with proper configuration

**Note**: Activate your virtual environment before running the start script.

## CLI Commands

### Project Management
```bash
# Show project status
python -m src.cli.main status

# Show task assignments
python -m src.cli.main tasks

# Show registered agents
python -m src.cli.main agents

# Show services
python -m src.cli.main services

# Show documents
python -m src.cli.main documents

# Real-time dashboard
python -m src.cli.main dashboard
```

### Database Management
```bash
# Initialize database (create tables)
python -m src.cli.main init

# Reset database (deletes all data)
python -m src.cli.main reset

# Seed with sample data
python -m src.cli.main seed
```

## Testing

### Running Tests
```bash
# IMPORTANT: Always use Claude virtual environment for testing
source claude_venv/bin/activate

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
- **Total Tests**: 78 (all passing)
- **Overall Coverage**: 71%
- **Models & Services**: 100% coverage
- **API Routes**: 53-79% coverage
- **CLI**: 83% coverage

### Test Architecture Notes
- API tests use temporary file-based SQLite databases (not in-memory) to avoid connection issues
- All models, enums, and services have comprehensive test coverage
- Tests include document creation, mention detection, service registry, and task lifecycle

## Architecture Overview

Headless PM is a REST API for LLM agent task coordination with document-based communication. Key architectural decisions:

1. **Document-Based Communication**: Agents communicate via documents with @mention support
2. **Service Registry**: Track running services with heartbeat monitoring
3. **Git Workflow Integration**: Major tasks use feature branches with PRs, minor tasks commit directly to main
4. **Changes Polling**: Efficient polling endpoint for agents to get updates since last check
5. **Role-Based System**: Five roles (frontend_dev, backend_dev, qa, architect, pm) with multiple agents per role
6. **Task Complexity**: Major/minor classification determines Git workflow (PR vs direct commit)
7. **Comprehensive Testing**: 78 tests with 71% coverage including full API testing

### Enhanced Features (Added from Feedback)
- **Documents Table**: Agent communication with mention detection
- **Service Registry**: Track microservices with heartbeat monitoring  
- **Mentions System**: @username notifications across documents and tasks
- **Changes API**: Polling endpoint returning changes since timestamp
- **Task Complexity**: Major/minor enum driving branching strategies

## Project Structure

```
headless-pm/
├── src/                    # Source code (to be implemented)
│   ├── api/               # FastAPI routes
│   ├── models/            # SQLModel database models
│   ├── services/          # Business logic
│   ├── cli/               # CLI commands
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test files (to be created)
├── agent_instructions/    # Per-role markdown instructions
├── setup/                 # Installation and setup scripts
└── docs/                  # Project documentation
```

## Key API Endpoints

### Core Task Management
- `POST /api/v1/register` - Register agent with role/skill level
- `GET /api/v1/context` - Get project context and paths
- `POST /api/v1/tasks/create` - Create new task with complexity (major/minor)
- `GET /api/v1/tasks/next` - Get next available task for role
- `POST /api/v1/tasks/{id}/lock` - Lock task to prevent duplicate work
- `PUT /api/v1/tasks/{id}/status` - Update task status
- `POST /api/v1/tasks/{id}/evaluate` - Approve/reject task (architect/pm only)

### Document Communication
- `POST /api/v1/documents` - Create document with auto @mention detection
- `GET /api/v1/documents` - List documents with filtering
- `GET /api/v1/mentions` - Get mentions for an agent

### Service Registry
- `POST /api/v1/services/register` - Register a service
- `GET /api/v1/services` - List all services
- `POST /api/v1/services/{name}/heartbeat` - Send service heartbeat

### Changes & Updates
- `GET /api/v1/changes` - Poll for changes since timestamp
- `GET /api/v1/changelog` - Get recent task status changes

## Technology Stack

- **FastAPI** - REST API framework
- **SQLModel** - ORM combining SQLAlchemy + Pydantic
- **Pydantic** - Data validation
- **SQLite/MySQL** - Database options
- **Python 3.11+** - Runtime requirement

## Development Notes

### Implementation Status
- ✅ **Fully Implemented**: Complete REST API with all endpoints
- ✅ **Database Models**: SQLModel with proper relationships
- ✅ **CLI Interface**: Full command-line management tools
- ✅ **Testing**: 78 tests with 71% coverage
- ✅ **Documentation**: Agent instructions and workflow guides

### Key Implementation Details
- **Task Difficulty Levels**: junior, senior, principal
- **Task Complexity**: major (requires PR), minor (direct commit)
- **Agent Communication**: Via documents with @mention detection
- **Service Monitoring**: Heartbeat-based health tracking
- **Change Detection**: Efficient polling since timestamp
- **Git Integration**: Automated workflow based on task complexity
- **Database**: SQLModel for type safety, supports SQLite and MySQL
- **API Validation**: Pydantic models for all request/response data

### Testing Environment
- Use `claude_venv` for all testing to ensure compatibility
- API tests use temporary file-based SQLite databases
- Run `python -m pytest --cov=src --cov-report=term-missing` for full coverage
- All core business logic has 100% test coverage
