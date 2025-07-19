#!/usr/bin/env python3
"""
Migration: Remove deprecated agent roles (pm, global_pm)
Description: Updates any existing agents with deprecated roles to use project_pm instead
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
    """Update deprecated agent roles to project_pm"""
    database_url = get_database_url()
    
    # Extract database path from SQLite URL
    if not database_url.startswith("sqlite"):
        print("❌ Migration only supports SQLite databases")
        return
    
    db_path = database_url.replace("sqlite:///", "")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for agents with deprecated roles
        cursor.execute("SELECT agent_id, role FROM agent WHERE role IN ('pm', 'global_pm')")
        deprecated_agents = cursor.fetchall()
        
        if deprecated_agents:
            print(f"Found {len(deprecated_agents)} agents with deprecated roles:")
            for agent_id, role in deprecated_agents:
                print(f"  {agent_id}: {role}")
            
            # Update deprecated roles to project_pm
            cursor.execute("""
                UPDATE agent 
                SET role = 'project_pm' 
                WHERE role IN ('pm', 'global_pm')
            """)
            
            updated_count = cursor.rowcount
            conn.commit()
            print(f"✅ Successfully updated {updated_count} agents to project_pm role")
        else:
            print("✅ No agents with deprecated roles found, migration not needed")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()