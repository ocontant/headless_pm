import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from src.main import app
from src.models.database import get_session
from src.models.models import Agent, Epic, Feature, Task
from src.models.enums import AgentRole, DifficultyLevel, TaskStatus, TaskComplexity

# Set API_KEY for tests
os.environ["API_KEY"] = "development-key"

@pytest.fixture(name="engine")
def engine_fixture():
    # Import ALL models to ensure they're registered with SQLModel metadata
    from src.models.models import (
        Agent, Epic, Feature, Task, Document, Service, 
        Mention, TaskEvaluation, Changelog
    )
    from src.models.enums import AgentRole, DifficultyLevel, TaskStatus, TaskComplexity
    from src.models.document_enums import DocumentType, ServiceStatus
    
    # Use file-based SQLite for tests to avoid memory DB connection issues
    import tempfile
    import os
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    os.unlink(db_path)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    from src.api.dependencies import verify_api_key
    
    def get_session_override():
        return session
    
    def verify_api_key_override():
        return "development-key"

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_api_key] = verify_api_key_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_api_data(session: Session):
    # Create agents
    architect = Agent(
        agent_id="architect_test_001",
        role=AgentRole.ARCHITECT,
        level=DifficultyLevel.PRINCIPAL
    )
    frontend_dev = Agent(
        agent_id="frontend_dev_test_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    pm_agent = Agent(
        agent_id="pm_test_001",
        role=AgentRole.PM,
        level=DifficultyLevel.PRINCIPAL
    )
    
    session.add_all([architect, frontend_dev, pm_agent])
    session.commit()
    
    # Create epic and feature
    epic = Epic(name="Test Epic", description="Test epic description")
    session.add(epic)
    session.commit()
    
    feature = Feature(
        epic_id=epic.id,
        name="Test Feature",
        description="Test feature description"
    )
    session.add(feature)
    session.commit()
    
    return {
        "agents": {"architect": architect, "frontend_dev": frontend_dev, "pm": pm_agent},
        "pm_agent": pm_agent,
        "epic": epic,
        "feature": feature
    }

def test_register_agent(client: TestClient, engine):
    """Test agent registration"""
    # Force the engine fixture to be used to ensure tables are created
    response = client.post(
        "/api/v1/register",
        headers={"X-API-Key": "development-key"},
        json={
            "agent_id": "test_agent_001",
            "role": "frontend_dev",
            "level": "senior"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "test_agent_001"
    assert data["role"] == "frontend_dev"
    assert data["level"] == "senior"

def test_register_agent_invalid_key(session: Session):
    """Test agent registration with invalid API key"""
    # Create a separate client without auth override to test auth failure
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    # Don't override verify_api_key for this test
    
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/register",
            headers={"X-API-Key": "invalid-key"},
            json={
                "agent_id": "test_agent_001",
                "role": "frontend_dev",
                "level": "senior"
            }
        )
        
        assert response.status_code == 401
    
    app.dependency_overrides.clear()

def test_create_epic(client: TestClient, sample_api_data):
    """Test epic creation by PM"""
    pm_agent = sample_api_data["pm_agent"]
    
    response = client.post(
        "/api/v1/epics",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": pm_agent.agent_id},
        json={
            "name": "Test Epic",
            "description": "Test epic description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Epic"
    assert data["task_count"] == 0
    assert data["completed_count"] == 0

def test_create_feature(client: TestClient, sample_api_data):
    """Test feature creation by PM"""
    pm_agent = sample_api_data["pm_agent"]
    epic = sample_api_data["epic"]
    
    response = client.post(
        "/api/v1/features",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": pm_agent.agent_id},
        json={
            "epic_id": epic.id,
            "name": "Test Feature",
            "description": "Test feature description"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Feature"
    assert data["epic_id"] == epic.id

def test_list_agents(client: TestClient, sample_api_data):
    """Test listing all agents"""
    response = client.get(
        "/api/v1/agents",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # At least the sample agents

def test_get_context(client: TestClient):
    """Test getting project context"""
    response = client.get(
        "/api/v1/context",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "project_name" in data
    assert "shared_path" in data
    assert "instructions_path" in data

def test_create_task(client: TestClient, sample_api_data):
    """Test task creation"""
    feature = sample_api_data["feature"]
    
    response = client.post(
        "/api/v1/tasks/create",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={
            "feature_id": feature.id,
            "title": "Test Task",
            "description": "Test task description",
            "target_role": "frontend_dev",
            "difficulty": "senior",
            "complexity": "major",
            "branch": "feature/test-task"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["target_role"] == "frontend_dev"
    assert data["complexity"] == "major"
    assert data["status"] == "created"

def test_get_next_task(client: TestClient, sample_api_data):
    """Test getting next task for agent"""
    # First create a task
    feature = sample_api_data["feature"]
    
    client.post(
        "/api/v1/tasks/create",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={
            "feature_id": feature.id,
            "title": "Test Task for Architect",
            "description": "Test task description",
            "target_role": "frontend_dev",
            "difficulty": "senior",
            "complexity": "major",
            "branch": "feature/test-task"
        }
    )
    
    # Architect should get this task for evaluation
    response = client.get(
        "/api/v1/tasks/next",
        headers={"X-API-Key": "development-key"},
        params={"role": "architect", "level": "principal"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert data["title"] == "Test Task for Architect"
    assert data["status"] == "created"


def test_lock_task(client: TestClient, sample_api_data):
    """Test task locking"""
    feature = sample_api_data["feature"]
    
    # Create and approve a task
    response = client.post(
        "/api/v1/tasks/create",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={
            "feature_id": feature.id,
            "title": "Task to Lock",
            "description": "Test task description",
            "target_role": "frontend_dev",
            "difficulty": "senior",
            "complexity": "major",
            "branch": "feature/test-lock"
        }
    )
    
    task_data = response.json()
    task_id = task_data["id"]
    
    # Approve the task first
    client.post(
        f"/api/v1/tasks/{task_id}/evaluate",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={"approved": True, "comment": "Approved"}
    )
    
    # Lock the task
    response = client.post(
        f"/api/v1/tasks/{task_id}/lock",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "frontend_dev_test_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["locked_by"] == "frontend_dev_test_001"
    assert data["locked_at"] is not None

def test_update_task_status(client: TestClient, sample_api_data):
    """Test task status update"""
    feature = sample_api_data["feature"]
    
    # Create, approve, and lock a task
    response = client.post(
        "/api/v1/tasks/create",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={
            "feature_id": feature.id,
            "title": "Task to Update",
            "description": "Test task description",
            "target_role": "frontend_dev",
            "difficulty": "senior",
            "complexity": "major",
            "branch": "feature/test-update"
        }
    )
    
    task_data = response.json()
    task_id = task_data["id"]
    
    # Approve and lock
    client.post(
        f"/api/v1/tasks/{task_id}/evaluate",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "architect_test_001"},
        json={"approved": True, "comment": "Approved"}
    )
    
    client.post(
        f"/api/v1/tasks/{task_id}/lock",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "frontend_dev_test_001"}
    )
    
    # Update status
    response = client.put(
        f"/api/v1/tasks/{task_id}/status",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "frontend_dev_test_001"},
        json={
            "status": "under_work",
            "notes": "Starting implementation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "under_work"
    assert data["notes"] == "Starting implementation"

def test_create_document(client: TestClient):
    """Test document creation"""
    response = client.post(
        "/api/v1/documents",
        headers={"X-API-Key": "development-key"},
        params={"author_id": "test_agent_001"},
        json={
            "doc_type": "update",
            "title": "Test Document",
            "content": "This is a test document with @frontend_dev_test_001 mention"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Document"
    assert data["doc_type"] == "update"
    assert "frontend_dev_test_001" in data["mentions"]

def test_list_documents(client: TestClient):
    """Test document listing"""
    # Create a document first
    client.post(
        "/api/v1/documents",
        headers={"X-API-Key": "development-key"},
        params={"author_id": "test_agent_001"},
        json={
            "doc_type": "update",
            "title": "Test Document List",
            "content": "Test content"
        }
    )
    
    # List documents
    response = client.get(
        "/api/v1/documents",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(doc["title"] == "Test Document List" for doc in data)

def test_register_service(client: TestClient):
    """Test service registration"""
    response = client.post(
        "/api/v1/services/register",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "test_agent_001"},
        json={
            "service_name": "test-api",
            "port": 8000,
            "status": "up",
            "meta_data": {"version": "1.0.0"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "test-api"
    assert data["port"] == 8000
    assert data["status"] == "up"

def test_list_services(client: TestClient):
    """Test service listing"""
    # Register a service first
    client.post(
        "/api/v1/services/register",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "test_agent_001"},
        json={
            "service_name": "test-list-api",
            "port": 9000,
            "status": "up"
        }
    )
    
    # List services
    response = client.get(
        "/api/v1/services",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(service["service_name"] == "test-list-api" for service in data)

def test_service_heartbeat(client: TestClient):
    """Test service heartbeat"""
    # Register a service first
    client.post(
        "/api/v1/services/register",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "test_agent_001"},
        json={
            "service_name": "test-heartbeat",
            "port": 7000,
            "status": "up"
        }
    )
    
    # Send heartbeat
    response = client.post(
        "/api/v1/services/test-heartbeat/heartbeat",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "test_agent_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "test-heartbeat"
    assert data["status"] == "up"

def test_get_mentions(client: TestClient, sample_api_data):
    """Test getting mentions for an agent"""
    # Create a document with mention
    client.post(
        "/api/v1/documents",
        headers={"X-API-Key": "development-key"},
        params={"author_id": "architect_test_001"},
        json={
            "doc_type": "critical_issue",
            "title": "Bug Report",
            "content": "Found a bug @frontend_dev_test_001 please fix"
        }
    )
    
    # Get mentions
    response = client.get(
        "/api/v1/mentions",
        headers={"X-API-Key": "development-key"},
        params={"agent_id": "frontend_dev_test_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["mentioned_agent_id"] == "frontend_dev_test_001"

def test_get_changes(client: TestClient):
    """Test changes polling endpoint"""
    response = client.get(
        "/api/v1/changes",
        headers={"X-API-Key": "development-key"},
        params={
            "since": "2020-01-01T00:00:00Z",
            "agent_id": "test_agent_001"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "changes" in data
    assert "last_timestamp" in data

def test_get_epics(client: TestClient, sample_api_data):
    """Test listing epics"""
    response = client.get(
        "/api/v1/epics",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Epic"

def test_get_features(client: TestClient, sample_api_data):
    """Test listing features for an epic"""
    epic = sample_api_data["epic"]
    
    response = client.get(
        f"/api/v1/features/{epic.id}",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Feature"

def test_get_changelog(client: TestClient):
    """Test getting changelog"""
    response = client.get(
        "/api/v1/changelog",
        headers={"X-API-Key": "development-key"}
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should be a list (may be empty)
    assert isinstance(data, list)