#!/usr/bin/env python3
"""
Migration: Add task_type column to tasks table
Description: Adds task_type column to support management tasks that don't get auto-assigned to AI agents
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.database import get_database_url

def run_migration():
    """Add task_type column to tasks table with default value 'regular'"""
    database_url = get_database_url()
    
    # Extract database path from SQLite URL
    if not database_url.startswith("sqlite"):
        print("❌ Migration only supports SQLite databases")
        return
    
    db_path = database_url.replace("sqlite:///", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(task)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'task_type' not in columns:
            print("Adding task_type column to tasks table...")
            
            # Add the column with default value
            cursor.execute('''
                ALTER TABLE task 
                ADD COLUMN task_type TEXT DEFAULT 'regular' 
                CHECK (task_type IN ('regular', 'waiting', 'management'))
            ''')
            
            # Update any existing tasks to have the default value
            cursor.execute("UPDATE task SET task_type = 'regular' WHERE task_type IS NULL")
            
            conn.commit()
            print("✅ Successfully added task_type column to tasks table")
        else:
            print("✅ task_type column already exists, skipping migration")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()