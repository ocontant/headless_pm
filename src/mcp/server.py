"""
Headless PM MCP Server - Model Context Protocol server for Headless PM integration
Provides standardized interface for Claude Code and other MCP clients.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    TextContent,
    Tool,
    EmbeddedResource,
)
from .token_tracker import TokenTracker

# Configure logging
logging.basicConfig(level=logging.INFO, format='[MCP] %(message)s')
logger = logging.getLogger("headless-pm-mcp")


class HeadlessPMMCPServer:
    """MCP Server for Headless PM integration."""

    def __init__(self, base_url: str = "http://localhost:6969", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.server = Server("headless-pm")
        
        # Setup HTTP client with API key headers (for write operations)
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        self.client = httpx.AsyncClient(timeout=30.0, headers=headers)
        
        # Setup public HTTP client (for read operations, no auth required)
        self.public_client = httpx.AsyncClient(timeout=30.0)
        
        self.agent_id: Optional[str] = None
        self.agent_role: Optional[str] = None
        self.agent_skill_level: Optional[str] = None
        self.current_project_id: Optional[int] = None  # Track current project
        self.token_tracker = TokenTracker()

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="switch_project",
                        description="Switch to a different project context",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "integer",
                                    "description": "ID of the project to switch to"
                                },
                                "project_name": {
                                    "type": "string",
                                    "description": "Name of the project to switch to (alternative to ID)"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="list_projects",
                        description="List all available projects",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="register_agent",
                        description="Register agent with Headless PM system in the current project",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "agent_id": {
                                    "type": "string",
                                    "description": "Unique identifier for the agent"
                                },
                                "role": {
                                    "type": "string",
                                    "description": "Agent role (frontend_dev, backend_dev, architect, pm, qa)",
                                    "enum": ["frontend_dev", "backend_dev", "architect", "pm", "qa"]
                                },
                                "skill_level": {
                                    "type": "string",
                                    "description": "Agent skill level",
                                    "enum": ["junior", "senior", "principal"],
                                    "default": "senior"
                                },
                                "project_id": {
                                    "type": "integer",
                                    "description": "Project ID to register in (optional, uses current project if not specified)"
                                }
                            },
                            "required": ["agent_id", "role"]
                        }
                    ),
                    Tool(
                        name="get_project_context",
                        description="Get project configuration and context information",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_next_task",
                        description="Get next available task for the registered agent",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "description": "Override agent role for task search"
                                },
                                "skill_level": {
                                    "type": "string",
                                    "description": "Override skill level for task search"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="create_task",
                        description="Create a new task",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed task description"
                                },
                                "complexity": {
                                    "type": "string",
                                    "description": "Task complexity level",
                                    "enum": ["minor", "major"]
                                },
                                "role": {
                                    "type": "string",
                                    "description": "Required role for the task"
                                },
                                "skill_level": {
                                    "type": "string",
                                    "description": "Required skill level for the task",
                                    "enum": ["junior", "senior", "principal"]
                                }
                            },
                            "required": ["title", "description", "complexity"]
                        }
                    ),
                    Tool(
                        name="lock_task",
                        description="Lock a task to prevent other agents from picking it up",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to lock"
                                }
                            },
                            "required": ["task_id"]
                        }
                    ),
                    Tool(
                        name="update_task_status",
                        description="Update task status and progress",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to update"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "New task status",
                                    "enum": ["created", "assigned", "under_work", "dev_done", "testing", "completed",
                                             "blocked"]
                                },
                                "notes": {
                                    "type": "string",
                                    "description": "Optional notes about the update"
                                }
                            },
                            "required": ["task_id", "status"]
                        }
                    ),
                    Tool(
                        name="create_document",
                        description="Create a document with optional @mentions for team communication",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Document title"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Document content (supports @mentions)"
                                },
                                "doc_type": {
                                    "type": "string",
                                    "description": "Document type",
                                    "default": "note"
                                },
                                "mentions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of agent IDs to mention"
                                }
                            },
                            "required": ["title", "content"]
                        }
                    ),
                    Tool(
                        name="get_mentions",
                        description="Get notifications and mentions for the registered agent",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="register_service",
                        description="Register a microservice with the system",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "service_name": {
                                    "type": "string",
                                    "description": "Name of the service"
                                },
                                "service_url": {
                                    "type": "string",
                                    "description": "Service URL"
                                },
                                "health_check_url": {
                                    "type": "string",
                                    "description": "Health check endpoint URL"
                                }
                            },
                            "required": ["service_name", "service_url"]
                        }
                    ),
                    Tool(
                        name="send_heartbeat",
                        description="Send heartbeat for a registered service",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "service_name": {
                                    "type": "string",
                                    "description": "Name of the service"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Service status",
                                    "default": "healthy"
                                }
                            },
                            "required": ["service_name"]
                        }
                    ),
                    Tool(
                        name="poll_changes",
                        description="Poll for system changes since a given timestamp",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "since_timestamp": {
                                    "type": "string",
                                    "description": "ISO timestamp to poll changes since"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_token_usage",
                        description="Get MCP token usage statistics",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )

        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """List available resources."""
            return ListResourcesResult(
                resources=[
                    Resource(
                        uri="headless-pm://tasks/list",
                        name="Current Tasks",
                        description="List of all current tasks in the system",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://agents/list",
                        name="Active Agents",
                        description="List of all registered agents",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://documents/recent",
                        name="Recent Documents",
                        description="Recently created documents and communications",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://services/status",
                        name="Service Status",
                        description="Status of all registered microservices",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://changelog/recent",
                        name="Recent Activity",
                        description="Recent system activity and changes",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://context/project",
                        name="Project Context",
                        description="Current project configuration and context",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="headless-pm://guidelines/code",
                        name="Code Guidelines",
                        description="Project code guidelines and standards",
                        mimeType="text/markdown"
                    )
                ]
            )

        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> ReadResourceResult:
            """Read resource content."""
            uri = request.uri

            try:
                if uri == "headless-pm://tasks/list":
                    response = await self.public_client.get(f"{self.base_url}/api/v1/public/tasks")
                    data = response.json()
                    content = json.dumps(data, indent=2)

                elif uri == "headless-pm://agents/list":
                    response = await self.public_client.get(f"{self.base_url}/api/v1/public/agents")
                    data = response.json()
                    content = json.dumps(data, indent=2)

                elif uri == "headless-pm://documents/recent":
                    response = await self.client.get(f"{self.base_url}/api/v1/documents?limit=20")
                    data = response.json()
                    content = json.dumps(data, indent=2)

                elif uri == "headless-pm://services/status":
                    response = await self.client.get(f"{self.base_url}/api/v1/services")
                    data = response.json()
                    content = json.dumps(data, indent=2)

                elif uri == "headless-pm://changelog/recent":
                    response = await self.client.get(f"{self.base_url}/api/v1/changelog?limit=50")
                    data = response.json()
                    content = json.dumps(data, indent=2)

                elif uri == "headless-pm://context/project":
                    project_id = self.current_project_id or 1  # Default to project 1
                    response = await self.public_client.get(f"{self.base_url}/api/v1/public/context/{project_id}")
                    data = response.json()
                    content = json.dumps(data, indent=2)
                elif uri == "headless-pm://guidelines/code":
                    project_id = self.current_project_id or 1  # Default to project 1
                    # Get project context to find code guidelines path
                    response = await self.public_client.get(f"{self.base_url}/api/v1/public/context/{project_id}")
                    context = response.json()
                    guidelines_path = context.get("code_guidelines_path")
                    
                    if not guidelines_path:
                        content = "# Code Guidelines\n\nNo code guidelines have been configured for this project yet.\n\nTo add code guidelines:\n1. Create a markdown file with your coding standards\n2. Update the project configuration to set the code_guidelines_path"
                    else:
                        try:
                            # Try to read the guidelines file
                            import os
                            if os.path.exists(guidelines_path):
                                with open(guidelines_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                            else:
                                content = f"# Code Guidelines\n\nCode guidelines file not found at: {guidelines_path}\n\nPlease ensure the file exists and the path is correct."
                        except Exception as e:
                            content = f"# Code Guidelines\n\nError reading guidelines file: {str(e)}\n\nPath: {guidelines_path}"

                else:
                    raise ValueError(f"Unknown resource URI: {uri}")

                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=content
                        )
                    ]
                )

            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Error reading resource: {str(e)}"
                        )
                    ]
                )

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls."""
            try:
                # Track request tokens
                self.token_tracker.track_request({"tool": request.name, "args": request.arguments})
                if request.name == "switch_project":
                    return await self._switch_project(request.arguments)
                elif request.name == "list_projects":
                    return await self._list_projects(request.arguments)
                elif request.name == "register_agent":
                    return await self._register_agent(request.arguments)
                elif request.name == "get_project_context":
                    return await self._get_project_context(request.arguments)
                elif request.name == "get_next_task":
                    return await self._get_next_task(request.arguments)
                elif request.name == "create_task":
                    return await self._create_task(request.arguments)
                elif request.name == "lock_task":
                    return await self._lock_task(request.arguments)
                elif request.name == "update_task_status":
                    return await self._update_task_status(request.arguments)
                elif request.name == "create_document":
                    return await self._create_document(request.arguments)
                elif request.name == "get_mentions":
                    return await self._get_mentions(request.arguments)
                elif request.name == "register_service":
                    return await self._register_service(request.arguments)
                elif request.name == "send_heartbeat":
                    return await self._send_heartbeat(request.arguments)
                elif request.name == "poll_changes":
                    return await self._poll_changes(request.arguments)
                elif request.name == "get_token_usage":
                    return await self._get_token_usage(request.arguments)
                else:
                    raise ValueError(f"Unknown tool: {request.name}")

            except Exception as e:
                logger.error(f"Error calling tool {request.name}: {e}")
                result = CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: {str(e)}"
                        )
                    ]
                )
                # Track response tokens
                self.token_tracker.track_response({"error": str(e)})
                return result

    async def _switch_project(self, args: Dict[str, Any]) -> CallToolResult:
        """Switch to a different project."""
        project_id = args.get("project_id")
        project_name = args.get("project_name")
        
        if not project_id and not project_name:
            raise ValueError("Either project_id or project_name must be provided")
        
        # If project_name provided, we need to look up the ID
        if project_name and not project_id:
            response = await self.public_client.get(f"{self.base_url}/api/v1/public/projects")
            projects = response.json()
            for project in projects:
                if project["name"].lower() == project_name.lower():
                    project_id = project["id"]
                    break
            if not project_id:
                raise ValueError(f"Project '{project_name}' not found")
        
        self.current_project_id = project_id
        
        # Get project details
        response = await self.client.get(f"{self.base_url}/api/v1/context/{project_id}")
        project_info = response.json()
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Switched to project: {project_info['project_name']} (ID: {project_id})"
                )
            ]
        )
    
    async def _list_projects(self, args: Dict[str, Any]) -> CallToolResult:
        """List all available projects."""
        response = await self.public_client.get(f"{self.base_url}/api/v1/public/projects")
        projects = response.json()
        
        project_list = "Available projects:\n"
        for project in projects:
            current = " (current)" if project["id"] == self.current_project_id else ""
            project_list += f"- {project['name']} (ID: {project['id']}){current}\n"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=project_list
                )
            ]
        )

    async def _register_agent(self, args: Dict[str, Any]) -> CallToolResult:
        """Register agent with the system."""
        project_id = args.get("project_id", self.current_project_id)
        if not project_id:
            raise ValueError("No project selected. Use 'switch_project' first or provide project_id")
        
        self.agent_id = args["agent_id"]
        self.agent_role = args["role"]
        self.agent_skill_level = args.get("skill_level", "senior")

        data = {
            "agent_id": self.agent_id,
            "role": self.agent_role,
            "level": self.agent_skill_level,  # Changed from skill_level to level
            "connection_type": "mcp",  # Set connection type to MCP
            "project_id": project_id
        }

        response = await self.client.post(f"{self.base_url}/api/v1/register", json=data)
        result = response.json()

        call_result = CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Agent {self.agent_id} registered as {self.agent_role} ({self.agent_skill_level}) in project ID {project_id}"
                )
            ]
        )
        
        # Track response tokens
        self.token_tracker.track_response(result)
        return call_result

    async def _get_project_context(self, args: Dict[str, Any]) -> CallToolResult:
        """Get project context."""
        project_id = self.current_project_id or 1  # Default to project 1
        
        response = await self.public_client.get(f"{self.base_url}/api/v1/public/context/{project_id}")
        result = response.json()

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )

    async def _get_next_task(self, args: Dict[str, Any]) -> CallToolResult:
        """Get next available task."""
        params = {
            "role": args.get("role", self.agent_role),
            "skill_level": args.get("skill_level", self.agent_skill_level),
            "agent_id": self.agent_id
        }

        response = await self.public_client.get(f"{self.base_url}/api/v1/public/tasks/next", params=params)
        result = response.json()

        if not result:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="No tasks available"
                    )
                ]
            )

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Task {result.get('id')}: {result.get('title')}\nComplexity: {result.get('complexity')}\n{result.get('description')}"
                )
            ]
        )

    async def _create_task(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a new task."""
        data = {
            "title": args["title"],
            "description": args["description"],
            "complexity": args["complexity"],
            "role": args.get("role", self.agent_role),
            "skill_level": args.get("skill_level", self.agent_skill_level)
        }

        response = await self.client.post(f"{self.base_url}/api/v1/tasks/create", json=data)
        result = response.json()

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Task {result.get('id')} created: {result.get('title')}"
                )
            ]
        )

    async def _lock_task(self, args: Dict[str, Any]) -> CallToolResult:
        """Lock a task."""
        task_id = args["task_id"]
        data = {"agent_id": self.agent_id}

        response = await self.client.post(f"{self.base_url}/api/v1/tasks/{task_id}/lock", json=data)

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Task {task_id} locked"
                )
            ]
        )

    async def _update_task_status(self, args: Dict[str, Any]) -> CallToolResult:
        """Update task status."""
        task_id = args["task_id"]
        data = {
            "status": args["status"],
            "agent_id": self.agent_id
        }

        if "notes" in args:
            data["notes"] = args["notes"]

        response = await self.client.put(f"{self.base_url}/api/v1/tasks/{task_id}/status", json=data)

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Task {task_id} status: {args['status']}"
                )
            ]
        )

    async def _create_document(self, args: Dict[str, Any]) -> CallToolResult:
        """Create a document."""
        data = {
            "title": args["title"],
            "content": args["content"],
            "type": args.get("doc_type", "note"),
            "author": self.agent_id
        }

        if "mentions" in args:
            data["mentions"] = args["mentions"]

        response = await self.client.post(f"{self.base_url}/api/v1/documents", json=data)
        result = response.json()

        mentions_text = ""
        if "mentions" in args and args["mentions"]:
            mentions_text = f"\n**Mentions:** {', '.join(args['mentions'])}"

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Document {result.get('id')} created: {result.get('title')}"
                )
            ]
        )

    async def _get_mentions(self, args: Dict[str, Any]) -> CallToolResult:
        """Get mentions for the agent."""
        params = {"agent_id": self.agent_id}
        response = await self.client.get(f"{self.base_url}/api/v1/mentions", params=params)
        result = response.json()

        if not result:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="No mentions"
                    )
                ]
            )

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"{len(result)} mentions: {json.dumps(result, indent=2)}"
                )
            ]
        )

    async def _register_service(self, args: Dict[str, Any]) -> CallToolResult:
        """Register a service."""
        data = {
            "name": args["service_name"],
            "url": args["service_url"],
            "registered_by": self.agent_id
        }

        if "health_check_url" in args:
            data["health_check_url"] = args["health_check_url"]

        response = await self.client.post(f"{self.base_url}/api/v1/services/register", json=data)

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Service '{args['service_name']}' registered"
                )
            ]
        )

    async def _send_heartbeat(self, args: Dict[str, Any]) -> CallToolResult:
        """Send service heartbeat."""
        service_name = args["service_name"]
        data = {"status": args.get("status", "healthy")}

        response = await self.client.post(f"{self.base_url}/api/v1/services/{service_name}/heartbeat", json=data)

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Heartbeat sent: {service_name}"
                )
            ]
        )

    async def _poll_changes(self, args: Dict[str, Any]) -> CallToolResult:
        """Poll for changes."""
        params = {}
        if "since_timestamp" in args:
            params["since"] = args["since_timestamp"]

        response = await self.client.get(f"{self.base_url}/api/v1/changes", params=params)
        result = response.json()

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )

    async def _get_token_usage(self, args: Dict[str, Any]) -> CallToolResult:
        """Get token usage statistics."""
        usage_summary = self.token_tracker.get_usage_summary()
        
        result = CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(usage_summary, indent=2)
                )
            ]
        )
        
        # Track response tokens
        self.token_tracker.track_response(usage_summary)
        return result

    async def run(self):
        """Run the MCP server."""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="headless-pm",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(
                                prompts_changed=True,
                                resources_changed=True,
                                tools_changed=True
                            ),
                            experimental_capabilities={}
                        )
                    )
                )
        finally:
            # Save token usage on shutdown
            if self.agent_id:
                self.token_tracker.end_session(self.agent_id)
            await self.client.aclose()


async def main():
    """Main entry point."""
    import sys
    import os

    # Get configuration from environment
    base_url = os.getenv('API_URL', os.getenv('HEADLESS_PM_URL', 'http://localhost:6969'))
    api_key = os.getenv('API_KEY')
    
    # Command line args can override
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        api_key = sys.argv[2]

    logger.info(f"Starting MCP server, connecting to API at {base_url}")
    if api_key:
        logger.info("Using API key authentication")
    
    server = HeadlessPMMCPServer(base_url, api_key)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
