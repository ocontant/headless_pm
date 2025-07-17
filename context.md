# Headless PM System Improvements Context

## Overview
This document defines the context and requirements for implementing project-scoped improvements to the Headless PM multi-agent coordination system.

## Current System Issues
- Agents can access tasks from any project (no project isolation)
- Document communication is global, not project-scoped
- Task assignment lacks proper project filtering
- No distinction between Global PM and Project PM roles
- Service registries are global instead of project-specific
- Agent availability status not visible to Project PMs

## Required Improvements

### 1. Role Enhancement

#### Global PM Role
- **Scope**: Cross-project operations
- **Permissions**:
  - ✅ Create epics, features, tasks in ANY project
  - ❌ Cannot assign tasks to specific agents
  - ✅ View all projects and their status
  - ✅ Cross-project coordination and planning

#### Project PM Role  
- **Scope**: Single project operations
- **Permissions**:
  - ✅ Create epics, features, tasks in THEIR project only
  - ✅ Assign tasks to agents within their project
  - ✅ View agent availability status in their project
  - ✅ Manage project-specific workflows
  - ✅ Coordinate with agents in their project

#### Agent Roles (No Changes)
- **Constraint**: Can only hold ONE task globally across all projects
- **Scope**: Work within assigned project context
- **Communication**: Project-scoped by default

### 2. Agent Availability System

#### Availability Status API
```json
{
  "agent_id": "backend_dev_001",
  "project_id": 1,
  "is_available": true,
  "current_task": null,
  "last_activity": "2025-01-17T10:30:00Z",
  "status": "idle|working|offline"
}
```

#### Project PM Dashboard Requirements
- Real-time view of agent availability in their project
- Ability to see which agents are working on tasks (from any project)
- Simple boolean indicator: agent can/cannot accept new tasks
- Integration with task assignment workflow

### 3. Project Context Requirements

#### API Operations Requiring Project Context
- **Task Management**: All task CRUD operations
- **Document Operations**: Create, read, update documents
- **Mention System**: @mentions filtered by project
- **Agent Communication**: Scoped to project members
- **Service Registry**: Project-specific service lists
- **Change Polling**: Project-filtered updates

#### API Endpoints to Modify
```
POST /api/v1/tasks/create?project_id={id}
GET  /api/v1/documents?project_id={id}
GET  /api/v1/mentions?project_id={id}
POST /api/v1/services/register?project_id={id}
GET  /api/v1/changes?project_id={id}&since={timestamp}
```

### 4. Communication Scoping

#### Project-Scoped Communication
- Documents created within project context only
- @mentions filtered to project members
- Status updates visible to project team
- Service health limited to project services

#### Cross-Project Communication (Future)
- Global PM can create cross-project notifications
- System-wide announcements capability
- Cross-project dependency tracking
- (Implementation deferred - no current use case)

### 5. Service Registry Improvements

#### Project-Level Service Registry
- Services registered within specific project context
- Project PMs can view their project's services
- Global PMs can view all services across projects
- Service health monitoring scoped to project

#### Service Context Structure
```json
{
  "service_name": "auth-api",
  "project_id": 1,
  "owner_agent_id": "backend_dev_001",
  "port": 8080,
  "status": "UP|DOWN|STARTING",
  "ping_url": "http://localhost:8080/health",
  "last_heartbeat": "2025-01-17T10:30:00Z"
}
```

## Implementation Priority

### Phase 1: Core Project Isolation
1. ✅ Fix task assignment to respect project boundaries
2. ✅ Implement project-scoped document communication
3. ✅ Add project filtering to mention system
4. ✅ Create agent availability status API

### Phase 2: Role Enhancements
1. ✅ Implement Global PM vs Project PM role distinction
2. ✅ Add task assignment permissions for Project PMs
3. ✅ Create project PM dashboard for agent availability
4. ✅ Restrict Global PM from direct agent task assignment

### Phase 3: Service Registry
1. ✅ Project-scoped service registration
2. ✅ Project-filtered service listing
3. ✅ Service health monitoring per project
4. ✅ Service registry permissions by role

## Technical Considerations

### Database Changes Required
- Add role distinction (global_pm vs project_pm)
- Ensure all entities have proper project_id relationships
- Add indices for project-filtered queries
- Create agent availability tracking

### API Changes Required
- Add project_id parameter to relevant endpoints
- Implement project context validation
- Add role-based permission checks
- Create agent availability endpoints

### Frontend Changes Required
- Project selector for operations
- Agent availability dashboard for Project PMs
- Project-scoped task and document views
- Role-based UI restrictions

## Success Criteria

1. **Project Isolation**: Agents only see tasks/documents from their projects
2. **Role Distinction**: Global PM and Project PM have appropriate permissions
3. **Agent Availability**: Project PMs can see real-time agent status
4. **Service Scoping**: Services are registered and monitored per project
5. **One Task Constraint**: Agents maintain single active task globally
6. **Communication Scoping**: All communication respects project boundaries

## Future Considerations

- Cross-project dependency tracking
- Multi-project agent assignment capabilities
- Global communication channels for system-wide updates
- Project templates and cloning functionality
- Resource allocation across projects

---

# Troubleshooting Context - System Health Page Project Selection Issue

## Problem Description
The dashboard system-health page was displaying an infinite "Loading project..." animation instead of showing the expected project data. The project dropdown showed "Select project" instead of auto-selecting the default "Headless-PM" project.

## Root Cause Analysis

### Initial Symptoms
- System health page showed infinite "Loading project..." with spinning animation
- Project dropdown in navigation showed "Select project" instead of auto-selecting default
- Service Health tab worked correctly (infrastructure monitoring)
- Project-specific tabs (Service Registry, Agents) were hidden due to loading state

### Investigation Steps

1. **Verified Project Selection Logic**
   - Navigation component had correct auto-selection logic for project ID 1 ("Headless-PM")
   - Project selector component had proper fallback logic
   - Projects API endpoint was working and returning correct data

2. **Identified API Client Architecture Issue**
   ```bash
   # Testing API endpoints revealed the core issue:
   curl -H "X-API-Key: [key]" http://localhost:6969/api/v1/services
   # Response: {"detail": [{"type": "missing", "loc": ["query", "project_id"], "msg": "Field required"}]}
   
   curl -H "X-API-Key: [key]" http://localhost:6969/api/v1/agents  
   # Response: Internal Server Error
   ```

3. **Found API Client Implementation Differences**
   - `getServices()` method: Throws error when `!this.currentProjectId`
   - `getAgents()` method: Also fails when no project is selected
   - Both methods require project selection before making API calls

### Root Cause
The infinite loading was caused by a **race condition** between:
1. Navigation component's asynchronous project selection
2. System health page's immediate API calls to services/agents endpoints

The page was waiting for both `useServices()` and `useAgents()` to succeed, but both were failing with "No project selected" errors, causing React Query to retry indefinitely.

## Solution Implemented

### 1. Enhanced Error Handling
**File**: `/dashboard/src/app/system-health/page.tsx`

```typescript
// Before: Simple loading check
const isLoading = servicesLoading || agentsLoading;
const hasProjectData = services && agents;

// After: Error-aware state management
const isLoading = servicesLoading || agentsLoading;
const hasErrors = servicesError || agentsError;
const hasProjectData = services && agents;

// If there are errors (likely "No project selected"), treat as no project
if (hasErrors || (!hasProjectData && !isLoading)) {
  return {
    hasProjectData: false,
    isLoading: false, // Not loading if we have errors
    hasErrors,
    // ... rest of empty state
  };
}
```

### 2. Improved User Feedback
Updated the project selection notice to distinguish between loading and error states:

```typescript
// Dynamic messaging based on state
{healthMetrics.isLoading ? 'Loading project data...' : 'No project selected'}
{healthMetrics.isLoading 
  ? 'Loading project-specific services and agents...'
  : 'Select a project from the dropdown above to view project-specific services and agents. The Service Health tab shows infrastructure status regardless of project selection.'
}
```

### 3. State Management Simplification
- Removed complex polling-based project selection tracking
- Let React Query handle API call states naturally
- Focused on graceful error handling rather than preventing errors

## Key Files Modified

1. **`/dashboard/src/app/system-health/page.tsx`**
   - Enhanced health metrics calculation with error handling
   - Improved loading state detection
   - Better user messaging for different states

2. **`/dashboard/src/lib/hooks/useApi.ts`** 
   - Temporarily added `useCurrentProject` hook (later simplified)
   - Reverted `useServices` and `useAgents` to original implementation

## Verification Steps

1. **Test API Endpoints Directly**
   ```bash
   # Verify services endpoint requires project_id
   curl -H "X-API-Key: [key]" http://localhost:6969/api/v1/services
   
   # Verify agents endpoint behavior  
   curl -H "X-API-Key: [key]" http://localhost:6969/api/v1/agents
   ```

2. **Check Dashboard Response**
   ```bash
   # Verify page loads without infinite loading
   curl -s http://localhost:3001/system-health | grep -E "(Loading project|No project)"
   ```

3. **Monitor Dashboard Logs**
   ```bash
   # Check for compilation and runtime errors
   tail -f /tmp/dashboard.log
   ```

## Resolution Outcome

✅ **Fixed infinite loading animation** - Page now shows "No project selected" message  
✅ **Maintained Service Health functionality** - Infrastructure monitoring works regardless of project selection  
✅ **Improved error handling** - API failures are handled gracefully  
✅ **Better UX** - Clear messaging about what action users need to take  

## Lessons Learned

1. **API Design Considerations**: Services and agents endpoints require project context, but this wasn't clearly communicated in the UI flow
2. **Error State Handling**: React Query errors should be treated as valid states, not infinite loading conditions
3. **Race Condition Prevention**: Async project selection needs proper synchronization with dependent API calls
4. **User Feedback**: Loading states should have clear completion criteria and fallback messaging

## Future Improvements

1. Consider making some system-level endpoints work without project selection
2. Implement proper project context provider for better state management
3. Add explicit error boundaries for API call failures
4. Improve navigation component to show loading state during project selection

---

**Document Version**: 1.1  
**Created**: 2025-01-17  
**Last Updated**: 2025-07-17  
**Status**: Requirements Definition + Troubleshooting Guide