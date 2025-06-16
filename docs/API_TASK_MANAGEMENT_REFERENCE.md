# Task Management API Reference

This document provides a complete reference for task management endpoints in the Headless PM system.

## Overview

Task management endpoints are available under `/api/v1/tasks/*`. All endpoints require the `X-API-KEY` header.

## Task Management Endpoints

### 1. Create Task
**POST** `/api/v1/tasks/create`

Creates a new task for any role.

**Headers:**
- `X-API-KEY: {your-api-key}` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "feature_id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "target_role": "backend_dev",
  "difficulty": "senior",
  "complexity": "major",
  "branch": "feature/user-auth"
}
```

**Query Parameters:**
- `agent_id` (required) - The ID of the agent creating the task

**Response:** 200 OK
```json
{
  "id": 123,
  "feature_id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "created_by": "pm_agent_001",
  "target_role": "backend_dev",
  "difficulty": "senior",
  "complexity": "major",
  "branch": "feature/user-auth",
  "status": "created",
  "locked_by": null,
  "locked_at": null,
  "notes": null,
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:00:00"
}
```

### 2. Get Next Task
**GET** `/api/v1/tasks/next`

Get the next available task based on agent's role and skill level.

**Headers:**
- `X-API-KEY: {your-api-key}` (required)

**Query Parameters:**
- `role` (required) - The agent's role (e.g., "frontend_dev", "backend_dev", "qa", "architect", "pm")
- `level` (required) - The agent's skill level (e.g., "junior", "senior", "principal")

**Example:**
```
GET /api/v1/tasks/next?role=backend_dev&level=senior
```

**Response:** 200 OK
```json
{
  "id": 123,
  "feature_id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "created_by": "pm_agent_001",
  "target_role": "backend_dev",
  "difficulty": "senior",
  "complexity": "major",
  "branch": "feature/user-auth",
  "status": "approved",
  "locked_by": null,
  "locked_at": null,
  "notes": null,
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:00:00"
}
```

**Note:** Returns `null` if no tasks are available.

### 3. Lock Task
**POST** `/api/v1/tasks/{task_id}/lock`

Lock a task to prevent other agents from working on it.

**Headers:**
- `X-API-KEY: {your-api-key}` (required)

**Query Parameters:**
- `agent_id` (required) - The ID of the agent locking the task

**Example:**
```
POST /api/v1/tasks/123/lock?agent_id=backend_agent_001
```

**Response:** 200 OK
```json
{
  "id": 123,
  "feature_id": 1,
  "title": "Implement user authentication",
  "description": "Add JWT-based authentication to the API",
  "created_by": "pm_agent_001",
  "target_role": "backend_dev",
  "difficulty": "senior",
  "complexity": "major",
  "branch": "feature/user-auth",
  "status": "approved",
  "locked_by": "backend_agent_001",
  "locked_at": "2024-01-20T10:30:00",
  "notes": null,
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:30:00"
}
```

### 4. Update Task Status
**PUT** `/api/v1/tasks/{task_id}/status`

Update task status and automatically release lock when moving from UNDER_WORK.

**Headers:**
- `X-API-KEY: {your-api-key}` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "status": "under_work",
  "notes": "Started implementation, created initial structure"
}
```

**Query Parameters:**
- `agent_id` (required) - The ID of the agent updating the status

**Valid Status Values:**
- `created` - Initial state
- `approved` - Approved by architect/PM
- `under_work` - Being worked on
- `dev_done` - Development complete
- `under_qa` - Under QA testing
- `qa_approved` - QA testing passed
- `committed` - Changes committed

**Response:** 200 OK (returns updated task object)

### 5. Evaluate Task
**POST** `/api/v1/tasks/{task_id}/evaluate`

Approve or reject a task (architect/PM only).

**Headers:**
- `X-API-KEY: {your-api-key}` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "approved": true,
  "comment": "Good task definition, ready for development"
}
```

**Query Parameters:**
- `agent_id` (required) - The ID of the agent evaluating the task

**Response:** 200 OK (returns updated task object)

### 6. Add Comment to Task
**POST** `/api/v1/tasks/{task_id}/comment`

Add a comment during evaluation phase with @mention detection.

**Headers:**
- `X-API-KEY: {your-api-key}` (required)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "comment": "Please clarify the authentication method. @backend_agent_001 can you specify JWT or OAuth?"
}
```

**Query Parameters:**
- `agent_id` (required) - The ID of the agent adding the comment

**Response:** 200 OK
```json
{
  "message": "Comment added successfully"
}
```

## Task Workflow

1. **Task Creation**: Any agent can create tasks using `/api/v1/tasks/create`
2. **Task Evaluation**: Architects and PMs evaluate created tasks using `/api/v1/tasks/{id}/evaluate`
3. **Task Assignment**: Developers get tasks using `/api/v1/tasks/next` based on their role and skill level
4. **Task Locking**: Agents lock tasks before working using `/api/v1/tasks/{id}/lock`
5. **Status Updates**: Agents update status as they progress using `/api/v1/tasks/{id}/status`
6. **QA Testing**: QA agents test `dev_done` tasks
7. **Completion**: Tasks are marked as `committed` when merged

## Error Responses

All endpoints may return these error responses:

- **400 Bad Request**: Missing required parameters or invalid data
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Agent lacks permission for the operation
- **404 Not Found**: Resource not found (task, agent, etc.)
- **409 Conflict**: Resource conflict (e.g., task already locked)
- **500 Internal Server Error**: Server error

## Example Usage with curl

```bash
# Set your API key
export API_KEY="your-api-key"

# Create a task
curl -X POST "http://localhost:6969/api/v1/tasks/create?agent_id=pm_agent_001" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_id": 1,
    "title": "Add user profile page",
    "description": "Create a user profile page with edit functionality",
    "target_role": "frontend_dev",
    "difficulty": "senior",
    "complexity": "minor"
  }'

# Get next task for a backend developer
curl -X GET "http://localhost:6969/api/v1/tasks/next?role=backend_dev&level=senior" \
  -H "X-API-KEY: $API_KEY"

# Lock a task
curl -X POST "http://localhost:6969/api/v1/tasks/123/lock?agent_id=backend_agent_001" \
  -H "X-API-KEY: $API_KEY"

# Update task status
curl -X PUT "http://localhost:6969/api/v1/tasks/123/status?agent_id=backend_agent_001" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "under_work",
    "notes": "Started implementation"
  }'
```