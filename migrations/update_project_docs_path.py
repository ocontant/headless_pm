#!/usr/bin/env python3
"""
Migration to update existing projects to use the new project-specific documentation structure.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from src.models.database import engine
from src.models.models import Project

def update_project_docs_paths():
    """Update existing projects to use project-specific documentation paths."""
    
    with Session(engine) as session:
        # Get all projects
        projects = session.exec(select(Project)).all()
        
        print(f"Updating {len(projects)} projects to use new documentation structure...")
        
        for project in projects:
            # Create project-specific directories
            project_dir = f"./projects/{project.id}"
            docs_dir = f"{project_dir}/docs"
            shared_dir = f"{project_dir}/shared"
            instructions_dir = f"{project_dir}/instructions"
            
            # Create directories if they don't exist
            os.makedirs(docs_dir, exist_ok=True)
            os.makedirs(shared_dir, exist_ok=True)
            os.makedirs(instructions_dir, exist_ok=True)
            
            # Update the project paths
            old_project_docs_path = project.project_docs_path
            old_shared_path = project.shared_path
            old_instructions_path = project.instructions_path
            
            project.project_docs_path = docs_dir
            project.shared_path = shared_dir
            project.instructions_path = instructions_dir
            
            session.add(project)
            
            print(f"✅ Updated Project {project.id} ({project.name}):")
            print(f"   docs: {old_project_docs_path} → {docs_dir}")
            print(f"   shared: {old_shared_path} → {shared_dir}")
            print(f"   instructions: {old_instructions_path} → {instructions_dir}")
        
        session.commit()
        print(f"\n✅ Successfully updated {len(projects)} projects")

if __name__ == "__main__":
    update_project_docs_paths()