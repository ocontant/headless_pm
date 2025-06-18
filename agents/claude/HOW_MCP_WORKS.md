# How MCP Works in Claude Code

## Architecture

```
Claude Code (You type here)
     |
     v
MCP Protocol
     |
     v
headless-pm-mcp-bridge.py (Running automatically)
     |
     v
HTTP Requests
     |
     v
Headless PM API (http://localhost:6969)
```

## What Happens When You Install

1. `install_client.sh` registers the bridge script with Claude Code
2. Claude Code starts the bridge automatically when needed
3. The bridge runs in the background and translates between MCP and HTTP

## What Happens When You Use It

1. You say: "I need to register as a developer"
2. Claude Code recognizes this needs the `register_agent` MCP tool
3. Claude Code sends an MCP message to the bridge
4. The bridge converts it to an HTTP API call
5. The response comes back through the same path

## Key Points

- **One-time installation**: Run install_client.sh ONCE
- **No manual execution**: Never run the bridge script yourself
- **Natural language**: Just describe what you want to do
- **Automatic**: Claude Code handles all the MCP protocol stuff

## Common Mistakes

❌ DON'T: Try to run `python headless-pm-mcp-bridge.py`
✅ DO: Just say what you want in natural language

❌ DON'T: Try to install every time you use Claude Code  
✅ DO: Install once, then just use natural language

❌ DON'T: Use command-like syntax from the docs
✅ DO: Use conversational language

## Example Session

```
You: I need to register as a backend developer named john_001
Claude: [Uses MCP register_agent tool automatically]

You: Show me available tasks
Claude: [Uses MCP get_next_task tool automatically]

You: Lock task 123 for me
Claude: [Uses MCP lock_task tool automatically]
```