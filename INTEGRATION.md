# Headless PM Integration Setup Guide

This guide provides complete setup instructions for both integration options: the lightweight Python client and the MCP server implementation.

## Prerequisites

- Python 3.10+ installed
- Headless PM server running on `http://localhost:6969`
- For MCP: Claude Code installed or another MCP-compatible client

## Option 1: Lightweight Python Client Integration

### Installation

1. **Save the client code** as `headless_pm_client.py` in your project directory

2. **Install dependencies:**
```bash
pip install requests
```

3. **Basic usage in Claude Code:**
```python
from headless_pm_client import claude_register, TaskStatus

# Quick registration and workflow
client = claude_register("claude_001", "backend_dev", "senior")

# Get next task
task = client.get_next_task()
if task:
    print(f"Working on: {task.title}")
    
    # Lock and start work
    client.lock_task(task.id)
    client.update_task_status(task.id, TaskStatus.UNDER_WORK)
    
    # After completing work
    client.update_task_status(task.id, TaskStatus.DEV_DONE, 
                             notes="Feature implemented with tests")
    
    # Document the work
    client.create_document(
        title=f"Completed: {task.title}",
        content="Implementation details and notes",
        mentions=["architect_001"]
    )
```

### Advanced Usage Examples

#### 1. Multi-Agent Coordination
```python
from headless_pm_client import HeadlessPMClient, TaskStatus, TaskComplexity

# Frontend agent
frontend_client = HeadlessPMClient(
    agent_id="claude_frontend", 
    role="frontend_dev", 
    skill_level="senior"
)
frontend_client.register()

# Backend agent
backend_client = HeadlessPMClient(
    agent_id="claude_backend", 
    role="backend_dev", 
    skill_level="senior"
)
backend_client.register()

# Create coordinated tasks
backend_task = backend_client.create_task(
    title="Create API endpoint for user management",
    description="Implement REST API for CRUD operations on users",
    complexity=TaskComplexity.MAJOR
)

frontend_task = frontend_client.create_task(
    title="Build user management UI",
    description="Create React components for user management",
    complexity=TaskComplexity.MAJOR
)

# Cross-team communication
backend_client.create_document(
    title="API Specification Ready",
    content=f"The user management API is complete. Frontend team can now integrate.\n\nAPI endpoint: /api/users\nDocs: http://localhost:8000/docs",
    mentions=["claude_frontend"]
)
```

#### 2. Service Registration and Monitoring
```python
# Register a microservice
client.register_service(
    service_name="user_service",
    service_url="http://localhost:8001",
    health_check_url="http://localhost:8001/health"
)

# Send periodic heartbeats
import time
while True:
    client.send_heartbeat("user_service", "healthy")
    time.sleep(30)  # Every 30 seconds
```

#### 3. Real-time Change Monitoring
```python
import datetime

# Poll for changes since last check
last_check = datetime.datetime.now().isoformat()

while True:
    changes = client.poll_changes(since_timestamp=last_check)
    
    if changes.get('has_changes'):
        print("New changes detected:")
        for change in changes.get('changes', []):
            print(f"- {change['type']}: {change['description']}")
    
    last_check = datetime.datetime.now().isoformat()
    time.sleep(10)  # Check every 10 seconds
```

## Option 2: MCP Server Integration

### Installation

1. **Install MCP dependencies:**
```bash
pip install mcp httpx
```

2. **Save the MCP server code** as `headless_pm_mcp_server.py`

3. **Create MCP configuration file** `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "headless-pm": {
      "command": "python",
      "args": ["-m", "headless_pm_mcp_server"],
      "env": {
        "HEADLESS_PM_URL": "http://localhost:6969"
      }
    }
  }
}
```

4. **For Claude Code integration**, add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "headless-pm": {
      "command": "python",
      "args": ["/path/to/your/project/headless_pm_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

### Using MCP Tools in Claude Code

Once configured, you can use natural language commands in Claude Code:

```
# Register as an agent
Please register me as agent "claude_mcp_001" with role "backend_dev" and skill level "senior"

# Get project context
What's the current project context?

# Work with tasks
Get my next available task
Lock task 123
Update task 123 status to "under_work" with notes "Starting implementation"
Update task 123 status to "dev_done" with notes "Feature complete, tests passing"

# Create documentation
Create a document titled "API Implementation Complete" with content describing the new user endpoint, mentioning architect_001

# Check for mentions
Do I have any new mentions or notifications?

# Monitor services
Register service "payment_api" at "http://localhost:8002" with health check at "/health"
Send heartbeat for service "payment_api"
```

### MCP Resources

The MCP server also provides resources that Claude can access:

- **Current Tasks**: `headless-pm://tasks/list`
- **Active Agents**: `headless-pm://agents/list`  
- **Recent Documents**: `headless-pm://documents/recent`
- **Service Status**: `headless-pm://services/status`
- **Recent Activity**: `headless-pm://changelog/recent`
- **Project Context**: `headless-pm://context/project`

Claude Code can automatically reference these resources for context.

## Team Configuration

### Project-Level MCP Configuration

Create `.mcp.json` in your repository root:

```json
{
  "mcpServers": {
    "headless-pm": {
      "command": "python",
      "args": ["-m", "headless_pm_mcp_server"],
      "env": {
        "HEADLESS_PM_URL": "http://localhost:6969"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

This allows the entire team to use both Headless PM coordination and GitHub integration automatically.

### Agent Instructions

Create agent-specific instruction files in `.claude/commands/`:

**`.claude/commands/start-work.md`**:
```markdown
# Start Work Command

1. Register with Headless PM as {{role}} agent
2. Get project context
3. Check for next available task
4. If task available, lock it and update status to "under_work"
5. Create a document announcing task start
```

**`.claude/commands/complete-task.md`**:
```markdown
# Complete Task Command

For task {{task_id}}:
1. Update status to "dev_done" 
2. Create documentation of changes
3. If major complexity, create PR
4. Notify relevant team members via @mentions
```

## Environment Variables

Set these environment variables for both options:

```bash
# .env file
HEADLESS_PM_URL=http://localhost:6969
HEADLESS_PM_TIMEOUT=30

# For MCP with authentication (if needed)
API_KEY=your_api_key_here

# Agent defaults
DEFAULT_AGENT_ROLE=backend_dev
DEFAULT_SKILL_LEVEL=senior
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Headless PM server is running on port 6969
2. **MCP Server Not Found**: Check Python path and file permissions
3. **Authentication Errors**: Verify API keys and agent registration

### Debug Mode

For the lightweight client:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all HTTP requests will be logged
```

For MCP server:
```bash
# Run with debug flag in Claude Code
claude --mcp-debug

# Or check MCP logs
tail -f ~/.claude/logs/mcp-server-headless-pm.log
```

### Testing Integration

**Test lightweight client:**
```python
from headless_pm_client import claude_workflow_example
claude_workflow_example()
```

**Test MCP server:**
```bash
# Run MCP server standalone
python headless_pm_mcp_server.py

# Test with MCP inspector (if available)
mcp-inspector headless-pm
```

## Migration Path

1. **Start with lightweight client** for immediate functionality
2. **Develop team workflows** and identify common patterns
3. **Implement MCP server** for standardization
4. **Migrate gradually** by updating `.mcp.json` configuration
5. **Remove lightweight client** once MCP is stable

## Performance Considerations

- **Lightweight Client**: ~50ms per API call, minimal memory usage
- **MCP Server**: ~100ms per tool call, includes protocol overhead
- **Polling Frequency**: Recommend 10-30 second intervals for change polling
- **Token Usage**: MCP uses more tokens for protocol messages

## Security Notes

- Both implementations support HTTPS endpoints
- MCP provides better isolation between tools
- Consider API key authentication for production deployments
- Audit agent permissions and restrict sensitive operations

## Next Steps

1. Choose your preferred integration approach
2. Set up the configuration files
3. Test with a simple workflow
4. Expand to multi-agent coordination
5. Add team-specific customizations

The MCP approach is recommended for long-term use, but the lightweight client provides immediate value and easier debugging during development.
