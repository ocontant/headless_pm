# Headless PM MCP Client for Claude Code

## Quick Start

1. Copy these two files to your project root:
   - `headless-pm-mcp-bridge.py`
   - `install_client.sh`

2. Run the installer:
   ```bash
   ./install_client.sh
   ```

3. Test the connection:
   ```bash
   claude "Register me as a backend developer"
   ```

## Connecting to Remote Server

```bash
export HEADLESS_PM_URL=http://your-server:6969
./install_client.sh
```

## Files

- **headless-pm-mcp-bridge.py**: The MCP bridge that connects Claude Code to Headless PM
- **install_client.sh**: Installs the bridge as an MCP server in Claude Code

## Requirements

- Python 3.6+ (uses only standard library)
- Claude Code CLI (`claude` command)
- Access to Headless PM server (default: http://localhost:6969)

## Available Commands

Once installed, you can use these commands in Claude Code:
- "Register me as a [role] developer"
- "Get my next task"
- "Lock task [id]"
- "Update task [id] status to [status]"
- "Get project context"

## Troubleshooting

Check connection:
```bash
claude mcp list
```

Enable debug mode:
```bash
export DEBUG=1
claude "Get project context"
```