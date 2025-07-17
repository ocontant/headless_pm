from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from src.models.models import Agent, Mention, Document, Task, Project
from src.models.enums import AgentRole, AgentStatus
from src.api.schemas import AgentResponse, MentionResponse, AgentRegisterRequest, AgentAvailabilityResponse
from src.api.dependencies import HTTPException


def register_or_update_agent(request: AgentRegisterRequest, db: Session) -> Agent:
    """
    Register a new agent or update existing agent's last seen timestamp.
    
    Args:
        request: Agent registration request data
        db: Database session
        
    Returns:
        The registered or updated agent
    """
    # Check if agent exists in the specified project
    agent = db.exec(select(Agent).where(
        Agent.agent_id == request.agent_id,
        Agent.project_id == request.project_id
    )).first()
    
    if agent:
        # Update last seen and connection type
        agent.last_seen = datetime.utcnow()
        agent.connection_type = request.connection_type
    else:
        # Create new agent
        agent = Agent(
            agent_id=request.agent_id,
            project_id=request.project_id,
            role=request.role,
            level=request.level,
            connection_type=request.connection_type
        )
        db.add(agent)
    
    db.commit()
    db.refresh(agent)
    
    return agent


def get_unread_mentions(agent_id: str, project_id: int, db: Session, limit: int = 10) -> List[MentionResponse]:
    """
    Get unread mentions for an agent.
    
    Args:
        agent_id: The agent's ID
        db: Database session
        limit: Maximum number of mentions to return
        
    Returns:
        List of mention responses with document/task titles
    """
    mention_query = select(Mention).where(
        Mention.mentioned_agent_id == agent_id,
        Mention.project_id == project_id,
        Mention.is_read == False
    ).order_by(Mention.created_at.desc()).limit(limit)
    mentions_data = db.exec(mention_query).all()
    
    # Build mention responses with document/task titles
    mentions = []
    for mention in mentions_data:
        response = MentionResponse(
            id=mention.id,
            document_id=mention.document_id,
            task_id=mention.task_id,
            mentioned_agent_id=mention.mentioned_agent_id,
            created_by=mention.created_by,
            is_read=mention.is_read,
            created_at=mention.created_at
        )
        
        # Add document title if it's a document mention
        if mention.document_id:
            document = db.get(Document, mention.document_id)
            if document:
                response.document_title = document.title
        
        # Add task title if it's a task mention
        if mention.task_id:
            task_obj = db.get(Task, mention.task_id)
            if task_obj:
                response.task_title = task_obj.title
        
        mentions.append(response)
    
    return mentions


def list_all_agents(db: Session, project_id: Optional[int] = None) -> List[AgentResponse]:
    """
    Get a list of all registered agents with project names ordered by last seen.
    
    Args:
        db: Database session
        project_id: Optional project filter
        
    Returns:
        List of all agents with project information
    """
    query = select(Agent, Project.name).join(Project, Agent.project_id == Project.id)
    if project_id is not None:
        query = query.where(Agent.project_id == project_id)
    
    results = db.exec(query.order_by(Agent.last_seen.desc())).all()
    
    # Convert to AgentResponse objects with project names
    agent_responses = []
    for agent, project_name in results:
        agent_response = AgentResponse(
            id=agent.id,
            agent_id=agent.agent_id,
            project_id=agent.project_id,
            project_name=project_name,
            role=agent.role,
            level=agent.level,
            connection_type=agent.connection_type,
            last_seen=agent.last_seen
        )
        agent_responses.append(agent_response)
    
    return agent_responses


def verify_agent_role(agent_id: str, project_id: int, allowed_roles: List[AgentRole], db: Session) -> Agent:
    """
    Verify that an agent exists and has one of the allowed roles.
    
    Args:
        agent_id: The agent's ID
        allowed_roles: List of allowed roles
        db: Database session
        
    Returns:
        The agent if verified
        
    Raises:
        HTTPException: If agent not found or doesn't have required role
    """
    agent = db.exec(select(Agent).where(
        Agent.agent_id == agent_id,
        Agent.project_id == project_id
    )).first()
    
    if not agent:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_id}' not found. Please ensure the agent is registered using POST /api/v1/register before attempting this operation."
        )
    
    if agent.role not in allowed_roles:
        role_names = [role.value for role in allowed_roles]
        raise HTTPException(
            status_code=403, 
            detail=f"Only {', '.join(role_names)} agents can perform this operation"
        )
    
    return agent


def delete_agent(agent_id: str, requester_agent_id: str, project_id: int, db: Session) -> dict:
    """
    Delete an agent record. Only PM agents can perform this action.
    
    Args:
        agent_id: ID of the agent to delete
        requester_agent_id: ID of the agent making the request
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If unauthorized or validation fails
    """
    # Verify requester is PM
    requester = verify_agent_role(requester_agent_id, project_id, [AgentRole.PM], db)
    
    # Prevent PM from deleting themselves
    if agent_id == requester_agent_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own agent record")
    
    agent = db.exec(select(Agent).where(
        Agent.agent_id == agent_id,
        Agent.project_id == project_id
    )).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    
    return {"message": f"Agent {agent_id} deleted successfully"}


def get_agents_availability(project_id: int, role: Optional[AgentRole], db: Session) -> List[AgentAvailabilityResponse]:
    """
    Get availability status for all agents in a project.
    
    Args:
        project_id: Project ID to filter agents
        role: Optional role filter
        db: Database session
        
    Returns:
        List of agent availability responses
    """
    query = select(Agent).where(Agent.project_id == project_id)
    if role:
        query = query.where(Agent.role == role)
    
    agents = db.exec(query.order_by(Agent.agent_id)).all()
    
    availability_responses = []
    for agent in agents:
        current_task = None
        current_task_title = None
        
        if agent.current_task_id:
            current_task = db.get(Task, agent.current_task_id)
            if current_task:
                current_task_title = current_task.title
        
        # Determine availability - agent is available if status is IDLE
        is_available = agent.status == AgentStatus.IDLE
        
        availability_responses.append(AgentAvailabilityResponse(
            agent_id=agent.agent_id,
            project_id=agent.project_id,
            is_available=is_available,
            current_task_id=agent.current_task_id,
            current_task_title=current_task_title,
            last_activity=agent.last_activity,
            status=agent.status
        ))
    
    return availability_responses


def get_agent_availability(agent_id: str, project_id: int, db: Session) -> AgentAvailabilityResponse:
    """
    Get availability status for a specific agent.
    
    Args:
        agent_id: Agent ID
        project_id: Project ID
        db: Database session
        
    Returns:
        Agent availability response
        
    Raises:
        HTTPException: If agent not found
    """
    agent = db.exec(select(Agent).where(
        Agent.agent_id == agent_id,
        Agent.project_id == project_id
    )).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    current_task = None
    current_task_title = None
    
    if agent.current_task_id:
        current_task = db.get(Task, agent.current_task_id)
        if current_task:
            current_task_title = current_task.title
    
    # Determine availability - agent is available if status is IDLE
    is_available = agent.status == AgentStatus.IDLE
    
    return AgentAvailabilityResponse(
        agent_id=agent.agent_id,
        project_id=agent.project_id,
        is_available=is_available,
        current_task_id=agent.current_task_id,
        current_task_title=current_task_title,
        last_activity=agent.last_activity,
        status=agent.status
    )