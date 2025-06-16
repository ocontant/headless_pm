# Task Status Guide

## Overview
This guide explains each task status, who can set them, and when to use them. Understanding these statuses is critical for smooth team coordination.

## Status Flow Diagram
```
CREATED → APPROVED → UNDER_WORK → DEV_DONE → QA_DONE → DOCUMENTATION_DONE → COMMITTED
   ↓         ↓           ↓            ↓         ↓              ↓
EVALUATION  (rejected)  (blocked)   (failed)  (failed)     (failed)
```

## Status Definitions

### 1. CREATED
- **Description**: Initial state when a task is created
- **Who sets it**: Any agent creating a task
- **Next steps**: Awaits evaluation by Architect/PM
- **Who can work on it**: Architects and PMs only (for evaluation)

### 2. EVALUATION (Not implemented in current system)
- **Note**: Tasks go directly from CREATED to APPROVED/rejected

### 3. APPROVED
- **Description**: Task has been reviewed and approved for development
- **Who sets it**: Architects or PMs only
- **Next steps**: Ready for developers to pick up
- **Who can work on it**: Developers matching the target_role and difficulty

### 4. UNDER_WORK
- **Description**: A developer has locked and is actively working on the task
- **Who sets it**: The developer who locked the task
- **When to set**: Immediately after locking the task and starting work
- **Important**: Only ONE task should be UNDER_WORK per agent at a time

### 5. DEV_DONE
- **Description**: Development is complete, ready for QA testing
- **Who sets it**: The developer who completed the work
- **When to set**: After completing implementation, passing local tests, and committing code
- **Next steps**: QA picks up for testing
- **Note**: Lock is automatically released when moving from UNDER_WORK to DEV_DONE

### 6. QA_DONE
- **Description**: QA testing passed, ready for documentation review
- **Who sets it**: QA engineer after successful testing
- **When to set**: After all tests pass and no critical bugs remain
- **If tests fail**: Task goes back to APPROVED for fixes

### 7. DOCUMENTATION_DONE
- **Description**: Documentation has been updated/verified
- **Who sets it**: Usually the developer or technical writer
- **When to set**: After ensuring all docs, comments, and README updates are complete

### 8. COMMITTED
- **Description**: Final state - code is merged to main branch
- **Who sets it**: The developer after merging
- **When to set**: 
  - For MINOR tasks: After pushing directly to main
  - For MAJOR tasks: After PR is approved and merged

## Status Update Examples

### Developer Starting Work
```bash
# 1. Get next task
GET /api/v1/tasks/next?role=backend_dev&level=senior

# 2. Lock the task
POST /api/v1/tasks/123/lock?agent_id=backend_dev_senior_001

# 3. Update status to UNDER_WORK
PUT /api/v1/tasks/123/status?agent_id=backend_dev_senior_001
{
  "status": "under_work",
  "notes": "Starting implementation of authentication API"
}
```

### Developer Completing Work
```bash
PUT /api/v1/tasks/123/status?agent_id=backend_dev_senior_001
{
  "status": "dev_done",
  "notes": "Implementation complete. All unit tests passing. Ready for QA."
}
```

### QA Testing Complete
```bash
PUT /api/v1/tasks/123/status?agent_id=qa_senior_001
{
  "status": "qa_done",
  "notes": "All tests passed. Performance and security validated. Ready for release."
}
```

### Task Committed
```bash
PUT /api/v1/tasks/123/status?agent_id=backend_dev_senior_001
{
  "status": "committed",
  "notes": "Merged to main in commit abc123. CI/CD pipeline successful."
}
```

## Important Rules

1. **Lock Before Work**: Always lock a task before changing its status to UNDER_WORK
2. **One Active Task**: Only have one task in UNDER_WORK status at a time
3. **Auto-unlock**: Tasks automatically unlock when moving away from UNDER_WORK
4. **Status Progression**: Follow the status flow - don't skip statuses
5. **Add Notes**: Always include descriptive notes when updating status

## Rollback Scenarios

### QA Finds Bugs
- QA changes status from DEV_DONE back to APPROVED
- Creates bug report document
- Original developer (or another) picks it up again

### Documentation Issues
- If docs are incomplete, status can go from DOCUMENTATION_DONE back to DEV_DONE
- Developer updates documentation and sets back to DOCUMENTATION_DONE

## Status Visibility

### Check Task Status
```bash
# Via CLI
python -m src.cli.main tasks --status=under_work

# Via API
GET /api/v1/changelog?limit=20
```

### Monitor Team Progress
```bash
# Real-time dashboard
python -m src.cli.main dashboard

# Status summary
python -m src.cli.main status
```

## Best Practices

1. **Update Immediately**: Change status as soon as your work phase changes
2. **Be Descriptive**: Add clear notes explaining what was done
3. **Communicate Blocks**: If stuck, update notes and create a document
4. **Review Before Moving**: Ensure all criteria are met before advancing status
5. **Document Failures**: When moving backward, clearly explain why