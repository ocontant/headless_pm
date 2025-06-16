#!/bin/bash
# Setup script for development environment that works with both ARM64 and x86_64

set -e

echo "==================================="
echo "Development Environment Setup"
echo "==================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine project root (parent of setup directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"
echo "Working from: $(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${GREEN}Installing requirements...${NC}"
pip install -r setup/requirements.txt

# Handle architecture-specific installations
if [[ "$ARCH" == "arm64" ]]; then
    echo -e "${YELLOW}ARM64 architecture detected - Installing standard packages${NC}"
    # Standard installation should work fine on ARM64
    pip install pydantic-ai
elif [[ "$ARCH" == "x86_64" ]]; then
    echo -e "${YELLOW}x86_64 architecture detected - Checking for compatibility issues${NC}"
    # Try to install, but don't fail if there are issues
    pip install pydantic-ai || {
        echo -e "${YELLOW}PydanticAI installation failed - Mock mode will be used${NC}"
        echo -e "${YELLOW}This is expected on x86_64 environments like Claude Code${NC}"
    }
fi

# Test the setup
echo -e "\n${GREEN}Testing architecture compatibility...${NC}"
python -c "
import sys
sys.path.insert(0, 'src')
from helpers.pydantic_ai_wrapper import get_architecture_info, is_mock_mode

info = get_architecture_info()
print(f\"Architecture: {info['cpu_arch']}\")
print(f\"PydanticAI Available: {info['pydantic_ai_available']}\")
print(f\"Mock Mode: {is_mock_mode()}\")
"

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\nTo run tests:"
echo -e "  ${YELLOW}python cli.py test-runner auto${NC}              # Run automatic tests"
echo -e "  ${YELLOW}python run_tests.py --separate${NC}    # Run old tests separately (avoids conflicts)"
echo -e "  ${YELLOW}python cli.py test simple${NC}         # Run simple test"
echo -e "\nTo use the CLI:"
echo -e "  ${YELLOW}python cli.py --help${NC}"
echo -e "  ${YELLOW}python cli.py interactive${NC}"