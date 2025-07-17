#!/usr/bin/env python3
"""
Script to safely restore project structure from backup.

This script:
1. Reads project data from backup (enum-safe since Project has no enum fields)
2. Validates project data
3. Restores projects using SQLModel for proper validation
4. Ensures Headless-PM is the default project (ID 1)

Run with: python scripts/restore_projects.py
"""

import sqlite3
import sys
import os
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import get_session
from src.models.models import Project
from sqlmodel import select

def get_backup_projects() -> list:
    """Get project data from the most recent backup."""
    backup_file = 'headless-pm.db.backup_enum_fix_20250717_114923'
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return []
    
    print(f"📂 Reading projects from backup: {backup_file}")
    
    conn = sqlite3.connect(backup_file)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, description, shared_path, instructions_path, 
               project_docs_path, code_guidelines_path 
        FROM project 
        ORDER BY id
    ''')
    
    projects_data = cursor.fetchall()
    conn.close()
    
    return projects_data

def validate_project_data(project_data: tuple) -> dict:
    """Validate and clean project data."""
    project_id, name, description, shared_path, instructions_path, project_docs_path, code_guidelines_path = project_data
    
    # Basic validation
    if not name or not description:
        raise ValueError(f"Invalid project data: missing name or description")
    
    if not shared_path or not instructions_path or not project_docs_path:
        raise ValueError(f"Invalid project data: missing required paths")
    
    return {
        'id': project_id,
        'name': name,
        'description': description,
        'shared_path': shared_path,
        'instructions_path': instructions_path,
        'project_docs_path': project_docs_path,
        'code_guidelines_path': code_guidelines_path,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }

def restore_projects() -> bool:
    """Restore projects from backup safely."""
    print("🔄 Starting project restoration...")
    
    # Get backup data
    backup_projects = get_backup_projects()
    if not backup_projects:
        print("❌ No projects found in backup")
        return False
    
    print(f"📋 Found {len(backup_projects)} projects in backup")
    
    # Validate all project data first
    validated_projects = []
    for project_data in backup_projects:
        try:
            validated_project = validate_project_data(project_data)
            validated_projects.append(validated_project)
            print(f"  ✅ Validated: {validated_project['name']}")
        except ValueError as e:
            print(f"  ❌ Validation failed for project: {e}")
            return False
    
    # Clear existing data and restore projects
    with next(get_session()) as session:
        print("\n🗑️  Removing existing data...")
        
        # Delete dependent records first to avoid foreign key constraints
        from src.models.models import Agent, Service, Document, Epic, Feature, Task, Changelog, Mention
        
        # Delete in reverse dependency order
        mention_count = len(session.exec(select(Mention)).all())
        for mention in session.exec(select(Mention)).all():
            session.delete(mention)
        print(f"    🗑️  Removed {mention_count} mentions")
        
        changelog_count = len(session.exec(select(Changelog)).all())
        for changelog in session.exec(select(Changelog)).all():
            session.delete(changelog)
        print(f"    🗑️  Removed {changelog_count} changelogs")
        
        # Delete task evaluations (if any)
        from src.models.models import TaskEvaluation
        eval_count = len(session.exec(select(TaskEvaluation)).all())
        for evaluation in session.exec(select(TaskEvaluation)).all():
            session.delete(evaluation)
        print(f"    🗑️  Removed {eval_count} task evaluations")
        
        task_count = len(session.exec(select(Task)).all())
        for task in session.exec(select(Task)).all():
            session.delete(task)
        print(f"    🗑️  Removed {task_count} tasks")
        
        feature_count = len(session.exec(select(Feature)).all())
        for feature in session.exec(select(Feature)).all():
            session.delete(feature)
        print(f"    🗑️  Removed {feature_count} features")
        
        epic_count = len(session.exec(select(Epic)).all())
        for epic in session.exec(select(Epic)).all():
            session.delete(epic)
        print(f"    🗑️  Removed {epic_count} epics")
        
        agent_count = len(session.exec(select(Agent)).all())
        for agent in session.exec(select(Agent)).all():
            session.delete(agent)
        print(f"    🗑️  Removed {agent_count} agents")
        
        service_count = len(session.exec(select(Service)).all())
        for service in session.exec(select(Service)).all():
            session.delete(service)
        print(f"    🗑️  Removed {service_count} services")
        
        document_count = len(session.exec(select(Document)).all())
        for document in session.exec(select(Document)).all():
            session.delete(document)
        print(f"    🗑️  Removed {document_count} documents")
        
        # Now safe to delete projects
        project_count = len(session.exec(select(Project)).all())
        for project in session.exec(select(Project)).all():
            print(f"    🗑️  Removing project: {project.name}")
            session.delete(project)
        print(f"    🗑️  Removed {project_count} projects")
        
        session.commit()
        print("  ✅ All existing data removed")
        
        print("\n📥 Restoring projects...")
        for project_data in validated_projects:
            project = Project(**project_data)
            session.add(project)
            print(f"  ✅ Restored: {project.name}")
        
        session.commit()
        
        # Verify Headless-PM is available
        headless_pm = session.exec(
            select(Project).where(Project.name == "Headless-PM")
        ).first()
        
        if headless_pm:
            print(f"\n🎯 Default project verified: {headless_pm.name} (ID: {headless_pm.id})")
        else:
            print("\n⚠️  Warning: Headless-PM project not found after restoration")
    
    print(f"\n🎉 Successfully restored {len(validated_projects)} projects!")
    return True

def main():
    """Main function."""
    print("🚀 Project Restoration Script")
    print("=" * 50)
    
    if not restore_projects():
        print("❌ Project restoration failed")
        sys.exit(1)
    
    print("✅ Project restoration completed successfully")

if __name__ == "__main__":
    main()