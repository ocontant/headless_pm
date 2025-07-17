#!/bin/bash
# Universal setup script that works for both ARM64 and x86_64

set -e

echo "==================================="
echo "Universal Environment Setup"
echo "==================================="

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Determine which venv to use
if [[ "$ARCH" == "arm64" ]]; then
    VENV_NAME="venv"
    echo "Using standard venv for ARM64"
else
    VENV_NAME="claude_venv"
    echo "Using claude_venv for x86_64"
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine project root (parent of setup directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"
echo "Working from: $(pwd)"

# Create appropriate virtual environment
if [ ! -d "$VENV_NAME" ]; then
    echo "Creating virtual environment: $VENV_NAME"
    python3 -m venv $VENV_NAME
fi

# Activate the environment
source $VENV_NAME/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages based on architecture
if [[ "$ARCH" == "arm64" ]]; then
    # Standard installation for ARM64
    echo "Installing packages normally for ARM64..."
    pip install -r setup/requirements.txt
else
    # Install for x86_64 (Claude Code compatibility)
    echo "Installing packages for x86_64..."
    
    # First, install pydantic with specific versions that work in Claude Code
    pip install pydantic==2.11.7 pydantic-core==2.33.2
    
    # Then install the rest of the requirements
    pip install -r setup/requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f "env-example" ]; then
    echo "Creating .env from env-example..."
    cp env-example .env
fi

echo ""
echo "==================================="
echo "Database Setup"
echo "==================================="

# Initialize database
echo "Initializing database..."
python -m src.cli.main init

# Check if we need to run migrations
echo "Checking for database migrations..."
if python -c "
import sys
sys.path.append('.')
from src.models.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM project'))
        print('Projects table exists')
        sys.exit(0)
except:
    print('Projects table missing - migration needed')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ Database schema is up to date"
else
    echo "Running project support migration..."
    python migrations/add_project_support.py
    echo "✅ Migration completed successfully"
fi

# Create default project if none exists
echo "Checking for default project..."
if python -c "
import sys
sys.path.append('.')
from src.models.database import get_session
from src.models.models import Project
from sqlmodel import select
try:
    db = next(get_session())
    projects = db.exec(select(Project)).all()
    if len(projects) == 0:
        print('No projects found - creating default')
        sys.exit(1)
    else:
        print(f'Found {len(projects)} project(s)')
        sys.exit(0)
except Exception as e:
    print(f'Error checking projects: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ Projects exist in database"
else
    echo "Creating default project..."
    python -c "
import sys
sys.path.append('.')
from src.models.database import get_session
from src.models.models import Project
import os
from datetime import datetime

try:
    db = next(get_session())
    
    # Create default project
    default_project = Project(
        name='Default',
        description='Default project for Headless PM',
        shared_path=os.getenv('SHARED_PATH', './shared'),
        instructions_path=os.getenv('INSTRUCTIONS_PATH', './agent_instructions'),
        project_docs_path=os.getenv('PROJECT_DOCS_PATH', './docs')
    )
    
    db.add(default_project)
    db.commit()
    db.refresh(default_project)
    
    print(f'✅ Created default project (ID: {default_project.id})')
    
except Exception as e:
    print(f'❌ Error creating default project: {e}')
    sys.exit(1)
"
fi

echo ""
echo "==================================="
echo "Setup complete!"
echo "==================================="
echo ""
echo "Environment: $VENV_NAME"
echo "Architecture: $ARCH"
echo ""
echo "To activate this environment:"
echo "  source $VENV_NAME/bin/activate"
echo ""
echo "To run the application:"
echo "  ./start.sh"
echo ""
echo "To run tests:"
echo "  python -m pytest tests/"
echo ""
echo "Multi-Project Features:"
echo "  List projects:    ./agents/client/headless_pm_client.py projects list"
echo "  Create project:   ./agents/client/headless_pm_client.py projects create --name 'My Project' --description 'Description'"
echo "  Register agent:   ./agents/client/headless_pm_client.py register --agent-id 'dev_001' --project-id 1 --role backend_dev --level senior"