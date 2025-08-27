# Auto-Git Repository Creation Implementation Plan

## Overview

Implement automatic Git repository creation during project setup with HTTP/HTTPS exposure for `git clone` operations.

## Current State Analysis

- **Project Creation**: Currently creates filesystem directories (`docs/`, `shared/`, `instructions/`) via `ensure_project_directories()`
- **Repository Fields**: Database already supports `repository_url`, `repository_main_branch`, `repository_clone_path`
- **File Structure**: Projects stored in `./projects/{sanitized-name}/`
- **Security**: Robust path sanitization and validation already implemented

## Implementation Plan

### Phase 1: Core Git Repository Auto-Creation (Medium Effort - 2-3 days)

#### 1.1 Extend Project Service (`src/services/project_service.py`)
- Add `create_git_repository()` function to `create_project()`
- Create bare Git repository: `git init --bare` in `{project_dir}/repo.git/`
- Initialize with default branch (main/master)
- Create initial commit with project structure

#### 1.2 Update Project Utils (`src/services/project_utils.py`)
- Add `get_project_repo_path()` function
- Extend `ensure_project_directories()` to include repo directory
- Add Git operations: `init_bare_repo()`, `create_initial_commit()`

#### 1.3 Dependencies
- Add `GitPython` or subprocess calls to `requirements.txt`
- Handle Git binary availability checks

### Phase 2: HTTP/HTTPS Git Server (High Effort - 5-7 days)

#### 2.1 Git HTTP Backend Implementation

**Option A: Embedded Git HTTP Server**
- Create new service: `src/services/git_http_service.py`
- Implement Git smart HTTP protocol
- Handle `git-upload-pack` and `git-receive-pack`
- Add authentication/authorization

**Option B: Nginx + git-http-backend (Recommended)**
- Add Nginx configuration for Git HTTP backend
- Configure `git-http-backend` CGI
- Route `/git/{project-name}.git` to project repositories
- Add Docker container or system package requirements

#### 2.2 API Routes (`src/api/git_routes.py`)
- `GET /git/{project-name}.git/*` - Git HTTP operations
- `GET /api/v1/projects/{id}/git/clone-url` - Get clone URL
- Authentication integration with existing API key system

#### 2.3 Database Schema Updates
- Extend `Project` model with `git_clone_url` field
- Migration to populate clone URLs for existing projects

### Phase 3: Integration & Configuration (Medium Effort - 2-3 days)

#### 3.1 Service Management
- Extend `scripts/manage_services.sh` to include Git HTTP service
- Add health checks for Git repository accessibility
- Configure ports (suggest: 8080 for Git HTTP)

#### 3.2 Environment Configuration
- Add `.env` variables: `GIT_HTTP_PORT`, `GIT_BASE_URL`, `GIT_AUTH_ENABLED`
- Update `env-example` with Git configuration options

#### 3.3 Dashboard Integration
- Display clone URLs in project details
- Add Git repository status indicators
- Show clone commands (HTTPS/SSH)

### Phase 4: Security & Authentication (Medium Effort - 1-2 days)

#### 4.1 Access Control
- Integrate with existing API key authentication
- Per-project access permissions
- Read/write access controls

#### 4.2 Security Hardening
- Rate limiting for Git operations
- Repository size limits
- Secure clone URL generation

## Technical Implementation Details

### Directory Structure (Post-Implementation)
```
./projects/{project-name}/
├── docs/                    # Project documentation
├── shared/                  # Shared files  
├── instructions/            # Agent instructions
├── code_guidelines/         # Code guidelines (optional)
└── repo.git/               # Bare Git repository
    ├── hooks/
    ├── objects/
    ├── refs/
    └── config
```

### Clone URL Format
- HTTP: `http://localhost:8080/git/{project-name}.git`
- HTTPS: `https://your-domain.com/git/{project-name}.git`

### New API Endpoints
```
GET  /git/{project-name}.git/info/refs        # Git smart HTTP
POST /git/{project-name}.git/git-upload-pack  # Git fetch/pull
POST /git/{project-name}.git/git-receive-pack # Git push
GET  /api/v1/projects/{id}/git/clone-url      # Get clone URL
```

## Effort Estimation

### Total Effort: **10-15 days** (2-3 weeks)
- **Phase 1** (Core Git): 2-3 days
- **Phase 2** (HTTP Server): 5-7 days  
- **Phase 3** (Integration): 2-3 days
- **Phase 4** (Security): 1-2 days

### Complexity Factors
- **Medium-High**: Git HTTP protocol implementation
- **Medium**: Service integration and configuration
- **Low-Medium**: Database and UI updates

### Dependencies
- Git binary installation
- Nginx (recommended) or custom HTTP server
- Additional Python packages (GitPython)
- Port configuration (8080 for Git HTTP)

## Benefits
- **Seamless Workflow**: Projects automatically get Git repositories
- **Immediate Cloning**: `git clone` works immediately after project creation
- **Standard Git Operations**: Full Git functionality (push, pull, branch, merge)
- **Multi-Agent Collaboration**: Teams can work on shared repositories
- **Branch Management**: Automated branch creation aligns with task system

## Alternative Approaches
1. **External Git Hosting**: Integrate with GitHub/GitLab APIs (lower effort, external dependency)
2. **Git Daemon**: Use `git daemon` instead of HTTP (simpler, less secure)
3. **Shared Filesystem**: NFS/SMB mounted repos (deployment complexity)

## Implementation Notes

### Prerequisite Work
This plan assumes the repository configuration foundation is already in place:
- Database schema with repository fields ✅ (completed in `feature/project-repository-integration` branch)
- Project creation UI with repository configuration ✅
- API schemas for repository data ✅
- Migration scripts for existing projects ✅

### Integration with Existing Features
- **Task Management**: Generated branch names will align with task branches
- **Multi-Project Architecture**: Each project gets its own isolated Git repository
- **Security Model**: Leverage existing authentication and authorization
- **Service Management**: Use existing service orchestration patterns

### Deployment Considerations
- **Development**: Local Git HTTP server for testing
- **Production**: Nginx + git-http-backend for performance and security
- **Scaling**: Repository storage and backup strategies
- **Monitoring**: Git operation metrics and health checks

This implementation provides a complete Git workflow integration while maintaining the existing multi-project architecture and security standards.