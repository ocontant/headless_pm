"""Test improved error messages in API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from src.main import app
from src.models.database import get_session
from src.models.models import Agent, Task, Document, Epic, Feature, Mention, TaskEvaluation, Changelog, Service
from src.models.enums import AgentRole, DifficultyLevel, TaskStatus
from src.api.dependencies import verify_api_key

@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine"""
    import tempfile
    import os
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    
    yield engine
    os.unlink(db_path)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with session and auth overrides"""
    def get_session_override():
        return session
    
    def verify_api_key_override():
        return "development-key"

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_api_key] = verify_api_key_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_get_next_task_missing_role(client: TestClient):
    """Test GET /tasks/next with missing role parameter"""
    response = client.get(
        "/api/v1/tasks/next",
        params={"level": "senior"}
    )
    
    assert response.status_code == 400
    assert "Missing required parameter 'role'" in response.json()["detail"]
    assert "?role=frontend_dev" in response.json()["detail"]

def test_get_next_task_missing_level(client: TestClient):
    """Test GET /tasks/next with missing level parameter"""
    response = client.get(
        "/api/v1/tasks/next",
        params={"role": "frontend_dev"}
    )
    
    assert response.status_code == 400
    assert "Missing required parameter 'level'" in response.json()["detail"]
    assert "?level=senior" in response.json()["detail"]

def test_lock_task_not_found(client: TestClient, session: Session):
    """Test task lock with non-existent task ID"""
    # Create an agent first
    agent = Agent(
        agent_id="test_agent_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent)
    session.commit()
    
    response = client.post(
        "/api/v1/tasks/999/lock",
        params={"agent_id": agent.agent_id}
    )
    
    assert response.status_code == 404
    assert "Task with ID 999 not found" in response.json()["detail"]
    assert "verify the task ID exists" in response.json()["detail"]

def test_lock_task_already_locked(client: TestClient, session: Session):
    """Test locking an already locked task"""
    # Create agents
    agent1 = Agent(agent_id="agent1", role=AgentRole.FRONTEND_DEV, level=DifficultyLevel.SENIOR)
    agent2 = Agent(agent_id="agent2", role=AgentRole.FRONTEND_DEV, level=DifficultyLevel.SENIOR)
    session.add_all([agent1, agent2])
    session.commit()
    
    # Create and lock a task
    from src.models.models import Epic, Feature
    epic = Epic(name="Test Epic", description="Test")
    session.add(epic)
    session.commit()
    
    feature = Feature(epic_id=epic.id, name="Test Feature", description="Test")
    session.add(feature)
    session.commit()
    
    task = Task(
        feature_id=feature.id,
        title="Test Task",
        description="Test",
        created_by_id=agent1.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="test",
        locked_by_id=agent1.id
    )
    session.add(task)
    session.commit()
    
    # Try to lock with second agent
    response = client.post(
        f"/api/v1/tasks/{task.id}/lock",
        params={"agent_id": agent2.agent_id}
    )
    
    assert response.status_code == 409
    assert f"Task {task.id} is already locked" in response.json()["detail"]
    assert "must be unlocked" in response.json()["detail"]

def test_agent_not_found(client: TestClient, session: Session):
    """Test operations with non-existent agent"""
    # Create a task
    from src.models.models import Epic, Feature
    agent = Agent(agent_id="creator", role=AgentRole.ARCHITECT, level=DifficultyLevel.PRINCIPAL)
    session.add(agent)
    session.commit()
    
    epic = Epic(name="Test Epic", description="Test")
    session.add(epic)
    session.commit()
    
    feature = Feature(epic_id=epic.id, name="Test Feature", description="Test")
    session.add(feature)
    session.commit()
    
    task = Task(
        feature_id=feature.id,
        title="Test Task",
        description="Test",
        created_by_id=agent.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="test"
    )
    session.add(task)
    session.commit()
    
    response = client.post(
        f"/api/v1/tasks/{task.id}/lock",
        params={"agent_id": "non_existent_agent"}
    )
    
    assert response.status_code == 404
    assert "Agent 'non_existent_agent' not found" in response.json()["detail"]
    assert "POST /api/v1/register" in response.json()["detail"]

def test_document_not_found(client: TestClient):
    """Test document operations with non-existent document"""
    response = client.get("/api/v1/documents/999")
    
    assert response.status_code == 404
    assert "Document with ID 999 not found" in response.json()["detail"]
    assert "verify the document ID exists" in response.json()["detail"]

def test_document_content_too_long(client: TestClient):
    """Test document creation with content exceeding limit"""
    response = client.post(
        "/api/v1/documents",
        params={"author_id": "test_agent"},
        json={
            "doc_type": "update",
            "title": "Test",
            "content": "x" * 50001  # Exceeds 50KB limit
        }
    )
    
    assert response.status_code == 400
    assert "exceeds maximum length of 50,000 characters" in response.json()["detail"]