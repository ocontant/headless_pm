"""Test the fixed comment endpoint"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, select
from src.main import app
from src.models.database import get_session
from src.models.models import Agent, Task, Epic, Feature, Mention, Document, Service, TaskEvaluation, Changelog
from src.models.enums import AgentRole, DifficultyLevel, TaskStatus
from src.api.dependencies import verify_api_key, get_db

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
    
    def get_db_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_api_key] = verify_api_key_override
    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_add_comment_to_task(client: TestClient, session: Session):
    """Test adding a comment to a task"""
    # Create agent
    agent = Agent(
        agent_id="pm_principal_001",
        role=AgentRole.PM,
        level=DifficultyLevel.PRINCIPAL
    )
    session.add(agent)
    session.commit()
    
    # Create epic, feature, and task
    epic = Epic(name="Test Epic", description="Test")
    session.add(epic)
    session.commit()
    
    feature = Feature(epic_id=epic.id, name="Test Feature", description="Test")
    session.add(feature)
    session.commit()
    
    task = Task(
        feature_id=feature.id,
        title="Test Task",
        description="Test task description",
        created_by_id=agent.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="test-branch"
    )
    session.add(task)
    session.commit()
    
    # Add comment
    response = client.post(
        f"/api/v1/tasks/{task.id}/comment",
        params={"agent_id": agent.agent_id},
        json={"comment": "This looks good, but needs more testing"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Comment added successfully"
    
    # Verify comment was added to task notes
    session.refresh(task)
    assert task.notes == "pm_principal_001: This looks good, but needs more testing"

def test_add_comment_with_mention(client: TestClient, session: Session):
    """Test adding a comment with @mentions"""
    # Create agents
    pm = Agent(agent_id="pm_001", role=AgentRole.PM, level=DifficultyLevel.PRINCIPAL)
    dev = Agent(agent_id="frontend_dev_001", role=AgentRole.FRONTEND_DEV, level=DifficultyLevel.SENIOR)
    session.add_all([pm, dev])
    session.commit()
    
    # Create epic, feature, and task
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
        created_by_id=pm.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="test"
    )
    session.add(task)
    session.commit()
    
    # Add comment with mention
    response = client.post(
        f"/api/v1/tasks/{task.id}/comment",
        params={"agent_id": pm.agent_id},
        json={"comment": "Please review this @frontend_dev_001"}
    )
    
    assert response.status_code == 200
    
    # Check mention was created
    mentions = session.exec(
        select(Mention).where(
            Mention.task_id == task.id,
            Mention.mentioned_agent_id == "frontend_dev_001"
        )
    ).all()
    
    assert len(mentions) == 1
    assert mentions[0].created_by == pm.agent_id

def test_add_multiple_comments(client: TestClient, session: Session):
    """Test adding multiple comments to a task"""
    # Create agents
    pm = Agent(agent_id="pm_001", role=AgentRole.PM, level=DifficultyLevel.PRINCIPAL)
    arch = Agent(agent_id="architect_001", role=AgentRole.ARCHITECT, level=DifficultyLevel.PRINCIPAL)
    session.add_all([pm, arch])
    session.commit()
    
    # Create task
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
        created_by_id=pm.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="test"
    )
    session.add(task)
    session.commit()
    
    # Add first comment
    response1 = client.post(
        f"/api/v1/tasks/{task.id}/comment",
        params={"agent_id": pm.agent_id},
        json={"comment": "Initial review comment"}
    )
    assert response1.status_code == 200
    
    # Add second comment
    response2 = client.post(
        f"/api/v1/tasks/{task.id}/comment",
        params={"agent_id": arch.agent_id},
        json={"comment": "Architecture looks good"}
    )
    assert response2.status_code == 200
    
    # Verify both comments are in notes
    session.refresh(task)
    assert "pm_001: Initial review comment" in task.notes
    assert "architect_001: Architecture looks good" in task.notes
    assert task.notes.count("\n\n") == 1  # Comments are separated by double newline

def test_comment_on_nonexistent_task(client: TestClient):
    """Test adding comment to non-existent task"""
    response = client.post(
        "/api/v1/tasks/999/comment",
        params={"agent_id": "test_agent"},
        json={"comment": "Test comment"}
    )
    
    assert response.status_code == 404
    assert "Task with ID 999 not found" in response.json()["detail"]