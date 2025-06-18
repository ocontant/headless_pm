#!/usr/bin/env python3
"""
Headless PM MCP Bridge - Standalone client for Claude Code
Connects to a Headless PM server and provides MCP interface
"""

import asyncio
import json
import sys
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

# Configuration from environment
SERVER_URL = os.getenv('HEADLESS_PM_URL', 'http://localhost:6969')
API_KEY = os.getenv('HEADLESS_PM_API_KEY', '')
DEBUG = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')

def debug(msg):
    """Print debug message to stderr."""
    if DEBUG:
        print(f"[DEBUG] {msg}", file=sys.stderr)

def api_request(method, endpoint, data=None):
    """Make API request to Headless PM server."""
    url = f"{SERVER_URL}/api/v1{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    # Add API key if provided
    if API_KEY:
        headers['X-API-Key'] = API_KEY
    
    req = Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except URLError as e:
        return {"error": str(e)}

async def handle_request(request):
    """Handle JSON-RPC request from Claude Code."""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")
    
    debug(f"Received: {method}")
    
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "headless-pm",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": "register_agent",
                        "description": "Register as an agent with Headless PM",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {
                                    "type": "string",
                                    "description": "Unique agent identifier"
                                },
                                "role": {
                                    "type": "string",
                                    "description": "Agent role",
                                    "enum": ["frontend_dev", "backend_dev", "architect", "pm", "qa"]
                                },
                                "skill_level": {
                                    "type": "string",
                                    "description": "Skill level",
                                    "enum": ["junior", "senior", "principal"],
                                    "default": "senior"
                                }
                            },
                            "required": ["agent_id", "role"]
                        }
                    },
                    {
                        "name": "get_context",
                        "description": "Get project context and configuration"
                    },
                    {
                        "name": "get_next_task",
                        "description": "Get the next available task"
                    },
                    {
                        "name": "lock_task",
                        "description": "Lock a task for exclusive work",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "Task ID to lock"
                                }
                            },
                            "required": ["task_id"]
                        }
                    },
                    {
                        "name": "update_task_status",
                        "description": "Update task status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "Task ID"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "New status",
                                    "enum": ["created", "assigned", "under_work", "dev_done", "testing", "completed", "blocked"]
                                }
                            },
                            "required": ["task_id", "status"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool = params.get("name")
            args = params.get("arguments", {})
            
            if tool == "register_agent":
                response = api_request("POST", "/register", {
                    "agent_id": args["agent_id"],
                    "role": args["role"],
                    "level": args.get("skill_level", "senior"),
                    "connection_type": "mcp"
                })
                text = f"Registered as {args['role']} agent: {args['agent_id']}"
            
            elif tool == "get_context":
                response = api_request("GET", "/context")
                text = json.dumps(response, indent=2)
            
            elif tool == "get_next_task":
                response = api_request("GET", "/tasks/next")
                if response and "id" in response:
                    text = f"Task {response['id']}: {response.get('title', 'Untitled')}\n{response.get('description', '')}"
                else:
                    text = "No tasks available"
            
            elif tool == "lock_task":
                task_id = args["task_id"]
                response = api_request("POST", f"/tasks/{task_id}/lock", {
                    "agent_id": "mcp-agent"  # TODO: Track agent ID from registration
                })
                text = f"Task {task_id} locked"
            
            elif tool == "update_task_status":
                task_id = args["task_id"]
                status = args["status"]
                response = api_request("PUT", f"/tasks/{task_id}/status", {
                    "status": status,
                    "agent_id": "mcp-agent"  # TODO: Track agent ID
                })
                text = f"Task {task_id} status updated to: {status}"
            
            else:
                text = f"Unknown tool: {tool}"
            
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        
        elif method == "resources/list":
            result = {
                "resources": [
                    {
                        "uri": "headless-pm://tasks",
                        "name": "Tasks",
                        "description": "Current tasks in the system"
                    },
                    {
                        "uri": "headless-pm://agents",
                        "name": "Agents",
                        "description": "Registered agents"
                    }
                ]
            }
        
        elif method == "resources/read":
            uri = params.get("uri", "")
            
            if uri == "headless-pm://tasks":
                response = api_request("GET", "/tasks")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://agents":
                response = api_request("GET", "/agents")
                content = json.dumps(response, indent=2)
            else:
                content = f"Unknown resource: {uri}"
            
            result = {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": content
                    }
                ]
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": request_id
        }

async def main():
    """Main stdio loop for MCP protocol."""
    debug(f"Starting MCP bridge, connecting to {SERVER_URL}")
    
    # Set up async stdio
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    while True:
        try:
            # Read line from stdin
            line = await reader.readline()
            if not line:
                break
            
            # Parse JSON-RPC request
            request = json.loads(line.decode().strip())
            debug(f"Request: {request}")
            
            # Handle request
            response = await handle_request(request)
            debug(f"Response: {response}")
            
            # Write response to stdout
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            # Send parse error
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                },
                "id": None
            }
            print(json.dumps(error_response), flush=True)
        
        except Exception as e:
            debug(f"Error: {e}")
            # Continue on other errors

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass