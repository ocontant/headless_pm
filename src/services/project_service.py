from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime

from src.models.models import Project, Agent, Epic, Task, Document, Service
from src.api.schemas import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
from fastapi import HTTPException


def create_project(request: ProjectCreateRequest, db: Session) -> Project:
    """Create a new project"""
    # Check if project name already exists
    existing = db.exec(select(Project).where(Project.name == request.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Project with name '{request.name}' already exists")
    
    project = Project(
        name=request.name,
        description=request.description,
        shared_path=request.shared_path,
        instructions_path=request.instructions_path,
        project_docs_path=request.project_docs_path,
        code_guidelines_path=request.code_guidelines_path
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


def list_projects(db: Session) -> List[ProjectResponse]:
    """List all projects with statistics"""
    projects = db.exec(select(Project)).all()
    
    project_responses = []
    for project in projects:
        # Get counts for each project
        agent_count = db.exec(
            select(func.count(Agent.id)).where(Agent.project_id == project.id)
        ).one()
        
        epic_count = db.exec(
            select(func.count(Epic.id)).where(Epic.project_id == project.id)
        ).one()
        
        # Count tasks through features and epics
        task_count = db.exec(
            select(func.count(Task.id))
            .join(Task.feature)
            .join(Epic)
            .where(Epic.project_id == project.id)
        ).one()
        
        project_response = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            shared_path=project.shared_path,
            instructions_path=project.instructions_path,
            project_docs_path=project.project_docs_path,
            created_at=project.created_at,
            updated_at=project.updated_at,
            agent_count=agent_count,
            epic_count=epic_count,
            task_count=task_count
        )
        project_responses.append(project_response)
    
    return project_responses


def list_all_projects(db: Session) -> List[dict]:
    """List all projects (simplified for MCP)"""
    projects = db.exec(select(Project)).all()
    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat() if project.created_at else None
        }
        for project in projects
    ]


def get_project(project_id: int, db: Session) -> Project:
    """Get a specific project by ID"""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id {project_id} not found")
    return project


def update_project(project_id: int, request: ProjectUpdateRequest, db: Session) -> Project:
    """Update a project"""
    project = get_project(project_id, db)
    
    if request.description is not None:
        project.description = request.description
    if request.shared_path is not None:
        project.shared_path = request.shared_path
    if request.instructions_path is not None:
        project.instructions_path = request.instructions_path
    if request.project_docs_path is not None:
        project.project_docs_path = request.project_docs_path
    if request.code_guidelines_path is not None:
        project.code_guidelines_path = request.code_guidelines_path
    
    project.updated_at = datetime.utcnow()
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


def delete_project(project_id: int, db: Session, force: bool = False) -> dict:
    """Delete a project and all associated data"""
    project = get_project(project_id, db)
    
    # Get counts for reporting
    agent_count = db.exec(
        select(func.count(Agent.id)).where(Agent.project_id == project_id)
    ).one()
    
    epic_count = db.exec(
        select(func.count(Epic.id)).where(Epic.project_id == project_id)
    ).one()
    
    doc_count = db.exec(
        select(func.count(Document.id)).where(Document.project_id == project_id)
    ).one()
    
    service_count = db.exec(
        select(func.count(Service.id)).where(Service.project_id == project_id)
    ).one()
    
    # Count tasks through features and epics
    from src.models.models import Feature
    task_count = db.exec(
        select(func.count(Task.id))
        .join(Feature)
        .join(Epic)
        .where(Epic.project_id == project_id)
    ).one() or 0
    
    # Check if there are any entities in the project (unless force delete)
    total_entities = agent_count + epic_count + task_count + doc_count + service_count
    
    if not force and total_entities > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete project with {total_entities} entities. Use force=true to delete anyway or remove entities first."
        )
    
    # Delete project (cascade should handle dependencies)
    db.delete(project)
    db.commit()
    
    return {
        "message": f"Project '{project.name}' deleted successfully",
        "deleted_entities": {
            "agents": agent_count,
            "epics": epic_count,
            "tasks": task_count,
            "documents": doc_count,
            "services": service_count
        }
    }