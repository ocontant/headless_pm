# Python Client Agent Instructions for Headless PM

This directory contains role-specific instructions for agents using the Python client integration.

## Overview

The Python client provides a programmatic interface to Headless PM, allowing you to integrate task management directly into your code workflow.

## Getting Started
- **Install client**: copy `headless_pm_client.py` to your project directory
- **Using client**: `python headless_pm_client.py --help`


## Troubleshooting

- **Connection Refused**: Ensure the API server is running on port 6969
- **Task Not Found**: The task may be locked by another agent
- **Registration Failed**: Check that your role is valid
- **Import Errors**: Ensure you're importing from the correct path

