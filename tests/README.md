# Headless PM Client Test Suite

Comprehensive test suite for the Headless PM Client that tests all API endpoints using real API calls with parallel processing.

## Features

- **No Mocking**: Uses real API calls against the running server
- **Parallel Processing**: Leverages `ThreadPoolExecutor` for concurrent testing
- **Complete Cleanup**: Creates real records and deletes them after testing
- **PM Role Registration**: Tests register as PM agent for full permissions
- **Full Coverage**: Tests all API endpoints including:
  - Agent management (register, list, delete)
  - Project structure (epics, features, tasks)
  - Document system with @mention detection
  - Service registry with heartbeats
  - Changes polling and changelog
  - Complete task lifecycle workflow

## Running the Tests

### Prerequisites

1. Ensure the Headless PM server is running:
   ```bash
   ./start.sh
   ```

2. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Run All Tests

```bash
# Run with API key from environment
API_KEY=your-api-key python tests/test_headless_pm_client.py

# Or if .env file is configured
python tests/test_headless_pm_client.py
```

### Run with pytest

```bash
# Run all tests
pytest tests/test_headless_pm_client.py -v

# Run specific test
pytest tests/test_headless_pm_client.py::TestHeadlessPMClient::test_agent_management -v

# Run with coverage
pytest tests/test_headless_pm_client.py --cov=headless_pm_client --cov-report=term-missing
```

## Test Structure

### Test Classes

- `TestableHeadlessPMClient`: A wrapper that raises exceptions instead of exiting on errors
- `TestHeadlessPMClient`: Main test class with all test methods

### Test Methods

1. **test_agent_management**: Tests agent registration, listing, and deletion
2. **test_project_structure**: Tests epic and feature creation/management
3. **test_task_lifecycle**: Tests complete task workflow with status updates
4. **test_document_system**: Tests document creation with @mention detection
5. **test_service_registry**: Tests service registration and heartbeats
6. **test_changes_and_changelog**: Tests polling for changes
7. **test_context_endpoint**: Tests project context retrieval
8. **test_parallel_stress_test**: Stress tests with many parallel operations

### Cleanup Strategy

The test suite tracks all created resources and cleans them up in reverse dependency order:

1. Services
2. Documents (cascades to mentions)
3. Tasks
4. Features
5. Epics
6. Agents (except PM agent which cannot self-delete)

## Output Example

```
================================================================================
Headless PM Client Test Suite
================================================================================
Test started at: 2025-06-18 08:26:21.739640
API URL: http://localhost:6969
================================================================================
✓ Registered PM agent: test_pm_c6f9f24a

=== Testing Agent Management ===
✓ Registered agent: test_backend_dev_c6f9f24a_bbe85b
✓ Listed 14 agents
✓ Deleted agent: test_backend_dev_c6f9f24a_bbe85b

[... more test output ...]

================================================================================
Test Summary
================================================================================
Tests run: 8
Failures: 0
Errors: 0
Success: True
Test completed at: 2025-06-18 08:26:23.174825
================================================================================
```

## Notes

- Each test run uses a unique test run ID to avoid conflicts
- Tests create real database records - ensure you have a test database
- The PM agent cannot delete itself (this is expected behavior)
- All tests use parallel processing where possible for performance
- Cleanup is automatic but check for orphaned test data if tests fail