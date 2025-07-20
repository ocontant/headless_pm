#!/usr/bin/env python3
"""
Database migration: Add repository fields to projects

This migration adds repository configuration fields to the Project model:
- repository_url: Git repository URL (required)
- repository_main_branch: Main branch name (default: "main")
- repository_clone_path: Local clone path (optional)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import create_engine, text
from src.models.database import get_database_url

def run_migration():
    """Add repository fields to projects table"""
    print("🔄 Starting repository fields migration...")
    
    # Get database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as connection:
            # Check if migration is needed
            try:
                result = connection.execute(text("SELECT repository_url FROM project LIMIT 1"))
                print("✅ Repository fields already exist, skipping migration")
                return
            except Exception:
                # Column doesn't exist, proceed with migration
                pass
            
            print("📝 Adding repository fields to project table...")
            
            # Add repository_url column (required)
            connection.execute(text("""
                ALTER TABLE project 
                ADD COLUMN repository_url TEXT
            """))
            
            # Add repository_main_branch column with default
            connection.execute(text("""
                ALTER TABLE project 
                ADD COLUMN repository_main_branch TEXT DEFAULT 'main'
            """))
            
            # Add repository_clone_path column (optional)
            connection.execute(text("""
                ALTER TABLE project 
                ADD COLUMN repository_clone_path TEXT
            """))
            
            # Update existing projects with placeholder repository URLs
            # This allows existing projects to continue working while requiring
            # manual update of repository information
            print("🔧 Setting placeholder repository URLs for existing projects...")
            connection.execute(text("""
                UPDATE project 
                SET repository_url = 'https://github.com/placeholder/' || LOWER(REPLACE(name, ' ', '-')) || '.git',
                    repository_main_branch = 'main'
                WHERE repository_url IS NULL
            """))
            
            # Make repository_url NOT NULL after setting placeholders
            connection.execute(text("""
                ALTER TABLE project 
                ALTER COLUMN repository_url SET NOT NULL
            """))
            
            connection.commit()
            print("✅ Repository fields migration completed successfully!")
            print("⚠️  Note: Existing projects have placeholder repository URLs.")
            print("   Please update them with actual repository information.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

def rollback():
    """Remove repository fields from projects table"""
    print("🔄 Rolling back repository fields migration...")
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as connection:
            # Remove the columns
            connection.execute(text("ALTER TABLE project DROP COLUMN repository_url"))
            connection.execute(text("ALTER TABLE project DROP COLUMN repository_main_branch"))
            connection.execute(text("ALTER TABLE project DROP COLUMN repository_clone_path"))
            
            connection.commit()
            print("✅ Repository fields rollback completed!")
            
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Repository fields migration")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    args = parser.parse_args()
    
    if args.rollback:
        rollback()
    else:
        run_migration()