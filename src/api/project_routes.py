from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlmodel import Session
from typing import List
import os
import pathlib

from src.models.database import get_session
from src.api.schemas import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, ProjectDocCreateRequest
from src.api.dependencies import verify_api_key
from src.services.project_service import (
    create_project, list_projects, get_project, update_project, delete_project
)
from src.services.project_utils import get_project_docs_path, sanitize_filename, sanitize_project_name, validate_path_security

router = APIRouter(prefix="/api/v1/projects", dependencies=[Depends(verify_api_key)])


@router.post("", response_model=ProjectResponse,
    summary="Create a new project",
    description="Create a new project with configuration paths")
def create_project_endpoint(request: ProjectCreateRequest, db: Session = Depends(get_session)):
    project = create_project(request, db)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        shared_path=project.shared_path,
        instructions_path=project.instructions_path,
        project_docs_path=project.project_docs_path,
        code_guidelines_path=project.code_guidelines_path,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.get("", response_model=List[ProjectResponse],
    summary="List all projects",
    description="Get a list of all projects with statistics")
def list_projects_endpoint(db: Session = Depends(get_session)):
    return list_projects(db)


@router.get("/{project_id}", response_model=ProjectResponse,
    summary="Get a specific project",
    description="Get details of a specific project by ID")
def get_project_endpoint(project_id: int, db: Session = Depends(get_session)):
    project = get_project(project_id, db)
    # Get statistics
    from sqlmodel import select, func
    from src.models.models import Agent, Epic, Task, Feature
    
    agent_count = db.exec(
        select(func.count(Agent.id)).where(Agent.project_id == project_id)
    ).one()
    
    epic_count = db.exec(
        select(func.count(Epic.id)).where(Epic.project_id == project_id)
    ).one()
    
    # Count tasks through features and epics
    task_count = db.exec(
        select(func.count(Task.id))
        .join(Feature)
        .join(Epic)
        .where(Epic.project_id == project_id)
    ).one()
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        shared_path=project.shared_path,
        instructions_path=project.instructions_path,
        project_docs_path=project.project_docs_path,
        code_guidelines_path=project.code_guidelines_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        agent_count=agent_count,
        epic_count=epic_count,
        task_count=task_count
    )


@router.patch("/{project_id}", response_model=ProjectResponse,
    summary="Update a project",
    description="Update project details")
def update_project_endpoint(
    project_id: int, 
    request: ProjectUpdateRequest, 
    db: Session = Depends(get_session)
):
    project = update_project(project_id, request, db)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        shared_path=project.shared_path,
        instructions_path=project.instructions_path,
        project_docs_path=project.project_docs_path,
        code_guidelines_path=project.code_guidelines_path,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.delete("/{project_id}",
    summary="Delete a project",
    description="Delete a project and all associated data")
def delete_project_endpoint(
    project_id: int, 
    force: bool = False,
    db: Session = Depends(get_session)
):
    return delete_project(project_id, db, force)


@router.get("/{project_id}/docs",
    summary="List project documentation files",
    description="Get a list of documentation files for a specific project")
def list_project_docs(project_id: int, db: Session = Depends(get_session)):
    """List all documentation files in the project's docs directory."""
    # Verify project exists and get project name
    project = get_project(project_id, db)
    
    # Use name-based filesystem path
    docs_path = get_project_docs_path(project.name)
    if not os.path.exists(docs_path):
        return {"files": []}
    
    files = []
    for root, dirs, filenames in os.walk(docs_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, docs_path)
            
            stat = os.stat(file_path)
            files.append({
                "name": filename,
                "path": relative_path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_directory": False
            })
    
    return {"files": files}


@router.get("/{project_id}/docs/{file_path:path}",
    summary="Get project documentation file",
    description="Retrieve a specific documentation file from the project")
def get_project_doc_file(project_id: int, file_path: str, db: Session = Depends(get_session)):
    """Get the contents of a specific documentation file."""
    # Verify project exists and get project name
    project = get_project(project_id, db)
    
    # Enhanced security validation for file path
    try:
        docs_base = get_project_docs_path(project.name)
        validated_path = validate_path_security(file_path, docs_base)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file path: {str(e)}")
    
    if not os.path.exists(validated_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.isdir(validated_path):
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")
    
    # For text files, return content as JSON
    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "path": file_path,
            "content": content,
            "size": os.path.getsize(validated_path),
            "modified": os.path.getmtime(validated_path)
        }
    except UnicodeDecodeError:
        # For binary files, return as file download
        return FileResponse(validated_path, filename=os.path.basename(file_path))
    except (OSError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.post("/{project_id}/docs/{file_path:path}",
    summary="Create or update project documentation file",
    description="Create or update a documentation file in the project")
def create_project_doc_file(
    project_id: int, 
    file_path: str, 
    request: ProjectDocCreateRequest,
    db: Session = Depends(get_session)
):
    """Create or update a documentation file."""
    # Verify project exists and get project name
    project = get_project(project_id, db)
    
    # Enhanced security validation for file path
    try:
        docs_base = get_project_docs_path(project.name)
        
        # First sanitize each component of the path
        path_components = file_path.split('/')
        sanitized_components = []
        
        for component in path_components:
            if component and component not in ['.', '..']:
                if '.' in component and not component.startswith('.'):
                    # This is likely a filename
                    sanitized_component = sanitize_filename(component)
                else:
                    # This is likely a directory name
                    sanitized_component = sanitize_project_name(component)
                sanitized_components.append(sanitized_component)
        
        # Reconstruct the sanitized path
        sanitized_path = '/'.join(sanitized_components)
        
        # Now validate the sanitized path
        final_validated_path = validate_path_security(sanitized_path, docs_base)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file path: {str(e)}")
    
    # Validate content for security (basic checks)
    if '\0' in request.content:
        raise HTTPException(status_code=400, detail="Content contains invalid null bytes")
    
    # Create directory if it doesn't exist
    try:
        os.makedirs(os.path.dirname(final_validated_path), exist_ok=True)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}")
    
    # Write the file with enhanced error handling
    try:
        with open(final_validated_path, 'w', encoding='utf-8') as f:
            f.write(request.content)
    except (OSError, IOError, UnicodeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")
    
    # Return the sanitized path in response
    final_relative_path = os.path.relpath(final_validated_path, docs_base)
    
    return {
        "path": final_relative_path,
        "original_path": file_path,
        "sanitized_path": sanitized_path,
        "size": os.path.getsize(final_validated_path),
        "created": True,
        "message": f"File {final_relative_path} created successfully"
    }