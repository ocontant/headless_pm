#!/bin/bash
# Create a separate virtual environment for Claude Code (x86_64)

set -e

echo "==================================="
echo "Creating Claude Code Environment"
echo "==================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine project root (parent of setup directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"
echo "Working from: $(pwd)"

# Remove existing claude_venv if it exists
if [ -d "claude_venv" ]; then
    echo "Removing existing claude_venv..."
    rm -rf claude_venv
fi

# Create new virtual environment
echo "Creating new virtual environment for x86_64..."
python3 -m venv claude_venv

# Activate the environment
source claude_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages without binaries (pure Python)
echo "Installing packages from source (no binaries)..."
pip install --no-binary :all: pydantic==2.10.5
pip install --no-binary :all: pydantic-core==2.27.2

# Install other requirements
pip install -r setup/requirements.txt --no-binary pydantic,pydantic-core

echo "==================================="
echo "Claude Code environment created!"
echo "==================================="
echo ""
echo "To use this environment in Claude Code:"
echo "  source claude_venv/bin/activate"
echo ""
echo "To run tests in Claude Code:"
echo "  source claude_venv/bin/activate"
echo "  python -m pytest tests/ -v"