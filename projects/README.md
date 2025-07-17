# Projects Directory

This directory contains project-specific documentation and files managed by the Headless PM application.

## Structure

```
projects/
├── {project_name}/     # Sanitized project name (e.g., "headless-pm", "my-app")
│   ├── docs/           # Project-specific documentation
│   ├── shared/         # Shared files for this project
│   └── instructions/   # Agent instructions for this project
└── README.md          # This file
```

## Project Documentation

Each project has its own dedicated documentation directory using the sanitized project name:
- `projects/{project_name}/docs/` - Project-specific documentation files
- `projects/{project_name}/shared/` - Shared resources for the project
- `projects/{project_name}/instructions/` - Agent-specific instructions

### Name Sanitization

Project names are automatically sanitized for filesystem safety:
- Special characters removed (keeping alphanumeric, hyphens, underscores)
- Spaces converted to hyphens
- Multiple consecutive separators collapsed
- Converted to lowercase
- Limited to 50 characters

## Application vs Project Documentation

- **Application Documentation**: `/docs/` - Contains Headless PM application documentation, API references, and system guides
- **Project Documentation**: `/projects/{project_name}/docs/` - Contains project-specific documentation managed by agents

## API Access

Project documentation is accessible via API using project IDs (which internally map to project names):
- `GET /api/v1/projects/{project_id}/docs` - List project documentation files
- `GET /api/v1/projects/{project_id}/docs/{file_path}` - Retrieve specific documentation file
- `POST /api/v1/projects/{project_id}/docs/{file_path}` - Create/update documentation file

The API automatically maps project IDs to their sanitized names for filesystem operations.