# Claude Code MCP Client

This directory contains the MCP client for connecting Claude Code to Headless PM.

## Quick Setup

### Server Side (Headless PM)

Start the Headless PM server:
```bash
./start.sh
```

This starts the API server on http://localhost:6969

### Client Side (Any Project)

1. Copy these files to your project:
   - `headless-pm-mcp-bridge.py`
   - `install_client.sh`

2. Run the installer:
   ```bash
   ./install_client.sh
   ```

3. Test it:
   ```bash
   claude "Register me as a backend developer"
   ```

## Remote Server

To connect to a Headless PM server on another machine:
```bash
export HEADLESS_PM_URL=http://your-server:6969
./install_client.sh
```

## Features

The MCP integration provides these tools:

- **register_agent**: Register as an agent with a specific role
- **get_project_context**: Get project configuration
- **get_next_task**: Get the next available task
- **create_task**: Create a new task
- **lock_task**: Lock a task for exclusive work
- **update_task_status**: Update task progress
- **create_document**: Create documents with @mentions
- **get_mentions**: Check for mentions/notifications
- **register_service**: Register microservices
- **send_heartbeat**: Send service health status
- **poll_changes**: Poll for system changes

## Usage Examples

In Claude Code, you can use natural language:

```
"Register me as a backend developer named claude_001"
"Get my next task"
"Lock task 123"
"Update task 123 status to under_work"
"Create a document titled 'API Implementation' with content about the new endpoints"
"Check for any mentions"
```

## Remote Connection

To connect to a Headless PM server on a different machine:

1. Ensure port 6968 is accessible from your client machine
2. Update the `.mcp.json` with the correct server address
3. No additional software or bridges needed - Claude Code connects directly via HTTP

## Troubleshooting

### Connection Issues
- Verify the server is running: `curl http://YOUR_SERVER:6968/`
- Check firewall settings for port 6968
- Ensure the baseUrl in `.mcp.json` is correct

### Authentication
Currently no authentication is required. In production, you may want to add API keys or other security measures.

## Environment Variables

On the server side, you can configure:
- `SERVICE_PORT`: API server port (default: 6969)
- `MCP_PORT`: MCP server port (default: 6968)
- `HEADLESS_PM_URL`: Internal API URL for MCP server