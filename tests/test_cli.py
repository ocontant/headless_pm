import pytest
from typer.testing import CliRunner
from sqlmodel import Session, create_engine, SQLModel
from src.cli.main import app
from src.models.database import get_session
from src.models.models import Agent, Epic, Feature, Task
from src.models.enums import AgentRole, DifficultyLevel, TaskComplexity

# Mock the get_session dependency for CLI tests
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Import all models to ensure they're registered
    from src.models.models import Agent, Task, Epic, Feature, Document, Service, Mention, TaskEvaluation, Changelog
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def mock_get_session(session: Session, monkeypatch):
    """Mock the get_session function for CLI tests"""
    def mock_get_db():
        return session
    
    # Patch the get_db function in the CLI module
    monkeypatch.setattr("src.cli.main.get_db", mock_get_db)
    return session

def test_cli_status_empty(mock_get_session):
    """Test status command with empty database"""
    runner = CliRunner()
    result = runner.invoke(app, ["status"])
    
    assert result.exit_code == 0
    assert "Headless PM Status" in result.stdout
    assert "Registered Agents: 0" in result.stdout

def test_cli_status_with_data(mock_get_session):
    """Test status command with some data"""
    session = mock_get_session
    
    # Add some test data
    agent = Agent(
        agent_id="test_agent_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent)
    session.commit()
    
    runner = CliRunner()
    result = runner.invoke(app, ["status"])
    
    assert result.exit_code == 0
    assert "Registered Agents: 1" in result.stdout

def test_cli_agents_empty(mock_get_session):
    """Test agents command with empty database"""
    runner = CliRunner()
    result = runner.invoke(app, ["agents"])
    
    assert result.exit_code == 0
    assert "No agents registered" in result.stdout

def test_cli_agents_with_data(mock_get_session):
    """Test agents command with data"""
    session = mock_get_session
    
    agent = Agent(
        agent_id="frontend_dev_senior_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent)
    session.commit()
    
    runner = CliRunner()
    result = runner.invoke(app, ["agents"])
    
    assert result.exit_code == 0
    assert "frontend_dev_senior_001" in result.stdout

def test_cli_tasks_empty(mock_get_session):
    """Test tasks command with empty database"""
    runner = CliRunner()
    result = runner.invoke(app, ["tasks"])
    
    assert result.exit_code == 0
    assert "No tasks found" in result.stdout

def test_cli_tasks_with_data(mock_get_session):
    """Test tasks command with data"""
    session = mock_get_session
    
    # Create required data
    agent = Agent(
        agent_id="architect_001",
        role=AgentRole.ARCHITECT,
        level=DifficultyLevel.PRINCIPAL
    )
    session.add(agent)
    session.commit()
    
    epic = Epic(name="Test Epic", description="Test epic")
    session.add(epic)
    session.commit()
    
    feature = Feature(epic_id=epic.id, name="Test Feature", description="Test feature")
    session.add(feature)
    session.commit()
    
    task = Task(
        feature_id=feature.id,
        title="Test Task",
        description="Test task description",
        created_by_id=agent.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        complexity=TaskComplexity.MINOR,
        branch="feature/test"
    )
    session.add(task)
    session.commit()
    
    runner = CliRunner()
    result = runner.invoke(app, ["tasks"])
    
    assert result.exit_code == 0
    assert "Test Task" in result.stdout

def test_cli_tasks_filter_by_status(mock_get_session):
    """Test tasks command with status filter"""
    runner = CliRunner()
    result = runner.invoke(app, ["tasks", "--status", "created"])
    
    assert result.exit_code == 0

def test_cli_tasks_filter_by_role(mock_get_session):
    """Test tasks command with role filter"""
    runner = CliRunner()
    result = runner.invoke(app, ["tasks", "--role", "frontend_dev"])
    
    assert result.exit_code == 0

def test_cli_tasks_invalid_status(mock_get_session):
    """Test tasks command with invalid status"""
    runner = CliRunner()
    result = runner.invoke(app, ["tasks", "--status", "invalid_status"])
    
    assert result.exit_code == 0
    assert "Invalid status" in result.stdout

def test_cli_tasks_invalid_role(mock_get_session):
    """Test tasks command with invalid role"""
    runner = CliRunner()
    result = runner.invoke(app, ["tasks", "--role", "invalid_role"])
    
    assert result.exit_code == 0
    assert "Invalid role" in result.stdout

def test_cli_services_empty(mock_get_session):
    """Test services command with empty database"""
    runner = CliRunner()
    result = runner.invoke(app, ["services"])
    
    assert result.exit_code == 0
    assert "No services registered" in result.stdout

def test_cli_documents_empty(mock_get_session):
    """Test documents command with empty database"""
    runner = CliRunner()
    result = runner.invoke(app, ["documents"])
    
    assert result.exit_code == 0
    assert "No documents found" in result.stdout

def test_cli_documents_invalid_type(mock_get_session):
    """Test documents command with invalid type"""
    runner = CliRunner()
    result = runner.invoke(app, ["documents", "--doc-type", "invalid_type"])
    
    assert result.exit_code == 0
    assert "Invalid document type" in result.stdout

def test_cli_reset_cancelled(mock_get_session):
    """Test reset command when cancelled"""
    runner = CliRunner()
    result = runner.invoke(app, ["reset"], input="n\n")
    
    assert result.exit_code == 0
    assert "Operation cancelled" in result.stdout

def test_cli_init(mock_get_session):
    """Test init command"""
    runner = CliRunner()
    result = runner.invoke(app, ["init"])
    
    assert result.exit_code == 0
    assert "Database initialized successfully" in result.stdout

def test_cli_seed(mock_get_session):
    """Test seed command"""
    runner = CliRunner()
    result = runner.invoke(app, ["seed"])
    
    assert result.exit_code == 0
    assert "Creating sample data" in result.stdout
    assert "Sample data created successfully" in result.stdout