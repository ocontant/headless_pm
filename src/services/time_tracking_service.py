"""
Time tracking service for dashboard user functionality.
"""

from sqlmodel import Session, select
from typing import List
from datetime import datetime

from src.models.models import TimeEntry, Task, Feature, Epic
from src.api.schemas import TimeEntryCreateRequest, TimeEntryResponse, TaskTimeTrackingResponse
from src.api.dependencies import HTTPException
from src.services.agent_service import get_agent_by_id, can_edit_task_fields
from src.utils.time_parser import parse_time_to_minutes, format_minutes_to_human, validate_time_entry


def add_time_entry(task_id: int, request: TimeEntryCreateRequest, agent_id: str, db: Session) -> TimeEntryResponse:
    """
    Add a time entry to a task. Only dashboard-user can perform this action.
    
    Args:
        task_id: ID of the task to add time to
        request: Time entry creation request
        agent_id: ID of the agent making the request (must be dashboard-user)
        db: Database session
        
    Returns:
        The created time entry
        
    Raises:
        HTTPException: If unauthorized, task not found, or validation fails
    """
    # Get task first to find project
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the feature to find the project ID
    feature = db.get(Feature, task.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    epic = db.get(Epic, feature.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    # Get agent and verify privileges (only dashboard-user can add time)
    agent = get_agent_by_id(agent_id, epic.project_id, db)
    if not can_edit_task_fields(agent.agent_id, agent.role):
        raise HTTPException(
            status_code=403, 
            detail="Only dashboard user can add time entries"
        )
    
    # Parse time input
    try:
        minutes = parse_time_to_minutes(request.time_input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Validate time entry
    is_valid, error_message = validate_time_entry(minutes, request.description)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Create time entry
    time_entry = TimeEntry(
        task_id=task_id,
        minutes=minutes,
        description=request.description,
        created_by=agent_id
    )
    
    db.add(time_entry)
    db.commit()
    db.refresh(time_entry)
    
    return TimeEntryResponse(
        id=time_entry.id,
        task_id=time_entry.task_id,
        minutes=time_entry.minutes,
        description=time_entry.description,
        created_by=time_entry.created_by,
        created_at=time_entry.created_at
    )


def get_task_time_tracking(task_id: int, agent_id: str, db: Session) -> TaskTimeTrackingResponse:
    """
    Get time tracking information for a task. Only dashboard-user can access this.
    
    Args:
        task_id: ID of the task
        agent_id: ID of the agent making the request (must be dashboard-user)
        db: Database session
        
    Returns:
        Time tracking information for the task
        
    Raises:
        HTTPException: If unauthorized or task not found
    """
    # Get task first to find project
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the feature to find the project ID
    feature = db.get(Feature, task.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    epic = db.get(Epic, feature.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    # Get agent and verify privileges
    agent = get_agent_by_id(agent_id, epic.project_id, db)
    if not can_edit_task_fields(agent.agent_id, agent.role):
        raise HTTPException(
            status_code=403, 
            detail="Only dashboard user can view time tracking"
        )
    
    # Get all time entries for the task
    time_entries = db.exec(
        select(TimeEntry)
        .where(TimeEntry.task_id == task_id)
        .order_by(TimeEntry.created_at.desc())
    ).all()
    
    # Calculate total time
    total_minutes = sum(entry.minutes for entry in time_entries)
    
    # Convert entries to response format
    entry_responses = [
        TimeEntryResponse(
            id=entry.id,
            task_id=entry.task_id,
            minutes=entry.minutes,
            description=entry.description,
            created_by=entry.created_by,
            created_at=entry.created_at
        )
        for entry in time_entries
    ]
    
    return TaskTimeTrackingResponse(
        total_minutes=total_minutes,
        total_formatted=format_minutes_to_human(total_minutes) if total_minutes != 0 else "0m",
        entries=entry_responses
    )


def delete_time_entry(entry_id: int, agent_id: str, db: Session) -> dict:
    """
    Delete a time entry. Only dashboard-user can perform this action.
    
    Args:
        entry_id: ID of the time entry to delete
        agent_id: ID of the agent making the request (must be dashboard-user)
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If unauthorized or time entry not found
    """
    # Get time entry
    time_entry = db.get(TimeEntry, entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    
    # Get task to find project
    task = db.get(Task, time_entry.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get the feature to find the project ID
    feature = db.get(Feature, task.feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    epic = db.get(Epic, feature.epic_id)
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")

    # Get agent and verify privileges
    agent = get_agent_by_id(agent_id, epic.project_id, db)
    if not can_edit_task_fields(agent.agent_id, agent.role):
        raise HTTPException(
            status_code=403, 
            detail="Only dashboard user can delete time entries"
        )
    
    # Delete the time entry
    db.delete(time_entry)
    db.commit()
    
    return {"message": f"Time entry {entry_id} deleted successfully"}


def get_task_total_time_minutes(task_id: int, db: Session) -> int:
    """
    Get the total time tracked for a task in minutes.
    This is a utility function for including time in task responses.
    
    Args:
        task_id: ID of the task
        db: Database session
        
    Returns:
        Total time in minutes
    """
    time_entries = db.exec(
        select(TimeEntry)
        .where(TimeEntry.task_id == task_id)
    ).all()
    
    return sum(entry.minutes for entry in time_entries)