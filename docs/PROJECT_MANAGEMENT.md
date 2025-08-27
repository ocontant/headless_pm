# Project Management Guide

This guide explains the multi-project architecture and management features in Headless PM.

## Overview

Headless PM supports multiple isolated projects, each with their own set of epics, features, tasks, and agents. This enables clear separation of concerns and parallel development across different projects.

## Project Architecture

### Project Isolation
- **Complete Isolation**: Projects have separate epics, features, tasks, and documents
- **Agent Flexibility**: Agents can work across multiple projects
- **Proper Foreign Keys**: Database relationships maintain referential integrity
- **Default Project**: System creates "Headless-PM" project during initialization

### Project Hierarchy
```
Project
├── Epics
│   ├── Features
│   │   └── Tasks
│   └── Features
│       └── Tasks
├── Documents
├── Agent Assignments
└── Service Registry
```

## Project Management API

### Create Project
**POST** `/api/v1/projects`

```json
{
  "name": "My New Project",
  "description": "Project description",
  "repository_url": "https://github.com/user/repo",
  "status": "active"
}
```

**Permissions**: PROJECT_PM, Architect, and UI_ADMIN roles only

### List Projects
**GET** `/api/v1/projects`

Returns all projects with basic information:
```json
[
  {
    "id": 1,
    "name": "Headless-PM",
    "description": "Default project",
    "status": "active",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Get Project Details
**GET** `/api/v1/projects/{id}`

Returns detailed project information including statistics:
```json
{
  "id": 1,
  "name": "Headless-PM", 
  "description": "Default project",
  "repository_url": "https://github.com/user/repo",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z",
  "epic_count": 5,
  "feature_count": 12,
  "task_count": 47,
  "active_agent_count": 3
}
```

### Update Project
**PUT** `/api/v1/projects/{id}`

Update project details (PM/Architect only):
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "inactive"
}
```

### Delete Project
**DELETE** `/api/v1/projects/{id}`

**Permissions**: PM role only
**Warning**: This permanently deletes all project data including epics, features, tasks, and documents.

## Project Status

Projects can have the following statuses:
- `active` - Currently active development
- `inactive` - Temporarily suspended
- `completed` - Project finished
- `archived` - Long-term storage

## CLI Integration

The `headless_pm_client.py` supports project management:

```bash
# List projects
./headless_pm_client.py projects list

# Create project
./headless_pm_client.py projects create --name "New Project" --description "Description"

# Get project details
./headless_pm_client.py projects get --id 1

# Update project
./headless_pm_client.py projects update --id 1 --status "completed"

# Delete project (PM only)
./headless_pm_client.py projects delete --id 1
```

## MCP Integration

When using the MCP server, set the project context:

```json
{
  "env": {
    "MCP_PROJECT_ID": "1"
  }
}
```

This ensures all MCP operations are scoped to the specified project.

## Web Dashboard

The Next.js dashboard provides a complete project management interface:

### Features
- **Project Selector**: Switch between projects in the navigation
- **Project Overview**: Statistics and progress tracking
- **Project Settings**: Edit project details
- **Project Creation**: Create new projects with validation
- **Bulk Operations**: Manage multiple projects

### Navigation
- Projects are accessible via the project selector in the top navigation
- Current project context is maintained across dashboard pages
- Project-specific URLs for direct access

## Database Schema

### Project Table
```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    repository_url VARCHAR(512),
    status VARCHAR(50) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Foreign Key Relationships
- `epic.project_id` → `project.id`
- `feature.project_id` → `project.id` (via epic)
- `task.project_id` → `project.id` (via feature)
- `document.project_id` → `project.id`

## Migration to Multi-Project

### Automatic Migration
The `add_project_support.py` migration:
1. Creates the project table
2. Adds project_id columns to existing tables
3. Creates default "Headless-PM" project
4. Associates existing data with default project
5. Updates foreign key constraints

### Data Safety
- **Backup**: Existing data is preserved
- **Validation**: Post-migration checks verify integrity
- **Rollback**: Restoration scripts available if needed
- **Dashboard User Creation**: Auto-creates dashboard-user for all projects with UI_ADMIN role

## Best Practices

### Project Organization
- Use descriptive project names
- Include repository URLs for code projects
- Set appropriate status based on development phase
- Use projects to separate different applications/services

### Agent Management
- Agents can work across multiple projects
- Use project context in agent instructions
- Consider project-specific skill requirements

### Task Assignment
- All tasks inherit project context from their feature
- Cross-project task dependencies should be minimized
- Use documents for cross-project communication

## Troubleshooting

### Common Issues

#### Project Not Found
```json
{
  "detail": "Project not found"
}
```
**Solution**: Verify project ID and ensure project exists

#### Permission Denied
```json
{
  "detail": "Only PM and Architect roles can create projects"
}
```
**Solution**: Use appropriate role for project management operations

#### Foreign Key Constraint
```json
{
  "detail": "Cannot delete project with existing epics"
}
```
**Solution**: Delete associated epics/features/tasks before deleting project

### Database Issues
```bash
# Check project data integrity
python -m src.cli.main sanity-check

# Restore from backup if needed
python scripts/restore_projects.py
```

## Security Considerations

### Access Control
- Project creation limited to PM/Architect roles
- Project deletion limited to PM role only
- Project updates restricted to authorized roles

### Data Isolation
- Project data is properly isolated in database
- API endpoints enforce project-based filtering
- Cross-project access requires explicit permission

### Audit Trail
- All project changes are logged
- Creation and modification timestamps tracked
- User actions associated with agent IDs