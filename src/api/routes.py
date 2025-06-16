from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import os

from src.models.database import get_session
from src.api.dependencies import get_db
from src.models.models import Agent, Task, Epic, Feature, Changelog
from src.models.enums import TaskStatus, AgentRole, DifficultyLevel
from src.api.schemas import (
    AgentRegisterRequest, AgentResponse,
    EpicCreateRequest, FeatureCreateRequest,
    TaskCreateRequest, TaskResponse, TaskStatusUpdateRequest,
    TaskCommentRequest,
    ProjectContextResponse, EpicResponse, FeatureResponse,
    ChangelogResponse
)
from src.api.dependencies import verify_api_key
from src.services.mention_service import create_mentions_for_task

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

@router.post("/register", response_model=AgentResponse, 
    summary="Register an agent",
    description="Register a new agent or update existing agent's last seen timestamp")
def register_agent(request: AgentRegisterRequest, db: Session = Depends(get_session)):
    # Check if agent exists
    agent = db.exec(select(Agent).where(Agent.agent_id == request.agent_id)).first()
    
    if agent:
        # Update last seen
        agent.last_seen = datetime.utcnow()
    else:
        # Create new agent
        agent = Agent(
            agent_id=request.agent_id,
            role=request.role,
            level=request.level
        )
        db.add(agent)
    
    db.commit()
    db.refresh(agent)
    return agent

@router.get("/agents", response_model=List[AgentResponse],
    summary="List all agents", 
    description="Get a list of all registered agents")
def list_agents(db: Session = Depends(get_session)):
    agents = db.exec(select(Agent).order_by(Agent.last_seen.desc())).all()
    return agents

@router.get("/context", response_model=ProjectContextResponse,
    summary="Get project context",
    description="Get project configuration and paths for documentation")
def get_context():
    return ProjectContextResponse(
        project_name=os.getenv("PROJECT_NAME", "Headless PM"),
        shared_path=os.getenv("SHARED_PATH", "./shared"),
        instructions_path=os.getenv("INSTRUCTIONS_PATH", "./agent_instructions"),
        project_docs_path=os.getenv("PROJECT_DOCS_PATH", "./docs"),
        database_type="sqlite" if os.getenv("DATABASE_URL", "").startswith("sqlite") else "mysql"
    )

@router.post("/epics", response_model=EpicResponse,
    summary="Create a new epic",
    description="PMs and architects can create epics")
def create_epic(request: EpicCreateRequest, agent_id: str, db: Session = Depends(get_session)):
    # Verify agent is PM or architect
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation.")
    
    if agent.role not in [AgentRole.PM, AgentRole.ARCHITECT]:
        raise HTTPException(status_code=403, detail="Only PMs and architects can create epics")
    
    # Create epic
    epic = Epic(
        name=request.name,
        description=request.description
    )
    db.add(epic)
    db.commit()
    db.refresh(epic)
    
    return EpicResponse(
        id=epic.id,
        name=epic.name,
        description=epic.description,
        created_at=epic.created_at,
        task_count=0,
        completed_count=0
    )

@router.post("/features", response_model=FeatureResponse,
    summary="Create a new feature",
    description="PMs and architects can create features within epics")
def create_feature(request: FeatureCreateRequest, agent_id: str, db: Session = Depends(get_session)):
    # Verify agent is PM or architect
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation.")
    
    if agent.role not in [AgentRole.PM, AgentRole.ARCHITECT]:
        raise HTTPException(status_code=403, detail="Only PMs and architects can create features")
    
    # Verify epic exists
    epic = db.get(Epic, request.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    # Create feature
    feature = Feature(
        epic_id=request.epic_id,
        name=request.name,
        description=request.description
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)
    
    return feature

@router.post("/tasks/create", response_model=TaskResponse,
    summary="Create a new task",
    description="Any agent can create a task for any role")
def create_task(request: TaskCreateRequest, agent_id: str, db: Session = Depends(get_session)):
    # Find creator agent
    creator = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator agent not found")
    
    # Verify feature exists
    feature = db.get(Feature, request.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    # Create task
    task = Task(
        feature_id=request.feature_id,
        title=request.title,
        description=request.description,
        created_by_id=creator.id,
        target_role=request.target_role,
        difficulty=request.difficulty,
        complexity=request.complexity,
        branch=request.branch
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Create initial changelog
    changelog = Changelog(
        task_id=task.id,
        old_status=TaskStatus.CREATED,
        new_status=TaskStatus.CREATED,
        changed_by=creator.agent_id,
        notes="Task created"
    )
    db.add(changelog)
    db.commit()
    
    return TaskResponse(
        id=task.id,
        feature_id=task.feature_id,
        title=task.title,
        description=task.description,
        created_by=task.creator.agent_id,
        target_role=task.target_role,
        difficulty=task.difficulty,
        complexity=task.complexity,
        branch=task.branch,
        status=task.status,
        locked_by=task.locked_by_agent.agent_id if task.locked_by_agent else None,
        locked_at=task.locked_at,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.get("/tasks/next", response_model=Optional[TaskResponse],
    summary="Get next available task",
    description="Get the next task based on agent's role and skill level. Both 'role' and 'level' query parameters are required.")
def get_next_task(role: AgentRole = None, level: DifficultyLevel = None, 
                  db: Session = Depends(get_session)):
    # Validate required parameters
    if role is None:
        raise HTTPException(
            status_code=400, 
            detail="Missing required parameter 'role'. Please provide a valid role (e.g., ?role=frontend_dev)"
        )
    if level is None:
        raise HTTPException(
            status_code=400, 
            detail="Missing required parameter 'level'. Please provide a valid level (e.g., ?level=senior)"
        )
    
    # Determine which statuses to look for based on role
    if role in [AgentRole.ARCHITECT, AgentRole.PM]:
        # Architects and PMs evaluate created tasks
        query = select(Task).where(
            Task.status == TaskStatus.CREATED,
            Task.locked_by_id.is_(None)
        )
    elif role == AgentRole.QA:
        # QA tests dev_done tasks
        query = select(Task).where(
            Task.status == TaskStatus.DEV_DONE,
            Task.locked_by_id.is_(None)
        )
    else:
        # Developers work on approved tasks
        # Get tasks at or below their skill level
        difficulty_order = {
            DifficultyLevel.JUNIOR: [DifficultyLevel.JUNIOR],
            DifficultyLevel.SENIOR: [DifficultyLevel.JUNIOR, DifficultyLevel.SENIOR],
            DifficultyLevel.PRINCIPAL: [DifficultyLevel.JUNIOR, DifficultyLevel.SENIOR, DifficultyLevel.PRINCIPAL]
        }
        allowed_difficulties = difficulty_order.get(level, [level])
        
        query = select(Task).where(
            Task.status == TaskStatus.APPROVED,
            Task.target_role == role,
            Task.difficulty.in_(allowed_difficulties),
            Task.locked_by_id.is_(None)
        )
    
    # Get oldest unlocked task
    task = db.exec(query.order_by(Task.created_at)).first()
    
    if not task:
        return None
    
    return TaskResponse(
        id=task.id,
        feature_id=task.feature_id,
        title=task.title,
        description=task.description,
        created_by=task.creator.agent_id,
        target_role=task.target_role,
        difficulty=task.difficulty,
        complexity=task.complexity,
        branch=task.branch,
        status=task.status,
        locked_by=None,
        locked_at=None,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.post("/tasks/{task_id}/lock", response_model=TaskResponse,
    summary="Lock a task",
    description="Lock a task to prevent other agents from working on it")
def lock_task(task_id: int, agent_id: str, db: Session = Depends(get_session)):
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found. Please verify the task ID exists.")
    
    # Check if already locked
    if task.locked_by_id:
        raise HTTPException(status_code=409, detail=f"Task {task_id} is already locked by another agent. The task must be unlocked before you can lock it.")
    
    # Get agent
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation.")
    
    # Lock the task
    task.locked_by_id = agent.id
    task.locked_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        feature_id=task.feature_id,
        title=task.title,
        description=task.description,
        created_by=task.creator.agent_id,
        target_role=task.target_role,
        difficulty=task.difficulty,
        complexity=task.complexity,
        branch=task.branch,
        status=task.status,
        locked_by=agent.agent_id,
        locked_at=task.locked_at,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.put("/tasks/{task_id}/status", response_model=TaskResponse,
    summary="Update task status",
    description="Update task status and automatically release lock when moving from UNDER_WORK")
def update_task_status(task_id: int, request: TaskStatusUpdateRequest, 
                      agent_id: str, db: Session = Depends(get_session)):
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found. Please verify the task ID exists.")
    
    # Get agent
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation.")
    
    # Store old status
    old_status = task.status
    
    # Update status
    task.status = request.status
    task.updated_at = datetime.utcnow()
    
    # Add notes if provided
    if request.notes:
        task.notes = request.notes
    
    # Release lock if moving from UNDER_WORK
    if old_status == TaskStatus.UNDER_WORK and request.status != TaskStatus.UNDER_WORK:
        task.locked_by_id = None
        task.locked_at = None
    
    db.add(task)
    
    # Create changelog
    changelog = Changelog(
        task_id=task.id,
        old_status=old_status,
        new_status=request.status,
        changed_by=agent_id,
        notes=request.notes
    )
    db.add(changelog)
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        feature_id=task.feature_id,
        title=task.title,
        description=task.description,
        created_by=task.creator.agent_id,
        target_role=task.target_role,
        difficulty=task.difficulty,
        complexity=task.complexity,
        branch=task.branch,
        status=task.status,
        locked_by=task.locked_by_agent.agent_id if task.locked_by_agent else None,
        locked_at=task.locked_at,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.post("/tasks/{task_id}/comment",
    summary="Add comment to task",
    description="Add a comment during evaluation phase with @mention detection")
def add_comment(task_id: int, request: TaskCommentRequest,
               agent_id: str, db: Session = Depends(get_db)):
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found. Please verify the task ID exists.")
    
    # Add comment to notes
    if task.notes:
        task.notes = f"{task.notes}\n\n{agent_id}: {request.comment}"
    else:
        task.notes = f"{agent_id}: {request.comment}"
    
    # Extract and create mentions from the comment
    create_mentions_for_task(db, task_id, request.comment, agent_id)
    
    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    
    return {"message": "Comment added successfully"}

@router.get("/epics", response_model=List[EpicResponse],
    summary="List all epics",
    description="Get all epics with task progress information")
def list_epics(db: Session = Depends(get_session)):
    epics = db.exec(select(Epic)).all()
    
    epic_responses = []
    for epic in epics:
        # Count tasks for this epic
        task_count = 0
        completed_count = 0
        
        for feature in epic.features:
            tasks = db.exec(select(Task).where(Task.feature_id == feature.id)).all()
            task_count += len(tasks)
            completed_count += len([t for t in tasks if t.status == TaskStatus.COMMITTED])
        
        epic_response = EpicResponse(
            id=epic.id,
            name=epic.name,
            description=epic.description,
            created_at=epic.created_at,
            task_count=task_count,
            completed_count=completed_count
        )
        epic_responses.append(epic_response)
    
    return epic_responses

@router.get("/features/{epic_id}", response_model=List[FeatureResponse],
    summary="List features for an epic",
    description="Get all features belonging to a specific epic")
def list_features(epic_id: int, db: Session = Depends(get_session)):
    features = db.exec(select(Feature).where(Feature.epic_id == epic_id)).all()
    return features

@router.get("/changelog", response_model=List[ChangelogResponse],
    summary="Get recent changes",
    description="Get recent task status changes across the project")
def get_changelog(limit: int = 50, db: Session = Depends(get_session)):
    changelogs = db.exec(
        select(Changelog)
        .order_by(Changelog.changed_at.desc())
        .limit(limit)
    ).all()
    return changelogs