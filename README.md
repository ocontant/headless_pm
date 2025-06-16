# Headless PM - LLM Agent Task Coordination API

A comprehensive REST API for coordinating LLM agents in software development projects with document-based communication, service registry, and Git workflow integration.

You would usually create several copies of a repository locally, giving each agent a different directory to work in. Each agent can then register itself, retrieve tasks, communicate through the API, and finally commit to GIT.

I use this with Claude Code, but it should work with any LLM Agent. 

## ⚡ Quick Start

```bash
# Clone, setup environment, and start the API server
git clone <repository>
cd headless-pm

# Setup virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r setup/requirements.txt

# Start the server (handles database setup automatically)
./start.sh
```

The start script automatically checks dependencies, initializes database, and starts the server on `http://localhost:6969`.

## 🚀 Features

### Core Task Management
- **Role-based task assignment** with skill levels (junior, senior, principal)
- **Task complexity workflows** (major → PR required, minor → direct commit)
- **Complete task lifecycle** with status tracking and evaluation
- **Git branch integration** with automated workflow decisions

### Agent Communication
- **Document-based messaging** with automatic @mention detection
- **Notification system** for cross-agent communication
- **Changes polling** for efficient real-time updates
- **Activity feed** with comprehensive changelog

### Service Management
- **Service registry** for tracking microservices
- **Heartbeat monitoring** with automatic status detection
- **Health dashboard** for system overview

### Developer Experience
- **Real-time CLI dashboard** for project monitoring
- **Comprehensive test suite** (78 tests, 71% coverage)
- **Agent instruction system** with Git workflow guidance
- **Sample workflows** and examples

## 🏗️ Architecture

- **FastAPI** REST API with OpenAPI documentation
- **SQLModel** ORM with SQLite/MySQL support
- **Document-driven** agent communication
- **Polling-based** updates (no WebSockets)
- **File-based** agent instructions
- **Stateless** agent design

## 🚀 Quick Start

### 1. Environment Setup

**For Claude Code (Recommended):**
```bash
# Create Claude-specific virtual environment
./setup/create_claude_venv.sh
source claude_venv/bin/activate
```

**For Standard Development:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r setup/requirements.txt
```

### 2. Configuration
```bash
# Configure environment
cp env-example .env
# Edit .env with your settings

# Initialize database
python -m src.cli.main init
python -m src.cli.main seed  # Optional: add sample data
```

### 3. Run Application
```bash
# Start API server
uvicorn src.main:app --reload --port 6969

# Or use CLI
python -m src.cli.main serve --port 6969
```

### 4. Monitor with Dashboard
```bash
# Real-time CLI dashboard
python -m src.cli.main dashboard
```

## 📖 API Documentation

### Core Endpoints
- `POST /api/v1/register` - Register agent with role/level
- `GET /api/v1/context` - Get project configuration
- `POST /api/v1/tasks/create` - Create task (with complexity: major/minor)
- `GET /api/v1/tasks/next` - Get next available task for role
- `POST /api/v1/tasks/{id}/lock` - Lock task to prevent conflicts
- `PUT /api/v1/tasks/{id}/status` - Update task progress
- `POST /api/v1/tasks/{id}/evaluate` - Approve/reject tasks (architect/PM)

### Communication
- `POST /api/v1/documents` - Create document with @mention detection
- `GET /api/v1/documents` - List documents with filtering
- `GET /api/v1/mentions` - Get notifications for agent

### Service Registry
- `POST /api/v1/services/register` - Register service
- `POST /api/v1/services/{name}/heartbeat` - Send heartbeat
- `GET /api/v1/services` - List all services

### Updates
- `GET /api/v1/changes` - Poll changes since timestamp
- `GET /api/v1/changelog` - Get recent activity

## 🎯 Task Workflows

### Major Tasks (Feature Development)
```bash
git checkout -b feature/task-name
# ... development work ...
git push origin feature/task-name
# Create PR for review
```

### Minor Tasks (Bug Fixes, Config)
```bash
git checkout main
# ... quick changes ...
git commit -m "fix: description"
git push origin main
```

## 🧪 Testing

**Always use Claude virtual environment for testing:**

```bash
source claude_venv/bin/activate

# Run all tests with coverage
python -m pytest --cov=src --cov-report=term-missing

# Run specific test files
python -m pytest tests/test_api.py -v
python -m pytest tests/test_models.py -v

# Quick test run
python -m pytest -q
```

**Test Coverage:**
- **78 tests** (100% passing)
- **71% overall coverage**
- **100% coverage** on models and core services
- **Comprehensive API testing** with all endpoints

## 🛠️ CLI Commands

### Project Management
```bash
python -m src.cli.main status     # Project overview
python -m src.cli.main tasks      # List tasks
python -m src.cli.main agents     # Show agents
python -m src.cli.main services   # Service status
python -m src.cli.main documents  # Recent documents
python -m src.cli.main dashboard  # Real-time monitoring
```

### Database Management
```bash
python -m src.cli.main init   # Create database tables
python -m src.cli.main reset  # Reset all data
python -m src.cli.main seed   # Add sample data
```

## 📁 Project Structure

```
headless-pm/
├── src/
│   ├── api/                 # FastAPI routes and schemas
│   ├── models/             # SQLModel database models
│   ├── services/           # Business logic and utilities
│   ├── cli/               # Command-line interface
│   └── main.py            # FastAPI application
├── tests/                 # Comprehensive test suite
├── agent_instructions/    # Role-specific agent guides
├── examples/             # Sample workflows and demos
├── setup/               # Installation and setup scripts
└── docs/               # Project documentation
```

## 🤖 Agent Roles

- **Architect** - System design and task evaluation
- **Project Manager** - Task creation and coordination
- **Frontend Developer** - UI/UX implementation
- **Backend Developer** - API and service development
- **QA Engineer** - Testing and quality assurance

Each role has detailed instructions in `/agent_instructions/` with:
- Role responsibilities
- Git workflow guidance
- Communication patterns
- Tool usage examples

## 🔧 Technology Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQLAlchemy + Pydantic ORM
- **SQLite/MySQL** - Database options
- **Pydantic** - Data validation and serialization
- **Typer** - CLI framework
- **Rich** - Terminal formatting
- **Pytest** - Testing framework

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Claude Code specific guidance
- **[PROJECT_BRIEF.md](PROJECT_BRIEF.md)** - Detailed system overview
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Development patterns
- **[SAMPLE_AGENT_WORKFLOW.md](docs/SAMPLE_AGENT_WORKFLOW.md)** - Usage examples
- **[Agent Instructions](agent_instructions/)** - Role-specific guides

## 🚦 Getting Started for Agents

1. **Register** your agent with role and skill level
2. **Get context** to understand the project setup
3. **Poll for tasks** using `/api/v1/tasks/next`
4. **Lock tasks** before starting work
5. **Update status** as you progress
6. **Communicate** via documents with @mentions
7. **Follow Git workflows** based on task complexity

## 🔍 Example Agent Workflow

```python
# See examples/agent_workflow_example.py for complete implementation
agent = HeadlessPMAgent("frontend_dev_001", "frontend_dev", "senior")
agent.register()
task = agent.get_next_task()
if task:
    agent.lock_task(task['id'])
    agent.update_task_status(task['id'], "under_work")
    # ... do work ...
    agent.update_task_status(task['id'], "dev_done")
```

## 🤝 Contributing

1. Use the Claude virtual environment for development
2. Run tests before submitting changes
3. Follow the established patterns in the codebase
4. Update documentation for new features

## 📄 License

MIT License - see LICENSE file for details. @ Timo Railo, 2025
