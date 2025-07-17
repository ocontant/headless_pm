from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from src.models.database import get_session
from src.api.schemas import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
from src.api.dependencies import verify_api_key
from src.services.project_service import (
    create_project, list_projects, get_project, update_project, delete_project
)

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