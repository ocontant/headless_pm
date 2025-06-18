# MCP Agent Instructions for Headless PM

This directory contains role-specific instructions for agents using the Model Context Protocol (MCP) integration.

## Overview

MCP provides a standardized way to interact with Headless PM through natural language commands. Instead of writing code, you can use conversational commands to manage tasks, create documents, and coordinate with other agents.

## Getting Started

1. **Ensure MCP Server is Running:**
   ```bash
   cd /path/to/headless-pm
   ./start.sh  # This starts both API and MCP servers
   ```

2. **Available MCP Tools:**
   - `register_agent` - Register yourself with a role and skill level
   - `get_project_context` - Get project information
   - `get_next_task` - Find available tasks for your role
   - `create_task` - Create new tasks
   - `lock_task` - Lock a task to work on it
   - `update_task_status` - Update task progress
   - `create_document` - Create documents with @mentions
   - `get_mentions` - Check for mentions and notifications
   - `register_service` - Register microservices
   - `send_heartbeat` - Send service health updates
   - `poll_changes` - Check for system changes

3. **Available MCP Resources:**
   - `headless-pm://tasks/list` - Current tasks
   - `headless-pm://agents/list` - Active agents
   - `headless-pm://documents/recent` - Recent documents
   - `headless-pm://services/status` - Service health
   - `headless-pm://changelog/recent` - Recent activity
   - `headless-pm://context/project` - Project context

## Example MCP Workflows

### Initial Registration
```
"Register me as agent 'claude_backend_01' with role 'backend_dev' and skill level 'senior'"
```

### Task Management
```
"Get the project context"
"Show me the next available task for my role"
"Lock task 42 for me"
"Update task 42 status to 'under_work' with notes 'Starting implementation'"
"Update task 42 status to 'dev_done' with notes 'Feature complete, all tests passing'"
```

### Communication
```
"Create a document titled 'API Design Complete' with content describing the new endpoints, mentioning ['architect_001', 'frontend_001']"
"Check if I have any mentions"
```

### Service Management
```
"Register service 'user-api' at 'http://localhost:8001' with health check at '/health'"
"Send heartbeat for service 'user-api' with status 'healthy'"
```

## Role-Specific Workflows

Each role has specific MCP instructions:

- **backend_dev.md** - Backend development workflows
- **frontend_dev.md** - Frontend development workflows  
- **architect.md** - Architecture and design workflows
- **qa.md** - Quality assurance workflows
- **pm.md** - Project management workflows

## Task Complexity and Git Workflow

- **Minor Tasks**: Can be committed directly to main branch
- **Major Tasks**: Require feature branches and pull requests

The MCP server will guide you through the appropriate workflow based on task complexity.

## Best Practices

1. **Registration First**: Always register before attempting other operations
2. **Lock Before Work**: Always lock tasks before starting work
3. **Status Updates**: Update task status as you progress through work
4. **Documentation**: Create documents to communicate important information
5. **Mentions**: Use @mentions in documents to notify specific team members
6. **Regular Polling**: Check for mentions and changes periodically

## Field Usage

The system supports unlimited text in key fields:
- Task descriptions
- Document content  
- Status update notes
- Comments

Use these fields to provide comprehensive information that helps the team work efficiently.

## Troubleshooting

- **Connection Issues**: Ensure the MCP server is running (check `./start.sh` output)
- **Registration Failed**: Check that your role is valid (frontend_dev, backend_dev, architect, qa, pm)
- **Task Not Found**: Tasks may be locked by other agents or filtered by skill level
- **Tool Errors**: Check the error message for specific requirements (e.g., missing parameters)

## Additional Resources

- API Documentation: http://localhost:6969/api/v1/docs
- Project Dashboard: `python -m src.cli.main dashboard`
- Integration Guide: `/INTEGRATION.md`