from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from sqlalchemy import Text, UniqueConstraint, Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import validator, root_validator
from .enums import TaskStatus, AgentRole, DifficultyLevel, TaskComplexity, ConnectionType, AgentStatus, TaskType
from .document_enums import DocumentType, ServiceStatus

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = Field(sa_column=Column(Text))
    shared_path: str
    instructions_path: str
    project_docs_path: str
    code_guidelines_path: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    agents: List["Agent"] = Relationship(back_populates="project")
    epics: List["Epic"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    documents: List["Document"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    services: List["Service"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: str = Field(index=True)  # e.g., "frontend_dev_senior_001"
    project_id: int = Field(foreign_key="project.id", index=True)
    role: AgentRole = Field(sa_column=Column(Enum(AgentRole, values_callable=lambda x: [e.value for e in x])))
    level: DifficultyLevel = Field(sa_column=Column(Enum(DifficultyLevel, values_callable=lambda x: [e.value for e in x])))
    connection_type: Optional[ConnectionType] = Field(default=ConnectionType.CLIENT, sa_column=Column(Enum(ConnectionType, values_callable=lambda x: [e.value for e in x])))
    status: AgentStatus = Field(default=AgentStatus.IDLE, sa_column=Column(Enum(AgentStatus, values_callable=lambda x: [e.value for e in x]), index=True))
    current_task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('role')
    def validate_role(cls, v):
        if isinstance(v, str):
            # Handle legacy 'pm' role
            if v.lower() == 'pm':
                return AgentRole.PROJECT_PM
            # Ensure proper case
            try:
                return AgentRole(v.lower())
            except ValueError:
                raise ValueError(f"Invalid agent role: {v}. Valid roles: {[r.value for r in AgentRole]}")
        return v
    
    @validator('level')
    def validate_level(cls, v):
        if isinstance(v, str):
            try:
                return DifficultyLevel(v.lower())
            except ValueError:
                raise ValueError(f"Invalid difficulty level: {v}. Valid levels: {[l.value for l in DifficultyLevel]}")
        return v
    
    @validator('connection_type')
    def validate_connection_type(cls, v):
        if isinstance(v, str):
            try:
                return ConnectionType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid connection type: {v}. Valid types: {[c.value for c in ConnectionType]}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if isinstance(v, str):
            # Handle mixed case status values
            try:
                return AgentStatus(v.lower())
            except ValueError:
                raise ValueError(f"Invalid agent status: {v}. Valid statuses: {[s.value for s in AgentStatus]}")
        return v
    
    project: Project = Relationship(back_populates="agents")
    current_task: Optional["Task"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Agent.current_task_id]"})
    tasks_created: List["Task"] = Relationship(back_populates="creator", sa_relationship_kwargs={"foreign_keys": "[Task.created_by_id]"})
    tasks_locked: List["Task"] = Relationship(back_populates="locked_by_agent", sa_relationship_kwargs={"foreign_keys": "[Task.locked_by_id]"})
    
    __table_args__ = (
        UniqueConstraint("agent_id", "project_id", name="uq_agent_project"),
    )

class Epic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    name: str
    description: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    project: Project = Relationship(back_populates="epics")
    features: List["Feature"] = Relationship(back_populates="epic", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Feature(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    epic_id: int = Field(foreign_key="epic.id")
    name: str
    description: str = Field(sa_column=Column(Text))
    
    epic: Epic = Relationship(back_populates="features")
    tasks: List["Task"] = Relationship(back_populates="feature", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    feature_id: int = Field(foreign_key="feature.id")
    title: str
    description: str = Field(sa_column=Column(Text))
    created_by_id: int = Field(foreign_key="agent.id")
    target_role: AgentRole = Field(sa_column=Column(Enum(AgentRole, values_callable=lambda x: [e.value for e in x])))
    difficulty: DifficultyLevel = Field(sa_column=Column(Enum(DifficultyLevel, values_callable=lambda x: [e.value for e in x])))
    complexity: TaskComplexity = Field(default=TaskComplexity.MAJOR, sa_column=Column(Enum(TaskComplexity, values_callable=lambda x: [e.value for e in x])))
    task_type: TaskType = Field(default=TaskType.REGULAR, sa_column=Column(Enum(TaskType, values_callable=lambda x: [e.value for e in x])))
    branch: str
    status: TaskStatus = Field(default=TaskStatus.CREATED, sa_column=Column(Enum(TaskStatus, values_callable=lambda x: [e.value for e in x])))
    locked_by_id: Optional[int] = Field(default=None, foreign_key="agent.id")
    locked_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('target_role')
    def validate_target_role(cls, v):
        if isinstance(v, str):
            # Handle legacy 'pm' role
            if v.lower() == 'pm':
                return AgentRole.PROJECT_PM
            try:
                return AgentRole(v.lower())
            except ValueError:
                raise ValueError(f"Invalid target role: {v}. Valid roles: {[r.value for r in AgentRole]}")
        return v
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        if isinstance(v, str):
            try:
                return DifficultyLevel(v.lower())
            except ValueError:
                raise ValueError(f"Invalid difficulty level: {v}. Valid levels: {[l.value for l in DifficultyLevel]}")
        return v
    
    @validator('complexity')
    def validate_complexity(cls, v):
        if isinstance(v, str):
            try:
                return TaskComplexity(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task complexity: {v}. Valid complexities: {[c.value for c in TaskComplexity]}")
        return v
    
    @validator('task_type')
    def validate_task_type(cls, v):
        if isinstance(v, str):
            try:
                return TaskType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task type: {v}. Valid types: {[t.value for t in TaskType]}")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if isinstance(v, str):
            # Handle legacy status values
            if v.lower() in ['evaluation', 'approved']:
                # Map legacy values to current ones
                return TaskStatus.QA_DONE if v.lower() == 'evaluation' else TaskStatus.COMMITTED
            try:
                return TaskStatus(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task status: {v}. Valid statuses: {[s.value for s in TaskStatus]}")
        return v
    
    feature: Feature = Relationship(back_populates="tasks")
    creator: Agent = Relationship(back_populates="tasks_created", sa_relationship_kwargs={"foreign_keys": "[Task.created_by_id]"})
    locked_by_agent: Optional[Agent] = Relationship(back_populates="tasks_locked", sa_relationship_kwargs={"foreign_keys": "[Task.locked_by_id]"})
    evaluations: List["TaskEvaluation"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    changelogs: List["Changelog"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    mentions: List["Mention"] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class TaskEvaluation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    evaluated_by: str  # agent_id
    approved: bool
    comment: Optional[str] = Field(default=None, sa_column=Column(Text))
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    task: Task = Relationship(back_populates="evaluations")

class Changelog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    old_status: TaskStatus = Field(sa_column=Column(Enum(TaskStatus, values_callable=lambda x: [e.value for e in x])))
    new_status: TaskStatus = Field(sa_column=Column(Enum(TaskStatus, values_callable=lambda x: [e.value for e in x])))
    changed_by: str  # agent_id
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('old_status', 'new_status')
    def validate_task_status(cls, v):
        if isinstance(v, str):
            # Handle legacy status values
            if v.lower() in ['evaluation', 'approved']:
                return TaskStatus.QA_DONE if v.lower() == 'evaluation' else TaskStatus.COMMITTED
            try:
                return TaskStatus(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task status: {v}. Valid statuses: {[s.value for s in TaskStatus]}")
        return v
    
    task: Task = Relationship(back_populates="changelogs")

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    doc_type: DocumentType = Field(sa_column=Column(Enum(DocumentType, values_callable=lambda x: [e.value for e in x]), index=True))
    author_id: str = Field(index=True)  # agent_id
    title: str = Field(max_length=200)
    content: str = Field(sa_column=Column(Text))  # Markdown supported
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None  # For auto-cleanup
    
    @validator('doc_type')
    def validate_doc_type(cls, v):
        if isinstance(v, str):
            try:
                return DocumentType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid document type: {v}. Valid types: {[t.value for t in DocumentType]}")
        return v
    
    project: Project = Relationship(back_populates="documents")
    mentions: List["Mention"] = Relationship(back_populates="document", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    service_name: str = Field(index=True, max_length=100)
    owner_agent_id: str  # agent_id
    ping_url: str  # URL to ping for health check
    port: Optional[int] = None
    status: ServiceStatus = Field(default=ServiceStatus.DOWN, sa_column=Column(Enum(ServiceStatus, values_callable=lambda x: [e.value for e in x])))
    last_heartbeat: Optional[datetime] = None
    last_ping_at: Optional[datetime] = None
    last_ping_success: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('status')
    def validate_status(cls, v):
        if isinstance(v, str):
            try:
                return ServiceStatus(v.lower())
            except ValueError:
                raise ValueError(f"Invalid service status: {v}. Valid statuses: {[s.value for s in ServiceStatus]}")
        return v
    
    project: Project = Relationship(back_populates="services")
    
    __table_args__ = (
        UniqueConstraint("service_name", "project_id", name="uq_service_project"),
    )

class Mention(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    document_id: Optional[int] = Field(default=None, foreign_key="document.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    mentioned_agent_id: str = Field(index=True)  # agent_id
    created_by: str  # agent_id
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    document: Optional[Document] = Relationship(back_populates="mentions")
    task: Optional[Task] = Relationship(back_populates="mentions")