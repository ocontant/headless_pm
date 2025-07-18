# Headless PM CLI Tools

Command-line interface tools for Headless PM database initialization, management, and utilities.

## Overview

The CLI tools provide command-line access to Headless PM core functionality:
- Database initialization and seeding
- System health checks and diagnostics
- Dashboard utilities
- Administrative operations

## Architecture

```
cli/
├── src/
│   ├── main.py          # Main CLI command interface
│   ├── dashboard.py     # Dashboard utilities
│   └── sanity_check.py  # Health checks and diagnostics
└── README.md           # This file
```

## Dependencies

The CLI tools depend on shared components:
- `shared/models/` - Database models and enums
- `shared/services/` - Business logic services

## Commands

### Database Management
```bash
# Initialize database schema
python -m cli.src.main init

# Seed database with sample data
python -m cli.src.main seed

# Run health checks
python -m cli.src.main sanity-check
```

### Dashboard Utilities
```bash
# Dashboard-specific operations
python -m cli.src.dashboard [command]
```

## Environment Setup

The CLI tools require:
- Python 3.11+
- Virtual environment activated
- Database access
- Proper PYTHONPATH configuration

```bash
# Set Python path
export PYTHONPATH=/app

# Set database URL
export DATABASE_URL=sqlite:///app/database/headless-pm.db
```

## Database Initialization

The `init` command:
1. Creates database tables from SQLModel schemas
2. Sets up foreign key relationships
3. Creates indexes for performance
4. Initializes default project
5. Creates dashboard-user agent

```bash
python -m cli.src.main init
```

## Database Seeding

The `seed` command adds sample data:
- Test projects with Epic/Feature/Task hierarchy
- Sample agents with different roles
- Example documents and communications
- Service registry entries

```bash
python -m cli.src.main seed
```

## Health Checks

The `sanity-check` command validates:
- Database connectivity
- Table schema integrity
- Data consistency
- Foreign key relationships
- Index performance

```bash
python -m cli.src.main sanity-check
```

## Usage in Containers

While CLI tools can run in containers, they're typically used during setup:

```bash
# Initialize database in API container
docker-compose exec api python -m cli.src.main init

# Run health checks
docker-compose exec api python -m cli.src.main sanity-check
```

## Development

For development, run CLI tools directly:

```bash
# From project root with venv activated
PYTHONPATH=/app python -m cli.src.main init
```

## Configuration

CLI tools use environment variables:
- `DATABASE_URL` - Database connection string
- `PYTHONPATH` - Python module path
- Project-specific settings from `.env`

## Error Handling

CLI tools provide detailed error messages:
- Database connection issues
- Schema validation errors
- Data integrity problems
- Permission errors

## Logging

CLI operations are logged to:
- Console output (info/error messages)
- Database logs (for data operations)
- System logs (for diagnostics)

## Integration

CLI tools are integrated into:
- Docker container startup sequences
- CI/CD pipeline steps
- Development workflows
- Administrative scripts

## Database Migrations

While separate migration scripts exist in `migrations/`, CLI tools handle:
- Initial schema creation
- Data validation after migrations
- Consistency checks
- Performance optimization

## Backup and Restore

CLI tools support database operations:
```bash
# Create backup before operations
cp database/headless-pm.db database/backup.db

# Restore if needed
cp database/backup.db database/headless-pm.db
```

## Testing

Test CLI operations:
```bash
# Test database initialization
python -m pytest tests/test_cli.py -v

# Test with temporary database
DATABASE_URL=sqlite:///tmp/test.db python -m cli.src.main init
```

## Security

CLI tools implement:
- Safe database operations
- Input validation
- Error handling without data exposure
- Proper permission checking

## Troubleshooting

### Database Issues
- Check DATABASE_URL environment variable
- Verify database file permissions
- Ensure SQLite/MySQL is accessible

### Import Errors
- Verify PYTHONPATH is set correctly
- Check shared module availability
- Ensure virtual environment is activated

### Permission Errors
- Check file system permissions
- Verify database directory is writable
- Ensure proper user context