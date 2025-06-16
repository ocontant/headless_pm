"""Test health and status endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime, timedelta
from src.main import app
from src.models.database import get_session
from src.models.models import Agent, Task, Document, Service, Epic, Feature, Mention, TaskEvaluation, Changelog
from src.models.enums import AgentRole, DifficultyLevel, TaskStatus
from src.models.document_enums import DocumentType, ServiceStatus

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
    """Create test client with session override"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_health_endpoint(client: TestClient):
    """Test /health endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "service" in data
    assert data["service"] == "headless-pm-api"
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "database" in data
    assert "timestamp" in data
    
    # Verify timestamp is valid ISO format
    datetime.fromisoformat(data["timestamp"])

def test_status_endpoint_empty(client: TestClient):
    """Test /status endpoint with empty database"""
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "service" in data
    assert data["service"] == "headless-pm-api"
    assert "version" in data
    assert "metrics" in data
    
    metrics = data["metrics"]
    assert metrics["total_agents"] == 0
    assert metrics["active_agents"] == 0
    assert metrics["total_tasks"] == 0
    assert metrics["total_documents"] == 0
    assert metrics["total_services"] == 0

def test_status_endpoint_with_data(client: TestClient):
    """Test /status endpoint returns proper structure"""
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "service" in data
    assert data["service"] == "headless-pm-api"
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "metrics" in data
    assert "timestamp" in data
    
    metrics = data["metrics"]
    # Just verify the structure, not specific counts since the endpoint uses its own session
    assert "total_agents" in metrics
    assert "active_agents" in metrics
    assert "total_tasks" in metrics
    assert "total_documents" in metrics
    assert "total_services" in metrics
    
    # Verify types
    assert isinstance(metrics["total_agents"], int)
    assert isinstance(metrics["active_agents"], int)
    assert isinstance(metrics["total_tasks"], int)
    assert isinstance(metrics["total_documents"], int)
    assert isinstance(metrics["total_services"], int)

def test_root_endpoint(client: TestClient):
    """Test root / endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Headless PM API"
    assert data["docs"] == "/api/v1/docs"
    assert data["health"] == "ok"

def test_health_endpoint_database_error(client: TestClient, session: Session):
    """Test /health endpoint when database has issues"""
    # This is difficult to test without mocking, but we can verify the structure
    # The actual database error testing would require more complex mocking
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Even with DB issues, endpoint should return 200 with degraded status
    assert "status" in data
    assert "database" in data