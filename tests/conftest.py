import pytest
from sqlmodel import Session, create_engine, SQLModel
from src.models.database import get_session
from src.models.models import Agent, Epic, Feature, Task, Document, Service, Mention, TaskEvaluation, Changelog
from src.models.enums import AgentRole, DifficultyLevel, TaskComplexity
from src.models.document_enums import DocumentType, ServiceStatus

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def sample_data(session: Session):
    # Create agents
    architect = Agent(
        agent_id="architect_principal_001",
        role=AgentRole.ARCHITECT,
        level=DifficultyLevel.PRINCIPAL
    )
    frontend_dev = Agent(
        agent_id="frontend_dev_senior_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    backend_dev = Agent(
        agent_id="backend_dev_junior_001",
        role=AgentRole.BACKEND_DEV,
        level=DifficultyLevel.JUNIOR
    )
    qa = Agent(
        agent_id="qa_senior_001",
        role=AgentRole.QA,
        level=DifficultyLevel.SENIOR
    )
    
    session.add_all([architect, frontend_dev, backend_dev, qa])
    session.commit()
    
    # Create epic and feature
    epic = Epic(name="User Authentication", description="Implement user auth system")
    session.add(epic)
    session.commit()
    
    feature = Feature(
        epic_id=epic.id,
        name="Login Form",
        description="Create login form component"
    )
    session.add(feature)
    session.commit()
    
    # Create tasks
    task1 = Task(
        feature_id=feature.id,
        title="Create login UI component",
        description="Build React component for login form",
        created_by_id=architect.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.JUNIOR,
        complexity=TaskComplexity.MINOR,
        branch="feature/login-ui"
    )
    task2 = Task(
        feature_id=feature.id,
        title="Implement login API endpoint",
        description="Create POST /api/login endpoint",
        created_by_id=architect.id,
        target_role=AgentRole.BACKEND_DEV,
        difficulty=DifficultyLevel.JUNIOR,
        complexity=TaskComplexity.MAJOR,
        branch="feature/login-api"
    )
    
    session.add_all([task1, task2])
    session.commit()
    
    return {
        "agents": {
            "architect": architect,
            "frontend_dev": frontend_dev,
            "backend_dev": backend_dev,
            "qa": qa
        },
        "epic": epic,
        "feature": feature,
        "tasks": [task1, task2]
    }