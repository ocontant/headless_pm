# IMPORTANT: How to Use Headless PM in Claude Code

## DO NOT RUN ANY SCRIPTS!

The `headless-pm-mcp-bridge.py` is already running in the background as an MCP server.

## How to Use MCP Tools

You have MCP tools available. To use them, just describe what you want in natural language.

### Examples:

**To Register:**
Instead of trying to run scripts, just say:
"I'll register as a Project PM agent now"

Then Claude Code will automatically:
1. Find the `register_agent` tool from the headlesspm MCP server
2. Call it with the right parameters
3. Get the response

**To Get Tasks:**
Just say: "Let me check for available tasks"

**To Create Documents:**
Just say: "I'll create a status update document"

## Available MCP Tools from headlesspm server:
- register_agent - Registers you with the system
- get_context - Gets project information  
- get_next_task - Gets available tasks
- lock_task - Locks a task for work
- update_task_status - Updates task status
- create_document - Creates documents
- get_mentions - Checks for mentions

## REMEMBER:
- The MCP bridge is ALREADY RUNNING
- You DON'T need to execute any Python scripts
- Just use natural language and Claude Code handles the MCP protocol
- If you see "headlesspm" in your MCP servers list, it's ready to use