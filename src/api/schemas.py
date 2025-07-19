from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from src.models.enums import TaskStatus, AgentRole, DifficultyLevel, TaskComplexity, ConnectionType, TaskType, AgentStatus
from src.models.document_enums import DocumentType, ServiceStatus

if TYPE_CHECKING:
    from typing import ForwardRef

# Request schemas
class ProjectCreateRequest(BaseModel):
    name: str = Field(..., description="Unique project name")
    description: str = Field(..., description="Project description")
    shared_path: str = Field(..., description="Path to shared files directory")
    instructions_path: str = Field(..., description="Path to agent instructions")
    project_docs_path: str = Field(..., description="Path to project documentation")
    code_guidelines_path: Optional[str] = Field(None, description="Path to code guidelines")

class ProjectUpdateRequest(BaseModel):
    description: Optional[str] = Field(None, description="Updated project description")
    shared_path: Optional[str] = Field(None, description="Updated shared files path")
    instructions_path: Optional[str] = Field(None, description="Updated instructions path")
    project_docs_path: Optional[str] = Field(None, description="Updated documentation path")
    code_guidelines_path: Optional[str] = Field(None, description="Updated code guidelines path")

class AgentRegisterRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier (e.g., 'frontend_dev_senior_001')")
    project_id: int = Field(..., description="Project ID to register agent for")
    role: AgentRole = Field(..., description="Agent's role in the project")
    level: DifficultyLevel = Field(..., description="Agent's skill level")
    connection_type: Optional[ConnectionType] = Field(ConnectionType.CLIENT, description="Connection type (MCP or Client)")
    
    @validator('role')
    def validate_role(cls, v):
        if isinstance(v, str):
            # Handle legacy 'pm' role
            if v.lower() == 'pm':
                return AgentRole.PROJECT_PM
            # Normalize case
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

class EpicCreateRequest(BaseModel):
    name: str = Field(..., description="Epic name")
    description: str = Field(..., description="Epic description")

class FeatureCreateRequest(BaseModel):
    epic_id: int = Field(..., description="ID of the epic this feature belongs to")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")

class TaskCreateRequest(BaseModel):
    feature_id: int = Field(..., description="ID of the feature this task belongs to")
    title: str = Field(..., description="Brief task title")
    description: str = Field(..., description="Detailed task description")
    target_role: AgentRole = Field(..., description="Role that should handle this task")
    difficulty: DifficultyLevel = Field(..., description="Task difficulty level")
    complexity: TaskComplexity = Field(TaskComplexity.MAJOR, description="Task complexity (minor = commit to main, major = requires PR)")
    task_type: TaskType = Field(TaskType.REGULAR, description="Task type (regular = development task, management = planning/analysis)")
    branch: str = Field(..., description="Git branch for this task")
    
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

class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus = Field(..., description="New status for the task")
    notes: Optional[str] = Field(None, description="Optional notes about the status change")
    
    @validator('status')
    def validate_status(cls, v):
        if isinstance(v, str):
            # Handle legacy status values
            if v.lower() in ['evaluation', 'approved']:
                return TaskStatus.QA_DONE if v.lower() == 'evaluation' else TaskStatus.COMMITTED
            try:
                return TaskStatus(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task status: {v}. Valid statuses: {[s.value for s in TaskStatus]}")
        return v

class TaskCommentRequest(BaseModel):
    comment: str = Field(..., description="Comment to add to the task")

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Updated task title")
    description: Optional[str] = Field(None, description="Updated task description")
    target_role: Optional[AgentRole] = Field(None, description="Updated target role")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Updated difficulty level")
    complexity: Optional[TaskComplexity] = Field(None, description="Updated task complexity")
    
    @validator('target_role')
    def validate_target_role(cls, v):
        if v is not None and isinstance(v, str):
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
        if v is not None and isinstance(v, str):
            try:
                return DifficultyLevel(v.lower())
            except ValueError:
                raise ValueError(f"Invalid difficulty level: {v}. Valid levels: {[l.value for l in DifficultyLevel]}")
        return v
    
    @validator('complexity')
    def validate_complexity(cls, v):
        if v is not None and isinstance(v, str):
            try:
                return TaskComplexity(v.lower())
            except ValueError:
                raise ValueError(f"Invalid task complexity: {v}. Valid complexities: {[c.value for c in TaskComplexity]}")
        return v

# Response schemas
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    shared_path: str
    instructions_path: str
    project_docs_path: str
    code_guidelines_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    agent_count: Optional[int] = 0
    epic_count: Optional[int] = 0
    task_count: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

class AgentResponse(BaseModel):
    id: int
    agent_id: str
    project_id: int
    project_name: Optional[str] = None
    role: AgentRole
    level: DifficultyLevel
    connection_type: Optional[ConnectionType]
    last_seen: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AgentRegistrationResponse(BaseModel):
    agent: AgentResponse
    next_task: Optional["TaskResponse"] = None
    mentions: List["MentionResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)

class AgentAvailabilityResponse(BaseModel):
    agent_id: str
    project_id: int
    is_available: bool
    current_task_id: Optional[int] = None
    current_task_title: Optional[str] = None
    last_activity: datetime
    status: AgentStatus
    
    model_config = ConfigDict(from_attributes=True)

class ProjectContextResponse(BaseModel):
    project_id: int
    project_name: str
    shared_path: str
    instructions_path: str
    project_docs_path: str
    code_guidelines_path: Optional[str] = None
    database_type: str

class TaskResponse(BaseModel):
    id: int
    feature_id: int
    title: str
    description: str
    created_by: str  # agent_id
    target_role: AgentRole
    difficulty: DifficultyLevel
    complexity: TaskComplexity
    branch: str
    status: TaskStatus
    locked_by: Optional[str] = None  # agent_id
    locked_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    task_type: Optional[TaskType] = TaskType.REGULAR
    poll_interval: Optional[int] = None  # seconds for waiting tasks
    
    model_config = ConfigDict(from_attributes=True)

class TaskStatusUpdateResponse(BaseModel):
    task: TaskResponse
    next_task: Optional[TaskResponse] = None
    workflow_status: str = Field(..., description="continue | waiting | no_tasks")
    task_completed: Optional[int] = Field(None, description="ID of completed task")
    auto_continue: bool = Field(True, description="Whether to automatically continue to next task")
    continuation_prompt: str = Field("Continue with the next task without waiting for confirmation", 
                                   description="Instruction for autonomous continuation")
    session_momentum: str = Field("high", description="high | medium | low - indicates work pace")
    
    model_config = ConfigDict(from_attributes=True)

class EpicResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    task_count: int = 0
    completed_task_count: int = 0
    in_progress_task_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class FeatureResponse(BaseModel):
    id: int
    epic_id: int
    name: str
    description: str
    
    model_config = ConfigDict(from_attributes=True)

class ChangelogResponse(BaseModel):
    id: int
    task_id: int
    old_status: TaskStatus
    new_status: TaskStatus
    changed_by: str
    notes: Optional[str] = None
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    detail: str

# Document schemas
class DocumentCreateRequest(BaseModel):
    doc_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., description="Document title", max_length=200)
    content: str = Field(..., description="Document content (Markdown supported)")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional meta_data")
    expires_at: Optional[datetime] = Field(None, description="Auto-cleanup expiration time")
    
    @validator('doc_type')
    def validate_doc_type(cls, v):
        if isinstance(v, str):
            try:
                return DocumentType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid document type: {v}. Valid types: {[t.value for t in DocumentType]}")
        return v

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Updated title", max_length=200)
    content: Optional[str] = Field(None, description="Updated content")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Updated meta_data")

class DocumentResponse(BaseModel):
    id: int
    doc_type: DocumentType
    author_id: str
    title: str
    content: str
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    mentions: List[str] = []  # List of mentioned agent_ids
    
    model_config = ConfigDict(from_attributes=True)

# Service schemas
class ServiceRegisterRequest(BaseModel):
    service_name: str = Field(..., description="Unique service name", max_length=100)
    ping_url: str = Field(..., description="URL to ping for health check (e.g., http://localhost:8080/health)")
    port: Optional[int] = Field(None, description="Port number if applicable")
    status: ServiceStatus = Field("up", description="Service status")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional service meta_data")

class ServiceResponse(BaseModel):
    id: int
    service_name: str
    owner_agent_id: str
    ping_url: str
    port: Optional[int] = None
    status: ServiceStatus
    last_heartbeat: Optional[datetime] = None
    last_ping_at: Optional[datetime] = None
    last_ping_success: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = None
    updated_at: datetime

class ProjectDocCreateRequest(BaseModel):
    content: str = Field(..., description="File content")
    
    model_config = ConfigDict(from_attributes=True)

# Mention schemas
class MentionResponse(BaseModel):
    id: int
    document_id: Optional[int] = None
    task_id: Optional[int] = None
    mentioned_agent_id: str
    created_by: str
    is_read: bool
    created_at: datetime
    document_title: Optional[str] = None
    task_title: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Rebuild models to resolve forward references
AgentRegistrationResponse.model_rebuild()