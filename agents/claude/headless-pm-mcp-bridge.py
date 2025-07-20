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
API_KEY = os.getenv('API_KEY', '')
DEBUG = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')

# Global state for multi-project support
current_project_id = None
current_agent_id = None

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
                        "name": "list_projects",
                        "description": "List all available projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "select_project",
                        "description": "Select a project to work with",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "integer",
                                    "description": "Project ID to select"
                                }
                            },
                            "required": ["project_id"]
                        }
                    },
                    {
                        "name": "create_project",
                        "description": "Create a new project with repository configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Project name"},
                                "description": {"type": "string", "description": "Project description"},
                                "repository_url": {"type": "string", "description": "Git repository URL (e.g., https://github.com/user/repo.git)"},
                                "repository_main_branch": {"type": "string", "description": "Main branch name", "default": "main"},
                                "shared_path": {"type": "string", "description": "Shared files path", "default": "/shared"},
                                "instructions_path": {"type": "string", "description": "Instructions path", "default": "/instructions"},
                                "project_docs_path": {"type": "string", "description": "Project docs path", "default": "/docs"},
                                "code_guidelines_path": {"type": "string", "description": "Code guidelines path (optional)"},
                                "repository_clone_path": {"type": "string", "description": "Local repository clone path (optional)"}
                            },
                            "required": ["name", "description", "repository_url"]
                        }
                    },
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
                        "description": "Get project context and configuration",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_next_task",
                        "description": "Get the next available task",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
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
                    },
                    # Epics CRUD
                    {
                        "name": "list_epics",
                        "description": "List all epics in current project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_epic",
                        "description": "Get epic details",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "epic_id": {"type": "integer", "description": "Epic ID"}
                            },
                            "required": ["epic_id"]
                        }
                    },
                    {
                        "name": "create_epic",
                        "description": "Create new epic",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Epic name"},
                                "description": {"type": "string", "description": "Epic description"},
                                "pm_id": {"type": "string", "description": "Project manager ID"}
                            },
                            "required": ["name"]
                        }
                    },
                    {
                        "name": "delete_epic",
                        "description": "Delete epic",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "epic_id": {"type": "integer", "description": "Epic ID"}
                            },
                            "required": ["epic_id"]
                        }
                    },
                    # Features CRUD
                    {
                        "name": "list_features",
                        "description": "List features for an epic",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "epic_id": {"type": "integer", "description": "Epic ID"}
                            },
                            "required": ["epic_id"]
                        }
                    },
                    {
                        "name": "create_feature",
                        "description": "Create new feature",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "epic_id": {"type": "integer", "description": "Epic ID"},
                                "name": {"type": "string", "description": "Feature name"},
                                "description": {"type": "string", "description": "Feature description"}
                            },
                            "required": ["epic_id", "name"]
                        }
                    },
                    # Tasks CRUD
                    {
                        "name": "list_tasks",
                        "description": "List all tasks or tasks for a feature",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "feature_id": {"type": "integer", "description": "Feature ID (optional)"}
                            }
                        }
                    },
                    {
                        "name": "create_task",
                        "description": "Create new task",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "feature_id": {"type": "integer", "description": "Feature ID"},
                                "title": {"type": "string", "description": "Task title"},
                                "description": {"type": "string", "description": "Task description"},
                                "assigned_role": {"type": "string", "description": "Target role", "enum": ["frontend_dev", "backend_dev", "architect", "pm", "qa"]},
                                "difficulty": {"type": "string", "description": "Difficulty level", "enum": ["junior", "senior", "principal"]},
                                "complexity": {"type": "string", "description": "Task complexity", "enum": ["minor", "major"]}
                            },
                            "required": ["feature_id", "title", "assigned_role", "difficulty", "complexity"]
                        }
                    },
                    {
                        "name": "delete_task",
                        "description": "Delete task",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "integer", "description": "Task ID"}
                            },
                            "required": ["task_id"]
                        }
                    },
                    # Documents CRUD
                    {
                        "name": "list_documents",
                        "description": "List documents in current project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "author_id": {"type": "string", "description": "Filter by author ID"},
                                "doc_type": {"type": "string", "description": "Filter by document type", "enum": ["comment", "update", "question", "announcement", "decision", "report"]}
                            }
                        }
                    },
                    {
                        "name": "get_document",
                        "description": "Get document details",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "integer", "description": "Document ID"}
                            },
                            "required": ["document_id"]
                        }
                    },
                    {
                        "name": "create_document",
                        "description": "Create new document",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "description": "Document type", "enum": ["comment", "update", "question", "announcement", "decision", "report"]},
                                "title": {"type": "string", "description": "Document title"},
                                "content": {"type": "string", "description": "Document content"},
                                "author_id": {"type": "string", "description": "Author ID"}
                            },
                            "required": ["type", "title", "content", "author_id"]
                        }
                    },
                    # Agents CRUD
                    {
                        "name": "list_agents",
                        "description": "List agents in current project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "delete_agent",
                        "description": "Delete agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string", "description": "Agent ID"}
                            },
                            "required": ["agent_id"]
                        }
                    },
                    # Services CRUD
                    {
                        "name": "list_services",
                        "description": "List services in current project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "register_service",
                        "description": "Register a new service",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Service name"},
                                "type": {"type": "string", "description": "Service type"},
                                "endpoint_url": {"type": "string", "description": "Service endpoint URL"},
                                "ping_url": {"type": "string", "description": "Health check URL"},
                                "metadata": {"type": "object", "description": "Additional metadata"}
                            },
                            "required": ["name", "type", "endpoint_url"]
                        }
                    },
                    {
                        "name": "unregister_service",
                        "description": "Unregister a service",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service_name": {"type": "string", "description": "Service name"}
                            },
                            "required": ["service_name"]
                        }
                    },
                    # Mentions
                    {
                        "name": "get_mentions",
                        "description": "Get mentions for current agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "unread_only": {"type": "boolean", "description": "Show only unread mentions", "default": false}
                            }
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool = params.get("name")
            args = params.get("arguments", {})
            
            if tool == "list_projects":
                response = api_request("GET", "/projects")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = "Available projects:\n"
                    for project in response:
                        text += f"  {project['id']}: {project['name']} - {project['description']}\n"
            
            elif tool == "select_project":
                global current_project_id
                project_id = args["project_id"]
                # Verify project exists
                response = api_request("GET", f"/projects/{project_id}")
                if "error" in response:
                    text = f"Error: Project {project_id} not found"
                else:
                    current_project_id = project_id
                    text = f"Selected project {project_id}: {response['name']}"
            
            elif tool == "register_agent":
                global current_agent_id
                current_agent_id = args["agent_id"]
                
                if current_project_id:
                    # Register in specific project
                    response = api_request("POST", "/register", {
                        "agent_id": args["agent_id"],
                        "project_id": current_project_id,
                        "role": args["role"],
                        "level": args.get("skill_level", "senior"),
                        "connection_type": "mcp"
                    })
                    if "error" in response:
                        text = f"Error: {response['error']}"
                    else:
                        text = f"Registered as {args['role']} agent: {args['agent_id']} in project {current_project_id}"
                else:
                    # Register in all projects
                    projects_response = api_request("GET", "/projects")
                    if "error" in projects_response:
                        text = f"Error getting projects: {projects_response['error']}"
                    else:
                        success_count = 0
                        error_messages = []
                        
                        for project in projects_response:
                            response = api_request("POST", "/register", {
                                "agent_id": args["agent_id"],
                                "project_id": project["id"],
                                "role": args["role"],
                                "level": args.get("skill_level", "senior"),
                                "connection_type": "mcp"
                            })
                            
                            if "error" in response:
                                error_messages.append(f"Project {project['id']}: {response['error']}")
                            else:
                                success_count += 1
                        
                        if success_count > 0:
                            text = f"Registered as {args['role']} agent: {args['agent_id']} in {success_count} projects"
                            if error_messages:
                                text += f"\nErrors: {'; '.join(error_messages)}"
                        else:
                            text = f"Failed to register in any projects. Errors: {'; '.join(error_messages)}"
            
            elif tool == "create_project":
                payload = {
                    "name": args["name"],
                    "description": args["description"],
                    "repository_url": args["repository_url"],
                    "repository_main_branch": args.get("repository_main_branch", "main"),
                    "shared_path": args.get("shared_path", "/shared"),
                    "instructions_path": args.get("instructions_path", "/instructions"),
                    "project_docs_path": args.get("project_docs_path", "/docs")
                }
                
                # Add optional fields if provided
                if "code_guidelines_path" in args and args["code_guidelines_path"]:
                    payload["code_guidelines_path"] = args["code_guidelines_path"]
                if "repository_clone_path" in args and args["repository_clone_path"]:
                    payload["repository_clone_path"] = args["repository_clone_path"]
                
                response = api_request("POST", "/projects", payload)
                if "error" in response:
                    text = f"Error creating project: {response['error']}"
                else:
                    text = f"Created project '{response['name']}' (ID: {response['id']}) with repository: {response['repository_url']}"
                    # Auto-select the newly created project
                    global current_project_id
                    current_project_id = response['id']
            
            elif tool == "get_context":
                if current_project_id:
                    response = api_request("GET", f"/context/{current_project_id}")
                    if "error" in response:
                        text = f"Error: {response['error']}"
                    else:
                        text = json.dumps(response, indent=2)
                else:
                    text = "Error: Please select a project first using select_project or list projects to see available options"
            
            elif tool == "get_next_task":
                response = api_request("GET", "/tasks/next")
                if response and "id" in response:
                    text = f"Task {response['id']}: {response.get('title', 'Untitled')}\n{response.get('description', '')}"
                else:
                    text = "No tasks available"
            
            elif tool == "lock_task":
                task_id = args["task_id"]
                if not current_agent_id:
                    text = "Error: Please register as an agent first"
                else:
                    response = api_request("POST", f"/tasks/{task_id}/lock", {
                        "agent_id": current_agent_id
                    })
                    if "error" in response:
                        text = f"Error: {response['error']}"
                    else:
                        text = f"Task {task_id} locked by {current_agent_id}"
            
            elif tool == "update_task_status":
                task_id = args["task_id"]
                status = args["status"]
                if not current_agent_id:
                    text = "Error: Please register as an agent first"
                else:
                    response = api_request("PUT", f"/tasks/{task_id}/status", {
                        "status": status,
                        "agent_id": current_agent_id
                    })
                    if "error" in response:
                        text = f"Error: {response['error']}"
                    else:
                        text = f"Task {task_id} status updated to: {status} by {current_agent_id}"
            
            # Epics CRUD
            elif tool == "list_epics":
                response = api_request("GET", "/epics")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = "Epics:\n" + "\n".join([f"  {epic['id']}: {epic['name']} - {epic.get('description', 'No description')}" for epic in response])
            
            elif tool == "get_epic":
                epic_id = args["epic_id"]
                response = api_request("GET", f"/epics/{epic_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = json.dumps(response, indent=2)
            
            elif tool == "create_epic":
                payload = {"name": args["name"]}
                if "description" in args:
                    payload["description"] = args["description"]
                if "pm_id" in args:
                    payload["pm_id"] = args["pm_id"]
                
                response = api_request("POST", "/epics", payload)
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Created epic {response['id']}: {response['name']}"
            
            elif tool == "delete_epic":
                epic_id = args["epic_id"]
                response = api_request("DELETE", f"/epics/{epic_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Deleted epic {epic_id}"
            
            # Features CRUD
            elif tool == "list_features":
                epic_id = args["epic_id"]
                response = api_request("GET", f"/features/{epic_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Features for epic {epic_id}:\n" + "\n".join([f"  {feature['id']}: {feature['name']} - {feature.get('description', 'No description')}" for feature in response])
            
            elif tool == "create_feature":
                payload = {
                    "epic_id": args["epic_id"],
                    "name": args["name"]
                }
                if "description" in args:
                    payload["description"] = args["description"]
                
                response = api_request("POST", "/features", payload)
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Created feature {response['id']}: {response['name']}"
            
            # Tasks CRUD
            elif tool == "list_tasks":
                if "feature_id" in args:
                    response = api_request("GET", f"/tasks/feature/{args['feature_id']}")
                    text_prefix = f"Tasks for feature {args['feature_id']}:\n"
                else:
                    response = api_request("GET", "/tasks")
                    text_prefix = "All tasks:\n"
                
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = text_prefix + "\n".join([f"  {task['id']}: {task['title']} [{task['status']}] - {task.get('description', 'No description')}" for task in response])
            
            elif tool == "create_task":
                payload = {
                    "feature_id": args["feature_id"],
                    "title": args["title"],
                    "assigned_role": args["assigned_role"],
                    "difficulty": args["difficulty"],
                    "complexity": args["complexity"]
                }
                if "description" in args:
                    payload["description"] = args["description"]
                
                response = api_request("POST", "/tasks/create", payload)
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Created task {response['id']}: {response['title']}"
            
            elif tool == "delete_task":
                task_id = args["task_id"]
                response = api_request("DELETE", f"/tasks/{task_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Deleted task {task_id}"
            
            # Documents CRUD
            elif tool == "list_documents":
                params = []
                if "author_id" in args:
                    params.append(f"author_id={args['author_id']}")
                if "doc_type" in args:
                    params.append(f"type={args['doc_type']}")
                
                query_string = "&" + "&".join(params) if params else ""
                response = api_request("GET", f"/documents?{query_string}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = "Documents:\n" + "\n".join([f"  {doc['id']}: {doc['title']} [{doc['doc_type']}] by {doc['author_id']}" for doc in response])
            
            elif tool == "get_document":
                document_id = args["document_id"]
                response = api_request("GET", f"/documents/{document_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = json.dumps(response, indent=2)
            
            elif tool == "create_document":
                payload = {
                    "type": args["type"],
                    "title": args["title"],
                    "content": args["content"],
                    "author_id": args["author_id"]
                }
                
                response = api_request("POST", "/documents", payload)
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Created document {response['id']}: {response['title']}"
            
            # Agents CRUD
            elif tool == "list_agents":
                params = f"?project_id={current_project_id}" if current_project_id else ""
                response = api_request("GET", f"/agents{params}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = "Agents:\n" + "\n".join([f"  {agent['agent_id']}: {agent['role']} ({agent['level']}) - {agent.get('connection_type', 'client')}" for agent in response])
            
            elif tool == "delete_agent":
                agent_id = args["agent_id"]
                response = api_request("DELETE", f"/agents/{agent_id}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Deleted agent {agent_id}"
            
            # Services CRUD
            elif tool == "list_services":
                response = api_request("GET", "/services")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = "Services:\n" + "\n".join([f"  {service['name']}: {service['type']} [{service['status']}] - {service['endpoint_url']}" for service in response])
            
            elif tool == "register_service":
                payload = {
                    "name": args["name"],
                    "type": args["type"],
                    "endpoint_url": args["endpoint_url"]
                }
                if "ping_url" in args:
                    payload["ping_url"] = args["ping_url"]
                if "metadata" in args:
                    payload["metadata"] = args["metadata"]
                
                response = api_request("POST", "/services/register", payload)
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Registered service {response['name']}"
            
            elif tool == "unregister_service":
                service_name = args["service_name"]
                response = api_request("DELETE", f"/services/{service_name}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    text = f"Unregistered service {service_name}"
            
            # Mentions
            elif tool == "get_mentions":
                unread_only = args.get("unread_only", False)
                params = f"?unread_only={'true' if unread_only else 'false'}"
                if current_agent_id:
                    params += f"&agent_id={current_agent_id}"
                
                response = api_request("GET", f"/mentions{params}")
                if "error" in response:
                    text = f"Error: {response['error']}"
                else:
                    if not response:
                        text = "No mentions found"
                    else:
                        text = "Mentions:\n" + "\n".join([f"  {mention['id']}: {mention.get('document_title', mention.get('task_title', 'Unknown'))} - {'unread' if not mention['is_read'] else 'read'}" for mention in response])
            
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
                        "uri": "headless-pm://projects",
                        "name": "Projects",
                        "description": "All available projects"
                    },
                    {
                        "uri": "headless-pm://tasks",
                        "name": "Tasks",
                        "description": "Current tasks in the system"
                    },
                    {
                        "uri": "headless-pm://epics",
                        "name": "Epics",
                        "description": "Epics in current project"
                    },
                    {
                        "uri": "headless-pm://features",
                        "name": "Features",
                        "description": "Features in current project"
                    },
                    {
                        "uri": "headless-pm://agents",
                        "name": "Agents",
                        "description": "Registered agents"
                    },
                    {
                        "uri": "headless-pm://documents",
                        "name": "Documents",
                        "description": "Documents in current project"
                    },
                    {
                        "uri": "headless-pm://services",
                        "name": "Services",
                        "description": "Registered services"
                    },
                    {
                        "uri": "headless-pm://context",
                        "name": "Project Context",
                        "description": "Current project context and configuration"
                    }
                ]
            }
        
        elif method == "resources/read":
            uri = params.get("uri", "")
            
            if uri == "headless-pm://projects":
                response = api_request("GET", "/projects")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://tasks":
                response = api_request("GET", "/tasks")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://epics":
                response = api_request("GET", "/epics")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://features":
                if current_project_id:
                    # Get all epics for current project, then all features
                    epics_response = api_request("GET", "/epics")
                    all_features = []
                    if "error" not in epics_response:
                        for epic in epics_response:
                            features_response = api_request("GET", f"/features/{epic['id']}")
                            if "error" not in features_response:
                                all_features.extend(features_response)
                    content = json.dumps(all_features, indent=2)
                else:
                    content = json.dumps({"error": "No project selected"}, indent=2)
            elif uri == "headless-pm://agents":
                params_str = f"?project_id={current_project_id}" if current_project_id else ""
                response = api_request("GET", f"/agents{params_str}")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://documents":
                response = api_request("GET", "/documents")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://services":
                response = api_request("GET", "/services")
                content = json.dumps(response, indent=2)
            elif uri == "headless-pm://context":
                if current_project_id:
                    response = api_request("GET", f"/context/{current_project_id}")
                    content = json.dumps(response, indent=2)
                else:
                    content = json.dumps({"error": "No project selected. Use select_project tool first."}, indent=2)
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