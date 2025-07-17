#!/usr/bin/env python3
"""
Migration runner script that executes all migrations in order.
This script runs all migration files in the migrations directory.
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

def run_all_migrations():
    """Run all migration scripts in order"""
    migrations_dir = Path(__file__).parent
    
    # List of migrations in order they should be run
    migration_files = [
        "add_project_support.py",
        "migrate_to_text_columns.py", 
        "migrate_connection_type.py",
        "migrate_service_ping.py",
        "add_agent_status_column.py"
    ]
    
    print("Running all migrations...")
    
    for migration_file in migration_files:
        migration_path = migrations_dir / migration_file
        
        if not migration_path.exists():
            print(f"⚠️  Migration file not found: {migration_file}")
            continue
            
        print(f"\n" + "="*60)
        print(f"Running migration: {migration_file}")
        print("="*60)
        
        try:
            # Import and run the migration
            spec = importlib.util.spec_from_file_location("migration", migration_path)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            
            # Call the run_migration function
            migration.run_migration()
            print(f"✅ Migration {migration_file} completed successfully")
            
        except Exception as e:
            print(f"❌ Migration {migration_file} failed: {e}")
            # Continue with other migrations instead of stopping
            continue
    
    print(f"\n" + "="*60)
    print("All migrations completed!")
    print("="*60)

if __name__ == "__main__":
    run_all_migrations()