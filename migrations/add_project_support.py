#!/usr/bin/env python3
"""
Migration script to add project support to the database.
This script:
1. Creates the project table (including code_guidelines_path column)
2. Adds code_guidelines_path column if missing from existing project table
3. Creates a default project for existing data
4. Adds project_id columns to all relevant tables
5. Migrates existing data to the default project
6. Updates unique constraints
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, select
from sqlalchemy import text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


def run_migration():
    """Run the migration to add project support"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        try:
            print("Starting migration to add project support...")
            
            # 1. Create project table if it doesn't exist
            print("Creating project table...")
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS project (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    shared_path VARCHAR NOT NULL,
                    instructions_path VARCHAR NOT NULL,
                    project_docs_path VARCHAR NOT NULL,
                    code_guidelines_path VARCHAR,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 2. Check if code_guidelines_path column exists and add if missing
            print("Checking for code_guidelines_path column...")
            result = session.execute(text("PRAGMA table_info(project)"))
            columns = [row[1] for row in result]
            
            if "code_guidelines_path" not in columns:
                print("Adding missing code_guidelines_path column...")
                session.execute(text("""
                    ALTER TABLE project 
                    ADD COLUMN code_guidelines_path VARCHAR
                """))
                print("Added code_guidelines_path column")
            else:
                print("code_guidelines_path column already exists")
            
            # 3. Check if we already have projects
            project_count = session.execute(text("SELECT COUNT(*) FROM project")).scalar()
            
            if project_count == 0:
                # 4. Create default project for existing data
                print("Creating default project for existing data...")
                session.execute(text("""
                    INSERT INTO project (name, description, shared_path, instructions_path, project_docs_path, created_at, updated_at)
                    VALUES (
                        'Default',
                        'Default project for migrated data',
                        :shared_path,
                        :instructions_path,
                        :project_docs_path,
                        :created_at,
                        :updated_at
                    )
                """), {
                    "shared_path": os.getenv("SHARED_PATH", "./shared"),
                    "instructions_path": os.getenv("INSTRUCTIONS_PATH", "./agent_instructions"),
                    "project_docs_path": os.getenv("PROJECT_DOCS_PATH", "./docs"),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
                default_project_id = session.execute(text("SELECT id FROM project WHERE name = 'Default'")).scalar()
                print(f"Created default project with ID: {default_project_id}")
            else:
                default_project_id = 1
                print(f"Using existing project ID: {default_project_id}")
            
            # 5. Add project_id columns to tables (if they don't exist)
            tables_to_update = [
                ("agent", "AFTER connection_type"),
                ("epic", "AFTER id"),
                ("document", "AFTER id"),
                ("service", "AFTER id"),
                ("mention", "AFTER id")
            ]
            
            for table_name, after_column in tables_to_update:
                print(f"Adding project_id to {table_name} table...")
                try:
                    # Check if column already exists
                    result = session.execute(text(f"PRAGMA table_info({table_name})"))
                    columns = [row[1] for row in result]
                    
                    if "project_id" not in columns:
                        # SQLite doesn't support ALTER TABLE ADD COLUMN with AFTER clause
                        # So we just add the column
                        session.execute(text(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN project_id INTEGER 
                            REFERENCES project(id)
                        """))
                        
                        # Set default project_id for existing rows
                        session.execute(text(f"""
                            UPDATE {table_name} 
                            SET project_id = {default_project_id}
                            WHERE project_id IS NULL
                        """))
                        
                        print(f"  Added project_id to {table_name}")
                    else:
                        print(f"  project_id already exists in {table_name}")
                        
                except Exception as e:
                    print(f"  Warning: Could not add project_id to {table_name}: {e}")
            
            # 6. Update unique constraints
            print("Updating unique constraints...")
            
            # For SQLite, we need to recreate tables to modify constraints
            # This is complex, so we'll create indexes instead
            try:
                # Create unique index for agent
                session.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_project 
                    ON agent(agent_id, project_id)
                """))
                
                # Create unique index for service
                session.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_service_project 
                    ON service(service_name, project_id)
                """))
                
                print("  Created unique indexes")
            except Exception as e:
                print(f"  Warning: Could not create indexes: {e}")
            
            # Commit all changes
            session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    run_migration()