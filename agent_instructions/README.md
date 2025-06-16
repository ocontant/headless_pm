# Agent instructions

It's easiest to  drop this entire directory into the root of your project. Then ask the LLM to read one of the files and assume that role. Make sure api key is configured in the .env file (example provided).

## Important: Enhanced Field Usage

**All agents should read `FIELD_USAGE_GUIDE.md`** - The system now supports unlimited text in description, notes, comment, and content fields. Use these fields to provide comprehensive, detailed information that minimizes communication overhead and helps the team work more efficiently.

## API Documentation

**Task Management API Reference**: See `/docs/API_TASK_MANAGEMENT_REFERENCE.md` for complete documentation of all task-related endpoints including:
- Creating tasks (`POST /api/v1/tasks/create`)
- Getting next task (`GET /api/v1/tasks/next`)
- Locking tasks (`POST /api/v1/tasks/{id}/lock`)
- Updating status (`PUT /api/v1/tasks/{id}/status`)
- Evaluating tasks (`POST /api/v1/tasks/{id}/evaluate`)
- Adding comments (`POST /api/v1/tasks/{id}/comment`)

**Task Status Guide**: See `/docs/TASK_STATUS_GUIDE.md` for understanding:
- What each status means (CREATED → APPROVED → UNDER_WORK → DEV_DONE → etc.)
- Who can set each status
- When to change statuses
- Proper status flow and progression

**Interactive API Documentation**: The API also provides interactive documentation at:
- Swagger UI: `http://localhost:6969/api/v1/docs`
- ReDoc: `http://localhost:6969/api/v1/redoc`
- OpenAPI Schema: `http://localhost:6969/api/v1/openapi.json`
