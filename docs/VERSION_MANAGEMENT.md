# Version Management Guide

This guide explains how to manage versions in the Headless PM project using the automated version bump script.

## Overview

The `scripts/bump_version.sh` script provides automated version management for all components of Headless PM. It can bump versions individually or all at once, update all relevant files, create git commits and tags, and push to the remote repository.

## Components

The project has three main components that can be versioned:

- **api** - FastAPI server and related API files
- **dashboard** - Next.js web dashboard  
- **mcp** - All MCP (Model Context Protocol) server implementations
- **all** - All components together

## Version Types

Follows semantic versioning (SemVer):

- **major** - Breaking changes (X.0.0)
- **minor** - New features, backward compatible (X.Y.0)  
- **patch** - Bug fixes, backward compatible (X.Y.Z)

## Usage

### Basic Usage

```bash
# Bump API to next major version
./scripts/bump_version.sh api major

# Bump dashboard to next minor version
./scripts/bump_version.sh dashboard minor

# Bump all MCP servers to next patch version
./scripts/bump_version.sh mcp patch

# Bump all components to next major version
./scripts/bump_version.sh all major
```

### Options

```bash
# Dry run - see what would change without making changes
./scripts/bump_version.sh all major --dry-run

# Skip pushing to remote repository
./scripts/bump_version.sh api minor --no-push

# Skip creating git tag
./scripts/bump_version.sh dashboard patch --no-tag

# Force bump even if working directory is dirty
./scripts/bump_version.sh mcp major --force

# Combine options
./scripts/bump_version.sh all minor --dry-run --no-push
```

### Help

```bash
./scripts/bump_version.sh --help
```

## What the Script Does

### 1. Validation
- Checks if you're in a git repository
- Warns if not on main branch
- Verifies working directory is clean (unless `--force`)
- Validates remote points to ocontant repository

### 2. Version Calculation
- Reads current version from `src/main.py`
- Calculates new version based on type (major/minor/patch)
- Shows current and new version for confirmation

### 3. File Updates

#### API Component
- `src/main.py` - FastAPI application version
- `src/api/routes.py` - API route version information

#### Dashboard Component
- `dashboard/package.json` - NPM package version

#### MCP Component
- `src/mcp/server.py` - Main MCP server
- `src/mcp/http_server.py` - HTTP MCP server
- `src/mcp/simple_sse_server.py` - Simple SSE server
- `src/mcp/sse_server.py` - SSE server
- `src/mcp/stdio_bridge.py` - STDIO bridge
- `src/mcp/streamable_http_server.py` - Streamable HTTP server
- `src/mcp/websocket_server.py` - WebSocket server

#### All Components
Updates all files listed above when using `all` component.

### 4. Changelog Update
- Automatically adds entry to `docs/CHANGELOG.md`
- Includes component name, version, and date
- Documents what was updated

### 5. Git Operations
- Stages all changes (`git add -A`)
- Creates descriptive commit message
- Creates annotated git tag
- Pushes commit and tag to origin (unless disabled)

## Git Tags

The script creates meaningful git tags:

- **Individual components**: `api-v2.1.0`, `dashboard-v1.5.2`, `mcp-v3.0.0`
- **All components**: `v2.0.0`

## Examples

### Release Workflow

```bash
# 1. Prepare for major release
./scripts/bump_version.sh all major --dry-run

# 2. Execute the release
./scripts/bump_version.sh all major

# 3. Verify the release
git log --oneline -3
git tag --list | tail -5
```

### Individual Component Updates

```bash
# API bug fix
./scripts/bump_version.sh api patch

# Dashboard new feature
./scripts/bump_version.sh dashboard minor

# MCP breaking change
./scripts/bump_version.sh mcp major
```

### Development Workflow

```bash
# Test changes without committing
./scripts/bump_version.sh dashboard minor --dry-run

# Bump version but don't push yet (for review)
./scripts/bump_version.sh api patch --no-push

# Later, push manually
git push origin main
git push origin api-v2.0.1
```

## Best Practices

### When to Use Each Version Type

#### Major Version Bump
- Database schema changes requiring migration
- Breaking API changes
- Removal of deprecated features
- Architectural overhauls

#### Minor Version Bump
- New features or endpoints
- Enhanced functionality
- New optional parameters
- Performance improvements

#### Patch Version Bump
- Bug fixes
- Security patches
- Documentation updates
- Minor performance tweaks

### Component-Specific Versioning

#### Use Individual Components When:
- Only one component changed significantly
- Testing specific component updates
- Gradual rollout of changes
- Component-specific hotfixes

#### Use All Components When:
- Major releases affecting entire system
- Coordinated feature releases
- Breaking changes across components
- Preparing for deployment

## Troubleshooting

### Common Issues

#### Working Directory Not Clean
```bash
# Check what's changed
git status

# Either commit or stash changes
git add . && git commit -m "WIP"
# OR
git stash

# Then run version bump
./scripts/bump_version.sh api major
```

#### Wrong Branch
```bash
# Switch to main branch
git checkout main

# Ensure it's up to date
git pull origin main

# Then run version bump
./scripts/bump_version.sh all minor
```

#### Remote Repository Issues
```bash
# Check remote configuration
git remote -v

# Should show ocontant repository
# If not, update remote
git remote set-url origin https://github.com/ocontant/headless_pm.git
```

#### Permission Denied
```bash
# Make script executable
chmod +x scripts/bump_version.sh

# Then run normally
./scripts/bump_version.sh dashboard patch
```

### Recovery from Failed Bump

If a version bump fails partway through:

```bash
# Reset to last commit (loses changes)
git reset --hard HEAD

# Or reset but keep changes staged
git reset --soft HEAD^

# Fix issues and try again
./scripts/bump_version.sh component version --force
```

## Script Output

The script provides colored output for easy monitoring:

- **🔵 INFO**: General information and progress
- **🟢 SUCCESS**: Successful operations
- **🟡 WARNING**: Warnings that don't stop execution
- **🔴 ERROR**: Errors that stop execution

### Example Output

```bash
$ ./scripts/bump_version.sh all minor

[INFO] Current version: 2.0.0
[INFO] New version: 2.1.0
[INFO] Updating API version to 2.1.0
[SUCCESS] Updated: src/main.py
[SUCCESS] Updated: src/api/routes.py
[INFO] Updating dashboard version to 2.1.0
[SUCCESS] Updated: dashboard/package.json
[INFO] Updating MCP version to 2.1.0
[SUCCESS] Updated: src/mcp/server.py
[SUCCESS] Updated: src/mcp/http_server.py
...
[SUCCESS] Updated changelog
[INFO] Staging changes...
[INFO] Creating commit...
[INFO] Creating tag: v2.1.0
[INFO] Pushing to origin...
[INFO] Pushing tag: v2.1.0
[SUCCESS] Version bump completed!
[SUCCESS] Component: all
[SUCCESS] Version: 2.0.0 → 2.1.0
[SUCCESS] Tag: v2.1.0
```

## Integration with CI/CD

The script can be integrated into automation workflows:

```bash
# In CI/CD pipeline
if [[ "$DEPLOY_TYPE" == "major" ]]; then
    ./scripts/bump_version.sh all major --no-push
elif [[ "$DEPLOY_TYPE" == "minor" ]]; then
    ./scripts/bump_version.sh all minor --no-push
else
    ./scripts/bump_version.sh all patch --no-push
fi

# Custom push logic in CI
git push origin main
git push origin --tags
```

## Security Considerations

- Script requires write access to repository
- Validates remote repository to prevent pushing to wrong location
- Prompts for confirmation on potentially dangerous operations
- Uses `--force` flag to override safety checks only when explicitly requested

## Maintenance

The script automatically handles:
- Finding all relevant files to update
- Calculating semantic version increments
- Creating consistent commit messages
- Managing git tags appropriately

To add new files for version updates, modify the appropriate `files` arrays in the script.