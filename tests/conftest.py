"""
Pytest configuration and fixtures for Headless PM tests
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "agents" / "client"))

# Load environment variables before any tests run
def pytest_configure(config):
    """Load environment variables from .env file"""
    from headless_pm_client import load_env_file
    load_env_file()
    
    # Verify API key is loaded
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("No API key found in environment. Please set API_KEY or configure .env file")