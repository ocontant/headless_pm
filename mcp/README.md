# Headless PM MCP Server

Model Context Protocol (MCP) server providing natural language interface to Headless PM for Claude Code integration.

## Overview

The MCP server enables Claude Code to interact with Headless PM using natural language through the Model Context Protocol. It bridges MCP calls to the Headless PM API, providing a conversational interface for project management tasks.

## Architecture

```
mcp/
├── src/
│   ├── server.py                    # Main MCP server implementation
│   ├── http_server.py              # HTTP transport
│   ├── sse_server.py               # Server-Sent Events transport
│   ├── simple_sse_server.py        # Simplified SSE transport
│   ├── stdio_bridge.py             # STDIO transport bridge
│   ├── streamable_http_server.py   # Streamable HTTP transport
│   ├── websocket_server.py         # WebSocket transport
│   ├── token_tracker.py            # Usage tracking
│   └── __main__.py                 # Entry point
├── Dockerfile                      # Container definition
└── README.md                      # This file
```

## Transport Protocols

The MCP server supports multiple transport protocols:

- **HTTP** - Standard HTTP requests/responses
- **Server-Sent Events (SSE)** - Real-time streaming
- **WebSocket** - Bidirectional real-time communication
- **STDIO** - Command-line interface bridge

## Dependencies

The MCP server communicates with:
- Headless PM API server (via HTTP)
- Shared models for type definitions (mounted as volume)

## Environment Variables

- `MCP_PORT` - MCP server port (default: 6968)
- `API_BASE_URL` - Base URL for Headless PM API
- `PYTHONPATH` - Python module path

## Running

### With Docker (Recommended)
```bash
# From project root
docker-compose up mcp
```

### Development Mode
```bash
# From project root, with virtual environment activated
python -m mcp.src.http_server
```

## Features

### Natural Language Interface
- Task creation and management
- Project queries and navigation
- Agent registration and status
- Document creation and search
- Service monitoring

### Usage Tracking
- Token usage statistics
- Session tracking
- Performance metrics
- Resource monitoring

### Multi-Protocol Support
- HTTP endpoints for REST-like access
- WebSocket for real-time communication
- SSE for streaming updates
- STDIO for command-line tools

## API Integration

The MCP server acts as a bridge to the main API:

```
Claude Code ↔ MCP Server ↔ HTTP ↔ Headless PM API
```

All MCP tools are translated to appropriate API calls:
- Agent registration → `POST /api/v1/register`
- Task queries → `GET /api/v1/tasks/next`
- Project context → `GET /api/v1/context`
- Document creation → `POST /api/v1/documents`

## Health Monitoring

Health is monitored via process checking since MCP doesn't have standard health endpoints:
```bash
# Check if MCP server is running
pgrep -f "mcp.src"
```

## Usage with Claude Code

The MCP server provides these tools to Claude Code:

### Project Management
- `get_project_context` - Get current project information
- `list_projects` - Show available projects
- `create_project` - Create new project

### Task Management  
- `get_next_task` - Get next available task for role
- `create_task` - Create new task with complexity
- `update_task_status` - Update task progress
- `lock_task` - Lock task to prevent conflicts

### Communication
- `create_document` - Create document with mentions
- `get_mentions` - Get mentions for agent
- `get_changes` - Poll for recent changes

### Agent Management
- `register_agent` - Register new agent
- `get_agent_context` - Get agent information

## Configuration

Configure via environment variables or mounted config files:
```bash
# Set API endpoint
export API_BASE_URL=http://api:6969

# Set MCP port
export MCP_PORT=6968
```

## Development

For development with the MCP server:

1. Start the API server first
2. Run MCP server with hot reload
3. Connect Claude Code to MCP endpoint

```bash
# Terminal 1: Start API
docker-compose up api

# Terminal 2: Start MCP in dev mode
PYTHONPATH=/app python -m mcp.src.http_server

# Terminal 3: Test MCP connection
curl http://localhost:6968/health
```

## Logging

MCP server logs include:
- Tool invocations
- API call traces
- Token usage
- Error diagnostics

View logs with:
```bash
docker-compose logs mcp
```

## Security

- Input validation for all MCP tools
- API key passthrough to main API
- Rate limiting support
- Secure token tracking

## Troubleshooting

### Connection Issues
- Verify API server is running and healthy
- Check network connectivity between containers
- Validate environment variables

### Tool Errors
- Check API server logs for backend errors
- Verify agent registration status
- Validate project context

### Performance
- Monitor token usage via tracking
- Check API response times
- Review resource utilization