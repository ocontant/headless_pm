#!/usr/bin/env python3
"""
Migration script to add missing columns to the agent table.
This script adds:
1. status column (AgentStatus enum) with default 'idle'
2. current_task_id column (optional foreign key to task.id)
3. last_activity column (datetime with default utcnow)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


def run_migration():
    """Run the migration to add missing agent columns"""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        try:
            print("Starting migration to add missing agent columns...")
            
            # Check current table structure
            result = session.execute(text("PRAGMA table_info(agent)"))
            columns = [row[1] for row in result]
            print(f"Current agent table columns: {columns}")
            
            # 1. Add status column if missing
            if "status" not in columns:
                print("Adding status column...")
                session.execute(text("""
                    ALTER TABLE agent 
                    ADD COLUMN status VARCHAR(8) DEFAULT 'idle' NOT NULL
                """))
                print("  Added status column")
            else:
                print("  status column already exists")
            
            # 2. Add current_task_id column if missing
            if "current_task_id" not in columns:
                print("Adding current_task_id column...")
                session.execute(text("""
                    ALTER TABLE agent 
                    ADD COLUMN current_task_id INTEGER REFERENCES task(id)
                """))
                print("  Added current_task_id column")
            else:
                print("  current_task_id column already exists")
            
            # 3. Add last_activity column if missing
            if "last_activity" not in columns:
                print("Adding last_activity column...")
                # SQLite doesn't allow NOT NULL with non-constant default in ALTER TABLE
                # So we add it as nullable first, then update and make it NOT NULL
                session.execute(text("""
                    ALTER TABLE agent 
                    ADD COLUMN last_activity DATETIME
                """))
                
                # Update all rows to have a default value
                session.execute(text("""
                    UPDATE agent 
                    SET last_activity = CURRENT_TIMESTAMP
                """))
                
                print("  Added last_activity column")
            else:
                print("  last_activity column already exists")
            
            # 4. Update existing rows to have proper default values
            print("Updating existing rows with default values...")
            
            # Set status to 'idle' for any NULL values
            session.execute(text("""
                UPDATE agent 
                SET status = 'idle' 
                WHERE status IS NULL
            """))
            
            # Set last_activity to current time for any NULL values
            session.execute(text("""
                UPDATE agent 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE last_activity IS NULL
            """))
            
            print("  Updated existing rows")
            
            # 5. Create index on status column for performance
            print("Creating index on status column...")
            try:
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_agent_status 
                    ON agent(status)
                """))
                print("  Created index on status column")
            except Exception as e:
                print(f"  Warning: Could not create index: {e}")
            
            # Commit all changes
            session.commit()
            print("Migration completed successfully!")
            
            # Verify the changes
            result = session.execute(text("PRAGMA table_info(agent)"))
            columns = [row[1] for row in result]
            print(f"Final agent table columns: {columns}")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    run_migration()