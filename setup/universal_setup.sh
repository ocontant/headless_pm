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
    # Install from source for x86_64
    echo "Installing packages from source for x86_64..."
    pip install --no-binary :all: pydantic==2.10.5 || echo "Pydantic installation may have issues"
    pip install --no-binary :all: pydantic-core==2.27.2 || echo "Pydantic-core installation may have issues"
    
    # Install other requirements
    pip install -r setup/requirements.txt --no-binary pydantic,pydantic-core || echo "Some packages may have issues"
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
echo "To run tests:"
echo "  python cli.py test-runner auto"