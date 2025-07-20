#!/usr/bin/env python3
"""
Migration: Create dashboard-user agents for existing projects
Date: 2025-07-20
Description: Auto-creates dashboard-user agents for any existing projects that don't have them
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from src.models.database import engine
from src.models.models import Project, Agent
from src.models.database import ensure_dashboard_user

def migrate_dashboard_users():
    """Create dashboard-user agents for all existing projects that don't have them."""
    print("🔄 Starting migration: Create dashboard-user agents for existing projects")
    
    with Session(engine) as session:
        # Get all projects
        projects = session.exec(select(Project)).all()
        
        if not projects:
            print("✅ No projects found, nothing to migrate")
            return
        
        print(f"📊 Found {len(projects)} project(s)")
        
        created_count = 0
        
        for project in projects:
            print(f"🔍 Checking project: {project.name} (ID: {project.id})")
            
            # Check if dashboard-user already exists for this project
            existing_dashboard_user = session.exec(
                select(Agent).where(
                    Agent.agent_id == "dashboard-user",
                    Agent.project_id == project.id
                )
            ).first()
            
            if existing_dashboard_user:
                print(f"  ✅ dashboard-user already exists for project {project.name}")
            else:
                print(f"  🔧 Creating dashboard-user for project {project.name}")
                ensure_dashboard_user(project.id, session)
                created_count += 1
        
        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Total projects: {len(projects)}")
        print(f"   - Dashboard users created: {created_count}")
        print(f"   - Already existed: {len(projects) - created_count}")

def verify_migration():
    """Verify that all projects have dashboard-user agents."""
    print("\n🔍 Verifying migration results...")
    
    with Session(engine) as session:
        projects = session.exec(select(Project)).all()
        
        all_good = True
        for project in projects:
            dashboard_user = session.exec(
                select(Agent).where(
                    Agent.agent_id == "dashboard-user",
                    Agent.project_id == project.id
                )
            ).first()
            
            if dashboard_user:
                print(f"  ✅ Project '{project.name}' has dashboard-user (Role: {dashboard_user.role.value})")
            else:
                print(f"  ❌ Project '{project.name}' is missing dashboard-user")
                all_good = False
        
        if all_good:
            print("✅ All projects have dashboard-user agents!")
        else:
            print("❌ Some projects are missing dashboard-user agents")
            return False
        
        return True

if __name__ == "__main__":
    try:
        migrate_dashboard_users()
        if verify_migration():
            print("\n🎉 Migration completed successfully and verified!")
        else:
            print("\n⚠️  Migration completed but verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)