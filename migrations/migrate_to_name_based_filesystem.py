#!/usr/bin/env python3
"""
Migration to rename project directories from ID-based to name-based structure.
"""

import os
import sys
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from src.models.database import engine
from src.models.models import Project
from src.services.project_utils import sanitize_project_name, ensure_project_directories, get_project_docs_path, get_project_shared_path, get_project_instructions_path

def migrate_project_directories():
    """Migrate existing project directories from ID-based to name-based structure."""
    
    with Session(engine) as session:
        # Get all projects
        projects = session.exec(select(Project)).all()
        
        print(f"Migrating {len(projects)} projects to name-based filesystem structure...")
        
        for project in projects:
            old_project_dir = f"./projects/{project.id}"
            sanitized_name = sanitize_project_name(project.name)
            new_project_dir = f"./projects/{sanitized_name}"
            
            print(f"\n📁 Migrating Project {project.id} ({project.name}):")
            print(f"   {old_project_dir} → {new_project_dir}")
            
            # Check if old directory exists
            if os.path.exists(old_project_dir):
                # Create new directory structure
                ensure_project_directories(project.name)
                
                # Migrate docs directory
                old_docs = f"{old_project_dir}/docs"
                new_docs = get_project_docs_path(project.name)
                if os.path.exists(old_docs) and old_docs != new_docs:
                    print(f"   📄 Moving docs: {old_docs} → {new_docs}")
                    if os.path.exists(new_docs):
                        # Merge directories
                        for item in os.listdir(old_docs):
                            src = os.path.join(old_docs, item)
                            dst = os.path.join(new_docs, item)
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                                print(f"      📄 Copied: {item}")
                            elif os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                                print(f"      📁 Copied dir: {item}")
                    else:
                        shutil.move(old_docs, new_docs)
                        print(f"      📄 Moved entire docs directory")
                
                # Migrate shared directory
                old_shared = f"{old_project_dir}/shared"
                new_shared = get_project_shared_path(project.name)
                if os.path.exists(old_shared) and old_shared != new_shared:
                    print(f"   📁 Moving shared: {old_shared} → {new_shared}")
                    if os.path.exists(new_shared):
                        # Merge directories
                        for item in os.listdir(old_shared):
                            src = os.path.join(old_shared, item)
                            dst = os.path.join(new_shared, item)
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                                print(f"      📄 Copied: {item}")
                            elif os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                                print(f"      📁 Copied dir: {item}")
                    else:
                        shutil.move(old_shared, new_shared)
                        print(f"      📁 Moved entire shared directory")
                
                # Migrate instructions directory
                old_instructions = f"{old_project_dir}/instructions"
                new_instructions = get_project_instructions_path(project.name)
                if os.path.exists(old_instructions) and old_instructions != new_instructions:
                    print(f"   📋 Moving instructions: {old_instructions} → {new_instructions}")
                    if os.path.exists(new_instructions):
                        # Merge directories
                        for item in os.listdir(old_instructions):
                            src = os.path.join(old_instructions, item)
                            dst = os.path.join(new_instructions, item)
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                                print(f"      📄 Copied: {item}")
                            elif os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                                print(f"      📁 Copied dir: {item}")
                    else:
                        shutil.move(old_instructions, new_instructions)
                        print(f"      📋 Moved entire instructions directory")
                
                # Remove old project directory if it's empty or different from new one
                if old_project_dir != new_project_dir:
                    try:
                        if os.path.exists(old_project_dir):
                            # Check if directory is empty
                            if not os.listdir(old_project_dir):
                                os.rmdir(old_project_dir)
                                print(f"   🗑️  Removed empty old directory: {old_project_dir}")
                            else:
                                print(f"   ⚠️  Old directory not empty, keeping: {old_project_dir}")
                    except OSError as e:
                        print(f"   ⚠️  Could not remove old directory: {e}")
                
                # Update database paths
                project.project_docs_path = get_project_docs_path(project.name)
                project.shared_path = get_project_shared_path(project.name)
                project.instructions_path = get_project_instructions_path(project.name)
                session.add(project)
                
                print(f"   ✅ Updated database paths for {project.name}")
            else:
                # Old directory doesn't exist, just ensure new structure and update DB
                ensure_project_directories(project.name)
                project.project_docs_path = get_project_docs_path(project.name)
                project.shared_path = get_project_shared_path(project.name)
                project.instructions_path = get_project_instructions_path(project.name)
                session.add(project)
                print(f"   ✅ Created new structure for {project.name} (old directory not found)")
        
        session.commit()
        print(f"\n✅ Successfully migrated {len(projects)} projects to name-based filesystem structure")

if __name__ == "__main__":
    migrate_project_directories()