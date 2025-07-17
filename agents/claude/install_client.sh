#!/bin/bash
# Install Headless PM MCP client for Claude Code
# Drop this file and headless-pm-mcp-bridge.py in your project root

echo "Installing Headless PM MCP client..."
echo "=================================="

# Get the directory of this script (where it was dropped)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BRIDGE_SCRIPT="$SCRIPT_DIR/headless-pm-mcp-bridge.py"

# Check if bridge script exists
if [ ! -f "$BRIDGE_SCRIPT" ]; then
    echo "Error: headless-pm-mcp-bridge.py not found in $SCRIPT_DIR"
    echo "Make sure both files are in the same directory"
    exit 1
fi

# Make bridge executable
chmod +x "$BRIDGE_SCRIPT"

# Default values
SERVER_URL="${HEADLESS_PM_URL:-http://localhost:6969}"
API_KEY="${API_KEY:-}"
SERVER_NAME="${MCP_SERVER_NAME:-headlesspm}"

echo "Server URL: $SERVER_URL"
echo "Bridge script: $BRIDGE_SCRIPT"
if [ -n "$API_KEY" ]; then
    echo "API Key: [Set]"
else
    echo "API Key: [Not set - may be required]"
fi

# Remove existing server if present
echo ""
echo "Removing any existing configuration..."
claude mcp remove $SERVER_NAME 2>/dev/null || true

# Find Python executable with full path
if command -v python3 &> /dev/null; then
    PYTHON_CMD=$(which python3)
elif command -v python &> /dev/null; then
    PYTHON_CMD=$(which python)
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"

# Add stdio server with environment variables
echo "Adding MCP server..."
if [ -n "$API_KEY" ]; then
    claude mcp add $SERVER_NAME -e HEADLESS_PM_URL="$SERVER_URL" -e API_KEY="$API_KEY" -- "$PYTHON_CMD" "$BRIDGE_SCRIPT"
else
    claude mcp add $SERVER_NAME -e HEADLESS_PM_URL="$SERVER_URL" -- "$PYTHON_CMD" "$BRIDGE_SCRIPT"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "IMPORTANT: This MCP server is now permanently installed in Claude Code!"
echo "  - You do NOT need to run this installer again"
echo "  - You do NOT need to run any Python scripts"
echo "  - The MCP bridge runs automatically when Claude Code starts"
echo ""
echo "Usage in Claude Code:"
echo "  - Just use natural language like:"
echo "    'I need to register as a backend developer'"
echo "    'Show me the next available task'"
echo "    'Create a task for the frontend team'"
echo ""
echo "To connect to a different server:"
echo "  export HEADLESS_PM_URL=http://your-server:6969"
echo "  export API_KEY=your-api-key  # if required"
echo "  ./install_client.sh"
echo ""
echo "To verify:"
echo "  claude mcp list"
echo ""
echo "To test:"
echo "  claude 'Please register me as a backend developer named test_agent'"