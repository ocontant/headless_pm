from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from src.models.models import Agent, Task, Feature, Changelog, Epic
from src.models.enums import TaskStatus, AgentRole, TaskType, AgentStatus
from src.api.schemas import (
    TaskCreateRequest, TaskResponse, TaskStatusUpdateRequest,
    TaskStatusUpdateResponse, TaskCommentRequest, ChangelogResponse
)
from src.api.dependencies import HTTPException
from src.services.mention_service import create_mentions_for_task
from src.services.task_service import get_next_task_for_agent


def create_task(request: TaskCreateRequest, agent_id: str, db: Session) -> TaskResponse:
    """
    Create a new task. Any agent can create a task for any role.
    
    Args:
        request: Task creation request data
        agent_id: ID of the agent creating the task
        db: Database session
        
    Returns:
        The created task
        
    Raises:
        HTTPException: If creator agent or feature not found
    """
    # Find creator agent
    creator = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator agent not found")
    
    # Verify feature exists and get project information
    feature = db.get(Feature, request.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    epic = db.get(Epic, feature.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    # Validate project access based on agent role
    if creator.role == AgentRole.GLOBAL_PM:
        # Global PM can create tasks in any project - no restriction
        pass
    elif creator.role == AgentRole.PROJECT_PM:
        # Project PM can only create tasks in their project
        if epic.project_id != creator.project_id:
            raise HTTPException(
                status_code=403,
                detail="Project PM can only create tasks within their assigned project"
            )
    else:
        # Regular agents can only create tasks in their project
        if epic.project_id != creator.project_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot create tasks in other projects"
            )
    
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


def list_tasks(status: Optional[TaskStatus], role: Optional[AgentRole], db: Session, project_id: Optional[int] = None, limit: Optional[int] = None) -> List[TaskResponse]:
    """
    List all tasks with optional filtering by status, role, and project.
    
    Args:
        status: Optional status filter
        role: Optional role filter
        db: Database session
        project_id: Optional project filter
        limit: Optional limit on number of results
        
    Returns:
        List of task responses
    """
    query = select(Task).order_by(Task.created_at.desc())
    
    if status:
        query = query.where(Task.status == status)
    
    if role:
        query = query.where(Task.target_role == role)
    
    if project_id:
        query = query.where(Task.project_id == project_id)
    
    if limit:
        query = query.limit(limit)
    
    tasks = db.exec(query).all()
    
    # Convert to TaskResponse objects
    return [
        TaskResponse(
            id=task.id,
            feature_id=task.feature_id,
            title=task.title,
            description=task.description,
            created_by=task.creator.agent_id if task.creator else "unknown",
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
        for task in tasks
    ]


def lock_task(task_id: int, agent_id: str, db: Session) -> TaskResponse:
    """
    Lock a task to prevent other agents from working on it.
    
    Args:
        task_id: ID of the task to lock
        agent_id: ID of the agent locking the task
        db: Database session
        
    Returns:
        The locked task
        
    Raises:
        HTTPException: If task not found, already locked, or agent not found
    """
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail=f"Task with ID {task_id} not found. Please verify the task ID exists."
        )
    
    # Check if already locked
    if task.locked_by_id:
        raise HTTPException(
            status_code=409, 
            detail=f"Task {task_id} is already locked by another agent. The task must be unlocked before you can lock it."
        )
    
    # Get agent
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation."
        )
    
    # Validate project access - agent can only lock tasks in their project
    feature = db.get(Feature, task.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    epic = db.get(Epic, feature.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    if epic.project_id != agent.project_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot lock tasks from other projects"
        )
    
    # Check if agent already has a task locked (global constraint)
    existing_locked_task = db.exec(
        select(Task).where(Task.locked_by_id == agent.id)
    ).first()
    
    if existing_locked_task:
        raise HTTPException(
            status_code=409,
            detail=f"Agent already has task {existing_locked_task.id} locked. Complete current task before locking a new one."
        )
    
    # Lock the task and update agent status
    task.locked_by_id = agent.id
    task.locked_at = datetime.utcnow()
    task.status = TaskStatus.UNDER_WORK
    
    # Update agent status to working
    agent.status = AgentStatus.WORKING
    agent.current_task_id = task.id
    agent.last_activity = datetime.utcnow()
    
    db.add(task)
    db.add(agent)
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


def update_task_status(
    task_id: int, 
    request: TaskStatusUpdateRequest, 
    agent_id: str, 
    db: Session
) -> TaskStatusUpdateResponse:
    """
    Update task status, automatically release lock when moving from UNDER_WORK,
    and return next available task.
    
    Args:
        task_id: ID of the task to update
        request: Status update request data
        agent_id: ID of the agent updating the task
        db: Database session
        
    Returns:
        Task status update response with next task
        
    Raises:
        HTTPException: If task or agent not found
    """
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail=f"Task with ID {task_id} not found. Please verify the task ID exists."
        )
    
    # Get agent
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation."
        )
    
    # Store old status
    old_status = task.status
    
    # Update status
    task.status = request.status
    task.updated_at = datetime.utcnow()
    
    # Add notes if provided
    if request.notes:
        task.notes = request.notes
    
    # Release lock if moving from UNDER_WORK and update agent status
    if old_status == TaskStatus.UNDER_WORK and request.status != TaskStatus.UNDER_WORK:
        task.locked_by_id = None
        task.locked_at = None
        
        # Update agent status to idle and clear current task
        agent.status = AgentStatus.IDLE
        agent.current_task_id = None
        agent.last_activity = datetime.utcnow()
        db.add(agent)
    
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
    
    # Create the current task response
    task_response = TaskResponse(
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
        updated_at=task.updated_at,
        task_type=TaskType.REGULAR
    )
    
    # Get next available task for this agent
    next_task = get_next_task_for_agent(agent, db)
    
    # Determine workflow status
    if next_task:
        workflow_status = "continue"
        auto_continue = True
        session_momentum = "high"
    else:
        workflow_status = "no_tasks"
        auto_continue = False
        session_momentum = "low"
    
    return TaskStatusUpdateResponse(
        task=task_response,
        next_task=next_task,
        workflow_status=workflow_status,
        task_completed=task_id,
        auto_continue=auto_continue,
        continuation_prompt="Continue with the next task without waiting for confirmation" if next_task else "No more tasks available",
        session_momentum=session_momentum
    )


def add_task_comment(task_id: int, request: TaskCommentRequest, agent_id: str, db: Session) -> dict:
    """
    Add a comment to a task during evaluation phase with @mention detection.
    
    Args:
        task_id: ID of the task to comment on
        request: Comment request data
        agent_id: ID of the agent adding the comment
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If task not found
    """
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=404, 
            detail=f"Task with ID {task_id} not found. Please verify the task ID exists."
        )
    
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


def delete_task(task_id: int, agent_id: str, db: Session) -> dict:
    """
    Delete a task. Only PM agents can perform this action.
    
    Args:
        task_id: ID of the task to delete
        agent_id: ID of the agent making the request
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If unauthorized or task not found
    """
    from src.services.agent_service import verify_agent_role
    
    # First get the agent to determine their project_id
    agent = db.exec(select(Agent).where(Agent.agent_id == agent_id)).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify agent is PM using their project_id
    verify_agent_role(agent_id, agent.project_id, [AgentRole.PROJECT_PM], db)
    
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": f"Task {task_id} deleted successfully"}


def assign_task_to_agent(
    task_id: int, 
    target_agent_id: str, 
    assigner_agent_id: str, 
    db: Session
) -> TaskResponse:
    """
    Assign a specific task to a specific agent. Only Project PMs can perform this action.
    
    Args:
        task_id: ID of the task to assign
        target_agent_id: ID of the agent to assign the task to
        assigner_agent_id: ID of the PM making the assignment
        db: Database session
        
    Returns:
        The assigned task
        
    Raises:
        HTTPException: If unauthorized, task not found, or validation fails
    """
    # Get assigner agent
    assigner = db.exec(select(Agent).where(Agent.agent_id == assigner_agent_id)).first()
    if not assigner:
        raise HTTPException(status_code=404, detail="Assigner agent not found")
    
    # Verify assigner is Project PM
    if assigner.role != AgentRole.PROJECT_PM:
        raise HTTPException(
            status_code=403,
            detail="Only Project PMs can assign tasks to specific agents. Global PMs cannot assign tasks directly."
        )
    
    # Get target agent
    target_agent = db.exec(select(Agent).where(Agent.agent_id == target_agent_id)).first()
    if not target_agent:
        raise HTTPException(status_code=404, detail="Target agent not found")
    
    # Verify both agents are in the same project
    if assigner.project_id != target_agent.project_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign tasks to agents in other projects"
        )
    
    # Get task
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify task is in the same project
    feature = db.get(Feature, task.feature_id)
    epic = db.get(Epic, feature.epic_id)
    
    if epic.project_id != assigner.project_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign tasks from other projects"
        )
    
    # Check if task is available for assignment
    if task.locked_by_id:
        raise HTTPException(
            status_code=409,
            detail="Task is already locked by another agent"
        )
    
    # Check if target agent is available
    if target_agent.status != AgentStatus.IDLE:
        raise HTTPException(
            status_code=409,
            detail=f"Agent {target_agent_id} is not available (status: {target_agent.status.value})"
        )
    
    # Check if target agent already has a task
    if target_agent.current_task_id:
        raise HTTPException(
            status_code=409,
            detail=f"Agent {target_agent_id} already has an assigned task"
        )
    
    # Assign the task
    task.locked_by_id = target_agent.id
    task.locked_at = datetime.utcnow()
    task.status = TaskStatus.UNDER_WORK
    
    # Update agent status
    target_agent.status = AgentStatus.WORKING
    target_agent.current_task_id = task.id
    target_agent.last_activity = datetime.utcnow()
    
    # Create changelog
    changelog = Changelog(
        task_id=task.id,
        old_status=task.status,
        new_status=TaskStatus.UNDER_WORK,
        changed_by=assigner_agent_id,
        notes=f"Task assigned to {target_agent_id} by Project PM"
    )
    
    db.add(task)
    db.add(target_agent)
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
        locked_by=target_agent.agent_id,
        locked_at=task.locked_at,
        notes=task.notes,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


def get_recent_changelog(limit: int, db: Session) -> List[Changelog]:
    """
    Get recent task status changes across the project.
    
    Args:
        limit: Maximum number of changelog entries to return
        db: Database session
        
    Returns:
        List of changelog entries
    """
    return db.exec(
        select(Changelog)
        .order_by(Changelog.changed_at.desc())
        .limit(limit)
    ).all()