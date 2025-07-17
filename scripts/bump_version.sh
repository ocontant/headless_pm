#!/bin/bash

# Headless PM Version Bump Script
# Bumps version for individual components or all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Version types
MAJOR="major"
MINOR="minor"
PATCH="patch"

# Components
API="api"
DASHBOARD="dashboard"
MCP="mcp"
ALL="all"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_usage() {
    cat << EOF
Usage: $0 <component> <version_type> [options]

Components:
  api        - API server (FastAPI)
  dashboard  - Web dashboard (Next.js)
  mcp        - MCP servers
  all        - All components

Version Types:
  major      - Major version bump (X.0.0)
  minor      - Minor version bump (X.Y.0)
  patch      - Patch version bump (X.Y.Z)

Options:
  --dry-run  - Show what would be changed without making changes
  --no-push  - Skip pushing to remote repository
  --no-tag   - Skip creating git tag
  --force    - Force version bump even if working directory is dirty

Examples:
  $0 api major                    # Bump API to next major version
  $0 dashboard minor              # Bump dashboard to next minor version
  $0 all patch                    # Bump all components to next patch version
  $0 mcp major --dry-run          # Show what would change for MCP major bump
  $0 all minor --no-push          # Bump all but don't push to remote

EOF
}

# Parse command line arguments
COMPONENT=""
VERSION_TYPE=""
DRY_RUN=false
NO_PUSH=false
NO_TAG=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        api|dashboard|mcp|all)
            COMPONENT="$1"
            shift
            ;;
        major|minor|patch)
            VERSION_TYPE="$1"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-push)
            NO_PUSH=true
            shift
            ;;
        --no-tag)
            NO_TAG=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate arguments
if [[ -z "$COMPONENT" || -z "$VERSION_TYPE" ]]; then
    log_error "Component and version type are required"
    show_usage
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Check if git working directory is clean
if [[ "$FORCE" != "true" ]]; then
    if ! git diff-index --quiet HEAD --; then
        log_error "Working directory is not clean. Use --force to override or commit your changes."
        exit 1
    fi
fi

# Get current version from main API file
get_current_version() {
    grep -oP 'version="\K[^"]+' src/main.py | head -1
}

# Parse version string into components
parse_version() {
    local version="$1"
    echo "$version" | sed 's/\([0-9]*\)\.\([0-9]*\)\.\([0-9]*\).*/\1 \2 \3/'
}

# Increment version based on type
increment_version() {
    local current_version="$1"
    local version_type="$2"
    
    read -r major minor patch <<< "$(parse_version "$current_version")"
    
    case "$version_type" in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "${major}.$((minor + 1)).0"
            ;;
        patch)
            echo "${major}.${minor}.$((patch + 1))"
            ;;
        *)
            log_error "Invalid version type: $version_type"
            exit 1
            ;;
    esac
}

# Update version in API files
update_api_version() {
    local new_version="$1"
    local files=(
        "src/main.py"
        "src/api/routes.py"
    )
    
    log_info "Updating API version to $new_version"
    
    for file in "${files[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would update: $file"
        else
            sed -i "s/version=\"[^\"]*\"/version=\"$new_version\"/g" "$file"
            log_success "Updated: $file"
        fi
    done
}

# Update version in MCP files
update_mcp_version() {
    local new_version="$1"
    local files=(
        "src/mcp/server.py"
        "src/mcp/http_server.py"
        "src/mcp/simple_sse_server.py"
        "src/mcp/sse_server.py"
        "src/mcp/stdio_bridge.py"
        "src/mcp/streamable_http_server.py"
        "src/mcp/websocket_server.py"
    )
    
    log_info "Updating MCP version to $new_version"
    
    for file in "${files[@]}"; do
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "Would update: $file"
        else
            sed -i "s/version=\"[^\"]*\"/version=\"$new_version\"/g" "$file"
            sed -i "s/server_version=\"[^\"]*\"/server_version=\"$new_version\"/g" "$file"
            log_success "Updated: $file"
        fi
    done
}

# Update version in dashboard
update_dashboard_version() {
    local new_version="$1"
    local file="dashboard/package.json"
    
    log_info "Updating dashboard version to $new_version"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Would update: $file"
    else
        sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/g" "$file"
        log_success "Updated: $file"
    fi
}

# Update changelog
update_changelog() {
    local component="$1"
    local new_version="$2"
    local version_type="$3"
    local file="docs/CHANGELOG.md"
    
    local component_name=""
    case "$component" in
        api) component_name="API Server" ;;
        dashboard) component_name="Dashboard" ;;
        mcp) component_name="MCP Servers" ;;
        all) component_name="All Components" ;;
    esac
    
    local date=$(date +"%B %d, %Y")
    local entry="### 🔄 ${component_name} Version ${new_version}
**Date**: ${date}  
**Type**: ${version_type^} version bump

#### 📦 Updated Components"
    
    if [[ "$component" == "all" ]]; then
        entry="${entry}
- **Main API**: Updated to ${new_version}
- **Dashboard**: Updated to ${new_version}
- **MCP Servers**: All updated to ${new_version}"
    else
        entry="${entry}
- **${component_name}**: Updated to ${new_version}"
    fi
    
    entry="${entry}

"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Would add changelog entry for $component_name $new_version"
    else
        # Insert after the first line containing "## Recent Major Updates"
        sed -i "/## Recent Major Updates/a\\
\\
${entry}" "$file"
        log_success "Updated changelog"
    fi
}

# Main version bump logic
bump_version() {
    local component="$1"
    local version_type="$2"
    
    # Get current version
    local current_version
    current_version=$(get_current_version)
    
    if [[ -z "$current_version" ]]; then
        log_error "Could not determine current version"
        exit 1
    fi
    
    log_info "Current version: $current_version"
    
    # Calculate new version
    local new_version
    new_version=$(increment_version "$current_version" "$version_type")
    
    log_info "New version: $new_version"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Update components based on selection
    case "$component" in
        api)
            update_api_version "$new_version"
            ;;
        dashboard)
            update_dashboard_version "$new_version"
            ;;
        mcp)
            update_mcp_version "$new_version"
            ;;
        all)
            update_api_version "$new_version"
            update_dashboard_version "$new_version"
            update_mcp_version "$new_version"
            ;;
    esac
    
    # Update changelog
    update_changelog "$component" "$new_version" "$version_type"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry run completed. No changes were made."
        return 0
    fi
    
    # Git operations
    log_info "Staging changes..."
    git add -A
    
    # Create commit message
    local commit_msg="Bump ${component} version to ${new_version}

## Version Update
- ${component^} version bumped from ${current_version} to ${new_version}
- Type: ${version_type^} version bump
- Updated changelog with version information

Co-Authored-By: ocontant <ocontant@users.noreply.github.com>"
    
    log_info "Creating commit..."
    git commit -m "$commit_msg"
    
    local tag_name=""
    if [[ "$component" == "all" ]]; then
        tag_name="v${new_version}"
    else
        tag_name="${component}-v${new_version}"
    fi
    
    # Create tag if not disabled
    if [[ "$NO_TAG" != "true" ]]; then
        log_info "Creating tag: $tag_name"
        git tag -a "$tag_name" -m "${component^} version ${new_version}"
    fi
    
    # Push to remote if not disabled
    if [[ "$NO_PUSH" != "true" ]]; then
        log_info "Pushing to origin..."
        git push origin main
        
        if [[ "$NO_TAG" != "true" ]]; then
            log_info "Pushing tag: $tag_name"
            git push origin "$tag_name"
        fi
    fi
    
    log_success "Version bump completed!"
    log_success "Component: $component"
    log_success "Version: $current_version → $new_version"
    log_success "Tag: $tag_name"
    
    if [[ "$NO_PUSH" == "true" ]]; then
        log_warning "Changes were not pushed to remote (--no-push used)"
    fi
}

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
    exit 1
fi

# Verify we're on the main branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    log_warning "Not on main branch (currently on: $current_branch)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Aborted"
        exit 0
    fi
fi

# Check if remote origin exists and points to ocontant
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$remote_url" != *"ocontant"* ]]; then
    log_warning "Remote origin does not appear to point to ocontant repository"
    log_warning "Current origin: $remote_url"
    if [[ "$NO_PUSH" != "true" ]]; then
        read -p "Continue with push? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Use --no-push to skip pushing"
            exit 0
        fi
    fi
fi

# Run the version bump
log_info "Starting version bump for $COMPONENT ($VERSION_TYPE)"
bump_version "$COMPONENT" "$VERSION_TYPE"