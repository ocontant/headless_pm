# Headless PM API Server

FastAPI-based REST API server for the Headless PM project management system.

## Overview

The API server provides RESTful endpoints for:
- Agent management and registration
- Task creation, assignment, and status tracking
- Project management with Epic/Feature/Task hierarchy
- Document-based communication with @mention support
- Service registry with health monitoring
- Change polling for real-time updates

## Architecture

```
api/
├── src/
│   ├── main.py              # FastAPI application entry point
│   └── routes/              # API route handlers
│       ├── routes.py        # Core agent/task endpoints
│       ├── project_routes.py   # Project management
│       ├── document_routes.py  # Document communication
│       ├── service_routes.py   # Service registry
│       ├── mention_routes.py   # Mention system
│       ├── changes_routes.py   # Change polling
│       ├── dependencies.py     # Auth, middleware
│       └── schemas.py          # Pydantic schemas
├── Dockerfile              # Container definition
└── README.md              # This file
```

## Dependencies

The API server depends on shared components:
- `shared/models/` - Database models and enums
- `shared/services/` - Business logic services
- `shared/schemas/` - Request/response schemas

## Environment Variables

- `PORT` - Server port (default: 6969)
- `DATABASE_URL` - Database connection string
- `PYTHONPATH` - Python module path

## Running

### With Docker (Recommended)
```bash
# From project root
docker-compose up api
```

### Development Mode
```bash
# From project root, with virtual environment activated
python -m api.src.main
```

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with service info
- `GET /health` - Health check with database status
- `GET /status` - Detailed status with metrics

### Agent Management
- `POST /api/v1/register` - Register agent
- `GET /api/v1/context` - Get project context
- `DELETE /api/v1/agents/{id}` - Delete agent

### Task Management
- `POST /api/v1/tasks/create` - Create task
- `GET /api/v1/tasks/next` - Get next available task
- `POST /api/v1/tasks/{id}/lock` - Lock task
- `PUT /api/v1/tasks/{id}/status` - Update task status
- `POST /api/v1/tasks/{id}/comment` - Add comment

### Project Management
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

See `/api/v1/docs` for complete API documentation.

## Health Monitoring

The API server includes comprehensive health monitoring:
- Database connection health
- Service metrics (agents, tasks, projects)
- Resource usage tracking
- Dependency status

## Security

- CORS enabled for cross-origin requests
- Input validation via Pydantic schemas
- SQL injection protection via SQLModel
- File system security for project documents

## Database

Uses SQLite by default with support for MySQL/PostgreSQL. Database file is stored outside the container in the `database/` directory for persistence.

## Logging

Logs are written to stdout and can be viewed with:
```bash
docker-compose logs api
```

## Development

For development with hot reload:
```bash
# From project root
PYTHONPATH=/app python -m api.src.main --reload
```

## Testing

Run tests from project root:
```bash
python -m pytest tests/ -v
```