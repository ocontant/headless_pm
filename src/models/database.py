from sqlmodel import SQLModel, create_engine, Session, select
from typing import Generator
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_database_url() -> str:
    """Get database URL based on DB_CONNECTION setting in .env"""
    db_connection = os.getenv("DB_CONNECTION", "sqlite").lower()
    
    if db_connection == "mysql":
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "headless_pm")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "")
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # Default to SQLite
        return os.getenv("DATABASE_URL", "sqlite:///./headless_pm.db")

DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

def create_db_and_tables():
    """Create database tables and ensure default Headless-PM project exists."""
    SQLModel.metadata.create_all(engine)
    
    # Ensure default Headless-PM project exists
    ensure_default_project()

def ensure_default_project():
    """Ensure the default Headless-PM project exists in the database."""
    from .models import Project  # Import here to avoid circular imports
    
    with Session(engine) as session:
        # Check if Headless-PM project exists
        headless_pm = session.exec(
            select(Project).where(Project.name == "Headless-PM")
        ).first()
        
        if not headless_pm:
            # Import project utilities for path generation
            from src.services.project_utils import ensure_project_directories, get_project_docs_path, get_project_shared_path, get_project_instructions_path
            
            project_name = "Headless-PM"
            
            # Ensure project directories exist
            ensure_project_directories(project_name)
            
            # Create the default Headless-PM project
            default_project = Project(
                name=project_name,
                description="Headless PM application development and infrastructure",
                shared_path=get_project_shared_path(project_name),
                instructions_path=get_project_instructions_path(project_name),
                project_docs_path=get_project_docs_path(project_name),
                code_guidelines_path="./CLAUDE.md",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(default_project)
            session.commit()
            session.refresh(default_project)
            print("✅ Created default Headless-PM project")
            
            # Create dashboard-user agent for the default project
            ensure_dashboard_user(default_project.id, session)
        else:
            print("✅ Default Headless-PM project already exists")
        
        # Ensure dashboard-user exists for ALL projects
        all_projects = session.exec(select(Project)).all()
        for project in all_projects:
            ensure_dashboard_user(project.id, session)

def ensure_dashboard_user(project_id: int, session: Session):
    """Ensure the dashboard-user agent exists for the given project with UI_ADMIN privileges."""
    from .models import Agent  # Import here to avoid circular imports
    from .enums import AgentRole, DifficultyLevel, ConnectionType, AgentStatus
    
    # Check if dashboard-user agent exists for this project
    dashboard_user = session.exec(
        select(Agent).where(
            Agent.agent_id == "dashboard-user",
            Agent.project_id == project_id
        )
    ).first()
    
    if not dashboard_user:
        # Create the dashboard-user agent with UI_ADMIN role
        dashboard_agent = Agent(
            agent_id="dashboard-user",
            project_id=project_id,
            role=AgentRole.UI_ADMIN,  # Special UI admin role with task editing privileges
            level=DifficultyLevel.PRINCIPAL,  # Highest level for admin user
            connection_type=ConnectionType.UI,  # UI connection type
            status=AgentStatus.IDLE,
            last_seen=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc)
        )
        session.add(dashboard_agent)
        session.commit()
        print("✅ Created dashboard-user agent with UI_ADMIN privileges")
    else:
        # Update existing dashboard-user to have correct role and connection type
        if dashboard_user.role != AgentRole.UI_ADMIN or dashboard_user.connection_type != ConnectionType.UI:
            dashboard_user.role = AgentRole.UI_ADMIN
            dashboard_user.connection_type = ConnectionType.UI
            dashboard_user.level = DifficultyLevel.PRINCIPAL
            session.commit()
            print("✅ Updated dashboard-user agent to UI_ADMIN privileges")
        else:
            print("✅ Dashboard-user agent already exists with correct privileges")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session