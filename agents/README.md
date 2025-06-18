# Headless PM Agent Instructions

This directory contains instructions and configurations for different agent integration approaches with Headless PM.

IMPORTANT: Claude Code does not work well in agentic mode using MCP. It should be directed to use headless_pm_client.py instead. 

## Directory Structure

```
agents/
├── claude/     # Claude Code specific configuration
├── mcp/        # Model Context Protocol instructions
├── client/     # Python client instructions
└── env-example # Environment configuration template
```

## Integration Approaches

### 1. MCP (Model Context Protocol) - Recommended for Claude Code
- **Location**: `/agents/mcp/`
- **Best for**: Natural language interaction with Headless PM
- **Setup**: Copy `/agents/claude/.mcp.json` to your project root
- **Usage**: Use conversational commands like "Register me as a backend developer"

### 2. Python Client
- **Location**: `/agents/client/`
- **Best for**: Programmatic integration and automation
- **Setup**: Import from `/examples/client.py`
- **Usage**: Direct API calls through Python methods

### 3. Claude Code Configuration
- **Location**: `/agents/claude/`
- **Contains**: MCP configuration files and Claude-specific instructions
- **Setup**: Follow instructions in `/agents/claude/CLAUDE.md`

## Quick Start

### For MCP Users (Claude Code)
1. Ensure Headless PM is running: `./start.sh`
2. Copy `/agents/claude/.mcp.json` to your project root
3. Read role-specific instructions in `/agents/mcp/[role].md`
4. Use natural language commands to interact

### For Python Client Users
1. Ensure Headless PM is running: `./start.sh`
2. Import the client: `from examples.client import HeadlessPMClient`
3. Read role-specific instructions in `/agents/client/[role].md`
4. Use Python methods to interact

## Available Roles

Each approach has instructions for these roles:
- **backend_dev** - Backend development and APIs
- **frontend_dev** - Frontend development and UI
- **architect** - System architecture and design
- **qa** - Quality assurance and testing
- **pm** - Project management

## Environment Setup

1. Copy `env-example` to `.env` in project root
2. Configure your database and API settings
3. Run `./start.sh` to start both API and MCP servers

## Key Differences

### MCP Approach
- Natural language commands
- No code required
- Automatic tool discovery
- Best for interactive development

### Python Client Approach
- Direct API integration
- Full programmatic control
- Better for automation
- Type-safe with enums

## Additional Resources

- Full integration guide: `/INTEGRATION.md`
- API documentation: `http://localhost:6969/api/v1/docs`
- Example workflows: `/docs/SAMPLE_AGENT_WORKFLOW.md`
