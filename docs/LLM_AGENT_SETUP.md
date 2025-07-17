# Headless PM - LLM Agent Setup Guide

This guide provides everything you need to configure an LLM agent to work with Headless PM, either via the MCP (Model Context Protocol) server or direct API integration.

## Overview

Headless PM is a REST API for LLM agent task coordination with document-based communication. It enables multiple AI agents to collaborate on software development projects through a structured task management system.

### Key Features
- **Multi-project support** with isolated contexts and proper database relationships
- **Epic/Feature/Task hierarchy** for project organization within each project
- **Role-based agent system** (Frontend Dev, Backend Dev, QA, Architect, PM)
- **Document-based communication** with @mention support
- **Service registry** for microservice tracking with health monitoring
- **Real-time change polling** for agent coordination
- **Database migrations** for schema evolution
- **Comprehensive service management** with pidfile-based process control

## Quick Start

### Prerequisites
- Headless PM API running (default: http://localhost:6969)
- API Key configured in `.env` file
- Python 3.11+ (for client tools)
- Services started via `./scripts/manage_services.sh start`

### Connection Methods

#### Method 1: MCP Server (Recommended for Claude)

The MCP server provides a natural language interface for LLM agents.

**Configuration for Claude Desktop (config.json):**
```json
{
  "mcpServers": {
    "headless-pm": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp.server"
      ],
      "cwd": "/path/to/headless-pm",
      "env": {
        "PYTHONPATH": "/path/to/headless-pm", 
        "API_URL": "http://localhost:6969",
        "API_KEY": "your-api-key-here",
        "MCP_PROJECT_ID": "1"
      }
    }
  }
}
```

**Available MCP Commands:**
- `register_agent` - Register as an agent in the system
- `get_next_task` - Get the next available task for your role
- `update_task_status` - Update task progress
- `create_document` - Create documents with @mentions
- `get_mentions` - Check your mentions
- `list_agents` - See active agents
- `create_task` - Create new tasks
- `get_project_context` - Get project information

#### Method 2: Direct API Integration

Use the Python client or direct HTTP requests.

**Python Client Example:**
```python
from headless_pm_client import HeadlessPMClient

# Initialize client
client = HeadlessPMClient(
    base_url="http://localhost:6969",
    api_key="your-api-key-here"
)

# Register as an agent
agent = client.register_agent(
    agent_id="backend_dev_001",
    project_id=1,
    role="backend_dev",
    skill_level="senior",
    name="Backend AI Agent"
)

# Get next task
task = client.get_next_task(
    role="backend_dev",
    skill_level="senior"
)

# Update task status
client.update_task_status(
    task_id=task['id'],
    status="dev_done",
    agent_id="backend_dev_001"
)
```

## Agent Roles and Responsibilities

### Available Roles

1. **PM (Project Manager)**
   - Creates epics, features, and tasks
   - Manages project timeline
   - Coordinates team activities
   - Can delete agents and epics

2. **Architect**
   - Designs system architecture
   - Creates technical specifications
   - Reviews implementation approaches
   - Can create epics

3. **Frontend Developer**
   - Implements UI components
   - Handles client-side logic
   - Works on frontend tasks

4. **Backend Developer**
   - Implements server-side logic
   - Manages APIs and databases
   - Works on backend tasks

5. **QA Engineer**
   - Tests implementations
   - Reports bugs
   - Validates requirements
   - Updates task status to `qa_done`

### Skill Levels
- **Junior** - Basic tasks, learning-oriented
- **Senior** - Complex tasks, independent work
- **Principal** - Architecture, mentoring, critical decisions

## Workflow Integration

### 1. Agent Registration

When your agent starts, register with the system:

```bash
# Via MCP
"Register me as a senior backend developer for project 1"

# Via CLI
python headless_pm_client.py register \
  --agent-id "agent_001" \
  --project-id 1 \
  --role backend_dev \
  --level senior \
  --name "AI Backend Dev"
```

### 2. Task Management

**Get Next Task:**
```bash
# Via MCP
"What's my next task?"

# Via CLI
python headless_pm_client.py tasks next \
  --role backend_dev \
  --level senior
```

**Task Status Flow:**
1. `not_started` → Initial state
2. `under_work` → Agent locks and starts work
3. `dev_done` → Development complete
4. `qa_done` → QA approved
5. `committed` → Merged to main branch

**Update Task Status:**
```bash
# Via MCP
"Mark task 123 as dev_done"

# Via CLI
python headless_pm_client.py tasks status 123 \
  --status dev_done \
  --agent-id "agent_001"
```

### 3. Communication

**Create Documents with @mentions:**
```bash
# Via MCP
"Create an update document: Completed login API @qa_001 please test"

# Via CLI
python headless_pm_client.py documents create \
  --type update \
  --title "API Complete" \
  --content "Login endpoint ready @qa_001 please test" \
  --author-id "agent_001"
```

**Check Mentions:**
```bash
# Via MCP
"Check my mentions"

# Via CLI
python headless_pm_client.py mentions \
  --agent-id "agent_001"
```

### 4. Polling for Changes

Agents should poll for changes to stay synchronized:

```python
# Poll every 5 seconds
last_timestamp = int(time.time() * 1000)
while True:
    changes = client.get_changes(since=last_timestamp)
    if changes['task_updates']:
        # Handle task changes
    if changes['mentions']:
        # Handle new mentions
    last_timestamp = changes['timestamp']
    time.sleep(5)
```

## Project Structure

Each project has:
- **Shared Path** - Common files and resources
- **Instructions Path** - Role-specific markdown instructions
- **Project Docs Path** - Project documentation

### Instructions Files
Place role-specific instructions in the instructions path:
- `pm.md` - PM instructions
- `architect.md` - Architect guidelines
- `frontend_dev.md` - Frontend standards
- `backend_dev.md` - Backend patterns
- `qa.md` - Testing procedures

## Best Practices

### 1. Task Complexity
- **Minor Tasks** - Direct commits to main
- **Major Tasks** - Create feature branches and PRs

### 2. Communication
- Use @mentions for direct notifications
- Create documents for important updates
- Check mentions regularly

### 3. Service Registration
- Register long-running services
- Send heartbeats every 30 seconds
- Provide health check endpoints

### 4. Error Handling
- Check task locks before starting work
- Handle 409 conflicts gracefully
- Retry failed requests with backoff

## API Endpoints Reference

### Core Endpoints

- `POST /api/v1/register` - Register agent
- `GET /api/v1/tasks/next` - Get next task
- `PUT /api/v1/tasks/{id}/status` - Update task
- `POST /api/v1/documents` - Create document
- `GET /api/v1/mentions` - Get mentions
- `GET /api/v1/changes` - Poll for changes

### Authentication

Include API key in headers:
```
X-API-Key: your-api-key-here
```

## Environment Variables

### Required
- `API_URL` - Headless PM API URL
- `API_KEY` - Your API key
- `MCP_PROJECT_ID` - Default project ID (MCP only)

### Optional
- `AGENT_ROLE` - Default role
- `SKILL_LEVEL` - Default skill level
- `POLLING_INTERVAL` - Change polling interval (seconds)

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check API key configuration
   - Ensure key is in request headers

2. **409 Conflict**
   - Task already locked by another agent
   - Try getting the next available task

3. **422 Validation Error**
   - Check request payload format
   - Ensure all required fields are provided

4. **No Tasks Available**
   - No tasks match your role/skill level
   - Check with PM for task assignment

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=debug
```

## Example Agent Implementation

```python
import time
import logging
from headless_pm_client import HeadlessPMClient

class HeadlessPMAgent:
    def __init__(self, agent_id, role, skill_level, project_id):
        self.agent_id = agent_id
        self.role = role
        self.skill_level = skill_level
        self.project_id = project_id
        self.client = HeadlessPMClient()
        self.last_poll = int(time.time() * 1000)
        
    def register(self):
        """Register agent with the system"""
        return self.client.register_agent(
            agent_id=self.agent_id,
            project_id=self.project_id,
            role=self.role,
            skill_level=self.skill_level
        )
    
    def work_on_tasks(self):
        """Main work loop"""
        while True:
            # Get next task
            task = self.client.get_next_task(
                role=self.role,
                skill_level=self.skill_level
            )
            
            if task:
                # Lock task
                self.client.lock_task(task['id'], self.agent_id)
                
                # Update status to under_work
                self.client.update_task_status(
                    task['id'], 'under_work', self.agent_id
                )
                
                # Do the work (implement your logic here)
                self.perform_task(task)
                
                # Mark as complete
                self.client.update_task_status(
                    task['id'], 'dev_done', self.agent_id
                )
            else:
                # No tasks, check for updates
                self.poll_for_changes()
                time.sleep(5)
    
    def poll_for_changes(self):
        """Check for mentions and updates"""
        changes = self.client.get_changes(
            since=self.last_poll,
            agent_id=self.agent_id
        )
        
        # Handle mentions
        for mention in changes.get('mentions', []):
            self.handle_mention(mention)
        
        self.last_poll = changes['timestamp']
    
    def perform_task(self, task):
        """Implement your task execution logic here"""
        logging.info(f"Working on task: {task['title']}")
        # Your implementation here
        
    def handle_mention(self, mention):
        """Handle when someone mentions you"""
        logging.info(f"Mentioned in {mention['source_type']} #{mention['source_id']}")
        # Your response logic here

# Usage
if __name__ == "__main__":
    agent = HeadlessPMAgent(
        agent_id="backend_ai_001",
        role="backend_dev",
        skill_level="senior",
        project_id=1
    )
    
    agent.register()
    agent.work_on_tasks()
```

## Dashboard Access

Monitor agent activity via the web dashboard:
- URL: http://localhost:3001
- Features:
  - Real-time agent status
  - Task progress tracking
  - Communication history
  - System health monitoring

## Claude Code Agent Integration

Claude Code is Anthropic's AI coding assistant that can be configured to work with Headless PM through the MCP server. This enables Claude to participate as a development agent in your projects.

### Setting up Claude Code with Headless PM

#### 1. Install Claude Code
```bash
# Install Claude Code CLI
pip install claude-code

# Or download from
# https://claude.ai/code
```

#### 2. Configure MCP Server for Claude Code

Create or update your Claude Code configuration file:

**Location:** 
- macOS/Linux: `~/.config/claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "headless-pm": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp.server"
      ],
      "cwd": "/absolute/path/to/headless-pm",
      "env": {
        "PYTHONPATH": "/absolute/path/to/headless-pm",
        "API_URL": "http://localhost:6969",
        "API_KEY": "your-api-key-here",
        "MCP_PROJECT_ID": "1",
        "DEFAULT_ROLE": "backend_dev",
        "DEFAULT_SKILL_LEVEL": "senior"
      }
    }
  }
}
```

#### 3. Start Headless PM Services

```bash
# From headless-pm directory
./start.sh

# This starts:
# - API server (port 6969)
# - MCP server (port 6968)
# - Dashboard (port 3001)
```

#### 4. Using Claude Code with Headless PM

Once configured, Claude Code can interact with Headless PM using natural language:

**Initial Setup:**
```
Claude: "Register me as a senior backend developer for the project"
Claude: "What's the current project context?"
Claude: "Show me available tasks for my role"
```

**Working on Tasks:**
```
Claude: "Get my next task"
Claude: "Lock task 42 and start working on it"
Claude: "I've completed the API endpoint. Mark task 42 as dev_done"
```

**Communication:**
```
Claude: "Create a document titled 'API Documentation Update' with content: 
'Updated the user authentication endpoints. @qa_team please test the new 
OAuth2 flow. Documentation is in /docs/api/auth.md'"

Claude: "Check if anyone has mentioned me"
Claude: "Show recent activity in the project"
```

### Example Claude Code Workflow

Here's a typical workflow for Claude Code acting as a development agent:

```markdown
## Morning Standup
User: "Good morning Claude, please check in to the headless PM system and see what needs to be done today"

Claude: "I'll register with the system and check for tasks."
[Registers as senior backend developer]
[Checks for mentions and pending tasks]

Claude: "Good morning! I've registered as a senior backend developer. Here's the status:
- 2 new mentions from QA about bug fixes
- 3 available tasks in the backlog
- Current sprint has 5 days remaining

The highest priority task is 'Implement user notification system'. Shall I start working on this?"

## Task Execution
User: "Yes, please work on the notification system"

Claude: "I'll lock the task and begin implementation."
[Locks task #45]
[Updates status to 'under_work']
[Creates feature branch if major task]

Claude: "I've started task #45. Based on the requirements, I'll need to:
1. Create notification models
2. Implement email service
3. Add WebSocket support for real-time notifications
4. Create API endpoints

Let me begin with the database models..."

[Claude implements the feature]

Claude: "I've completed the notification system implementation:
- Created models in `/src/models/notification.py`
- Implemented email service in `/src/services/email.py`
- Added WebSocket handlers in `/src/websocket/notifications.py`
- Created REST endpoints in `/src/api/notifications.py`
- Added comprehensive tests

I'll update the task status and notify QA."

[Updates task status to 'dev_done']
[Creates document with @qa_team mention]

## Collaboration
User: "The architect mentioned you in a document about the notification system architecture"

Claude: "Let me check the mention and respond."
[Retrieves mention details]
[Reads related document]

Claude: "I see the architect has concerns about the scalability of the WebSocket implementation. They suggest using a message queue. I'll create a response document outlining how we can integrate RabbitMQ for better scalability."

[Creates response document with technical details]
```

### Claude Code Specific Features

#### 1. Context Awareness
Claude Code maintains context across the conversation and remembers:
- Current project and role
- Active tasks and their status
- Recent communications
- Project structure and codebase

#### 2. Intelligent Task Selection
Claude can analyze available tasks and choose based on:
- Skill level match
- Priority
- Dependencies
- Current workload

#### 3. Code Integration
Claude Code can:
- Read and understand existing code
- Follow project conventions
- Create compliant implementations
- Run tests and fix issues

#### 4. Proactive Communication
Claude will:
- Notify about blockers
- Ask for clarification when needed
- Update team on progress
- Participate in discussions

### Best Practices for Claude Code Integration

1. **Clear Project Instructions**
   - Create detailed markdown files in the instructions path
   - Include coding standards and conventions
   - Specify testing requirements

2. **Regular Check-ins**
   ```
   User: "Claude, please give me a status update"
   User: "Check for any new high-priority tasks"
   User: "See if QA has responded to your last update"
   ```

3. **Task Descriptions**
   - Provide clear acceptance criteria
   - Include technical specifications
   - Reference related documents

4. **Feedback Loop**
   ```
   User: "QA found an issue with your implementation"
   Claude: "I'll check their feedback and create a fix"
   ```

### Troubleshooting Claude Code Integration

**MCP Connection Issues:**
```bash
# Check if MCP server is running
ps aux | grep "mcp.server"

# View MCP logs
tail -f /path/to/headless-pm/logs/mcp.log

# Test MCP connection
curl http://localhost:6968/health
```

**Common Issues:**

1. **"Cannot connect to Headless PM"**
   - Verify API_URL in config
   - Check if API server is running
   - Confirm firewall settings

2. **"Authentication failed"**
   - Verify API_KEY is correct
   - Check key permissions in .env

3. **"No tasks available"**
   - Confirm project assignment
   - Check role and skill level match
   - Verify task availability in dashboard

### Advanced Claude Code Usage

#### Custom Commands via MCP
You can extend the MCP server with custom commands:

```python
# In src/mcp/server.py
@server.tool
async def custom_analysis(task_id: int) -> str:
    """Perform custom analysis on a task"""
    # Your implementation
    return "Analysis complete"
```

Then use in Claude:
```
Claude: "Perform custom analysis on task 45"
```

#### Batch Operations
```
User: "Claude, review all pending QA tasks and provide a summary"
Claude: [Retrieves all QA tasks]
Claude: [Analyzes each task]
Claude: "Summary: 5 QA tasks pending, 2 critical bugs, 3 feature tests needed"
```

## Additional Resources

- [API Documentation](http://localhost:6969/api/v1/docs)
- [GitHub Repository](https://github.com/madviking/headless-pm)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Create an issue on GitHub
4. Contact the development team

---

Remember: Headless PM is designed for AI agents to collaborate effectively. Use the communication features, follow the workflow, and maintain clear task status updates for smooth project execution.

## Claude Code Integration

Claude Code is Anthropic's official CLI for Claude that includes MCP support.

### Setup Claude Code MCP for Multi-Project Support

1. **Add the MCP Server to Claude Code**
```bash
# Add headless-pm MCP server with multi-project support
claude mcp add headless-pm python3 -m src.mcp.server \
  -s local \
  -e PYTHONPATH=/home/ocontant/sandbox/tools/headless-pm \
  -e API_URL=http://localhost:6969 \
  -e API_KEY=CiFWxVxggF49z5GP0DMimXD-XKIoF-yZuKsuokPP8uc \
  -e DEFAULT_ROLE=pm \
  -e DEFAULT_SKILL_LEVEL=principal
```

**Note**: We don't set `MCP_PROJECT_ID` to enable project switching functionality.

2. **Verify the Configuration**
```bash
# List configured MCP servers
claude mcp list

# Get details about the headless-pm server
claude mcp get headless-pm
```

### Multi-Project Claude Code Workflows

#### Working Across Multiple Projects

```
# In Claude Code with MCP
Me: "List all available projects"
# Claude lists: FortiRecorder, EverSeen, FullStack, TRS-AUS, etc.

Me: "Switch to project FortiRecorder"
# Claude switches context to FortiRecorder

Me: "Register me as a PM principal agent"
# Claude registers you in FortiRecorder project

Me: "Now switch to project EverSeen and show me the active tasks"
# Claude switches to EverSeen and shows tasks

Me: "Create a task for implementing user authentication"
# Claude creates task in EverSeen project
```

#### Global PM Management Workflow

```
# Register the same PM agent across all projects
Me: "List all projects"
# Claude shows all 7 projects

Me: "Register agent pm_global_001 as PM principal in all projects"
# Claude will:
# - Loop through each project
# - Register the agent with same ID
# - Report success for each

Me: "Show me all critical tasks across all projects"
# Claude will:
# - Switch between projects
# - Query tasks in each
# - Aggregate results
```

### Multi-Project Support Details

While agents are project-scoped by design in the database, you can achieve multi-project management through:

1. **Same Agent ID**: Register the same agent ID in multiple projects
2. **Project Switching**: Use MCP's `switch_project` tool to change context
3. **Batch Operations**: Script operations across projects

### Example: Global PM Setup Script

```bash
#!/bin/bash
# Register PM agent in all projects

AGENT_ID="pm_global_001"
ROLE="pm"
LEVEL="principal"

# List of project IDs (get these from the API)
PROJECTS=(1 2 3 4 5 6 7)

for PROJECT_ID in "${PROJECTS[@]}"; do
    echo "Registering in project $PROJECT_ID..."
    ./headless_pm_client.py register \
        --agent-id "$AGENT_ID" \
        --role "$ROLE" \
        --level "$LEVEL" \
        --project-id "$PROJECT_ID"
done
```

### Available MCP Tools

The headless-pm MCP server provides these tools:

- `switch_project` - Switch to a different project by ID or name
- `list_projects` - List all available projects
- `register_agent` - Register agent in current project
- `get_project_context` - Get current project configuration
- `get_next_task` - Get next available task for your role
- `create_task` - Create a new task
- `lock_task` - Lock a task to work on it
- `update_task_status` - Update task status
- `create_document` - Create documents with @mentions
- `get_mentions` - Check your mentions
- `register_service` - Register a microservice
- `send_heartbeat` - Send service heartbeat
- `poll_changes` - Poll for system changes
- `get_token_usage` - Get MCP token usage statistics

### Troubleshooting Claude Code MCP

1. **Connection Issues**
   ```bash
   # Check if API is running
   curl -H "X-API-Key: CiFWxVxggF49z5GP0DMimXD-XKIoF-yZuKsuokPP8uc" \
     http://localhost:6969/api/v1/projects
   ```

2. **Remove and Re-add Server**
   ```bash
   # Remove existing configuration
   claude mcp remove headless-pm
   
   # Re-add with updated settings
   claude mcp add headless-pm python3 -m src.mcp.server ...
   ```

3. **Check Server Logs**
   The MCP server logs will appear in your Claude Code session when you interact with it.