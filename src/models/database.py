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
            # Create the default Headless-PM project
            default_project = Project(
                name="Headless-PM",
                description="Headless PM application development and infrastructure",
                shared_path="./shared",
                instructions_path="./agents/mcp",
                project_docs_path="./docs",
                code_guidelines_path="./CLAUDE.md",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(default_project)
            session.commit()
            print("✅ Created default Headless-PM project")
        else:
            print("✅ Default Headless-PM project already exists")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session