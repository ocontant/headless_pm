# Setup Directory

This directory contains all installation and setup scripts for the AI Engine project.

## Files

### install.sh
Main installation script that:
- Creates virtual environment
- Installs all dependencies
- Sets up .env file template
- Configures the CLI

**Usage from project root:**
```bash
bash setup/install.sh
```

### setup_dev_env.sh
Development environment setup that:
- Detects architecture (ARM64 vs x86_64)
- Installs appropriate dependencies
- Tests architecture compatibility
- Provides development guidance

**Usage from project root:**
```bash
bash setup/setup_dev_env.sh
```

### universal_setup.sh
Universal setup that works for both architectures:
- Automatically chooses correct venv (venv for ARM64, claude_venv for x86_64)
- Installs dependencies appropriately for each architecture
- Provides unified setup experience

**Usage from project root:**
```bash
bash setup/universal_setup.sh
```

### create_claude_venv.sh
Creates a separate virtual environment for Claude Code (x86_64):
- Installs packages from source (no binaries)
- Handles architecture compatibility issues
- Used when running in Claude Code environment

**Usage from project root:**
```bash
bash setup/create_claude_venv.sh
```

### setup.py & pyproject.toml
Python package configuration files:
- Define package metadata
- Specify dependencies
- Configure package installation

## Running Setup Scripts

All setup scripts should be run from the **project root directory**, not from within the setup/ directory:

```bash
# Correct - from project root
bash setup/install.sh

# Incorrect - from within setup/
cd setup
bash install.sh  # This won't work correctly
```

The scripts automatically handle directory changes internally.

## Environment Variables

After setup, create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GOOGLE_API_KEY=your_key
OPEN_ROUTER_API_KEY=your_key

# Database configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_engine
DB_TEST_NAME=ai_engine_test
```

## Architecture Compatibility

The project supports both ARM64 (Apple Silicon) and x86_64 architectures:

- **ARM64**: Uses standard `venv` with normal pip installations
- **x86_64**: May use `claude_venv` with source installations for compatibility

The setup scripts automatically detect and handle architecture differences.