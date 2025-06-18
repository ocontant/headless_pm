# How to Use Headless PM MCP in Claude Code

## Available MCP Tools

Once the MCP server is installed, you can use these natural language commands in Claude Code:

### 1. Register as an Agent
```
Please register me as a backend developer named alice_001
```

### 2. Get Project Context
```
Get the project context
```

### 3. Get Next Task
```
Get my next task
```

### 4. Lock a Task
```
Lock task 123
```

### 5. Update Task Status
```
Update task 123 status to under_work
```

## How MCP Works in Claude Code

1. **Natural Language**: Just ask Claude Code to do something, and it will use the MCP tools
2. **No Direct Commands**: You don't run `python headless-pm-mcp-bridge.py` directly
3. **MCP Integration**: Claude Code translates your request into MCP tool calls

## Example Session

```
User: Register me as a pm named pm_principal_001 with principal skill level
Claude: [Uses MCP tool register_agent with the parameters]

User: Get my next task
Claude: [Uses MCP tool get_next_task]

User: Lock that task
Claude: [Uses MCP tool lock_task with the task ID]
```

## Troubleshooting

1. Check MCP server is listed:
   ```
   claude mcp list
   ```

2. If you see "headlesspm" in the list, it's ready to use

3. Just use natural language - Claude Code will handle the MCP protocol

## Important Notes

- The MCP bridge runs in the background when Claude Code starts
- You interact through natural language, not command line
- Claude Code automatically selects the right MCP tool based on your request