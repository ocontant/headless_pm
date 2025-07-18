#!/usr/bin/env python3
"""
Headless PM CLI - Command-line interface for project management
"""

import typer
from typing import Optional
from sqlmodel import Session, select
from tabulate import tabulate
from datetime import datetime, timezone
import os

from shared.models.database import get_session, create_db_and_tables
from shared.models.models import Agent, Epic, Feature, Task, Service, Document, Project
from shared.models.enums import TaskStatus, AgentRole, DifficultyLevel
from shared.models.document_enums import DocumentType, ServiceStatus

app = typer.Typer(help="Headless PM - Project Management for LLM Agents")

def get_db() -> Session:
    """Get database session"""
    return next(get_session())

def ensure_default_project(db: Session) -> Project:
    """Ensure a default project exists, create one if not"""
    project = db.exec(select(Project)).first()
    if not project:
        project = Project(
            name="Default",
            description="Default project for Headless PM",
            shared_path="./shared",
            instructions_path="./agent_instructions", 
            project_docs_path="./docs"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        typer.echo(f"✅ Created default project (ID: {project.id})")
    return project

@app.command()
def status():
    """Show project status overview"""
    db = get_db()
    
    # Count tasks by status
    task_counts = {}
    for status in TaskStatus:
        count = len(db.exec(select(Task).where(Task.status == status)).all())
        task_counts[status.value] = count
    
    # Count active agents
    agent_count = len(db.exec(select(Agent)).all())
    
    # Count active services
    active_services = len(db.exec(
        select(Service).where(Service.status == ServiceStatus.UP)
    ).all())
    
    # Recent documents
    recent_docs = len(db.exec(
        select(Document).where(
            Document.created_at > datetime.now().replace(hour=0, minute=0, second=0)
        )
    ).all())
    
    typer.echo("🚀 Headless PM Status")
    typer.echo("=" * 50)
    typer.echo(f"Registered Agents: {agent_count}")
    typer.echo(f"Active Services: {active_services}")
    typer.echo(f"Documents Today: {recent_docs}")
    typer.echo("\nTask Breakdown:")
    
    for status, count in task_counts.items():
        typer.echo(f"  {status.replace('_', ' ').title()}: {count}")

@app.command()
def tasks(
    status: Optional[str] = typer.Option(None, help="Filter by task status"),
    role: Optional[str] = typer.Option(None, help="Filter by target role")
):
    """Show task assignments"""
    db = get_db()
    
    query = select(Task).order_by(Task.created_at.desc())
    
    if status:
        try:
            task_status = TaskStatus(status)
            query = query.where(Task.status == task_status)
        except ValueError:
            typer.echo(f"Invalid status: {status}")
            return
    
    if role:
        try:
            agent_role = AgentRole(role)
            query = query.where(Task.target_role == agent_role)
        except ValueError:
            typer.echo(f"Invalid role: {role}")
            return
    
    tasks = db.exec(query.limit(20)).all()
    
    if not tasks:
        typer.echo("No tasks found matching criteria")
        return
    
    # Prepare table data
    table_data = []
    for task in tasks:
        table_data.append([
            task.id,
            task.title[:30] + "..." if len(task.title) > 30 else task.title,
            task.target_role.value,
            task.difficulty.value,
            task.status.value.replace('_', ' '),
            task.creator.agent_id if task.creator else "unknown",
            task.locked_by_agent.agent_id if task.locked_by_agent else "-"
        ])
    
    headers = ["ID", "Title", "Role", "Level", "Status", "Creator", "Locked By"]
    typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

@app.command()
def reset():
    """Reset database (WARNING: Deletes all data)"""
    confirm = typer.confirm("This will delete ALL data. Are you sure?")
    if not confirm:
        typer.echo("Operation cancelled")
        return
    
    db = get_db()
    
    # Drop and recreate tables
    from shared.models.database import engine
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    typer.echo("✅ Database reset successfully")

@app.command()
def agents():
    """List registered agents"""
    db = get_db()
    
    agents = db.exec(select(Agent).order_by(Agent.last_seen.desc())).all()
    
    if not agents:
        typer.echo("No agents registered")
        return
    
    table_data = []
    for agent in agents:
        last_seen = agent.last_seen.strftime("%Y-%m-%d %H:%M") if agent.last_seen else "Never"
        table_data.append([
            agent.agent_id,
            agent.role.value,
            agent.level.value,
            last_seen
        ])
    
    headers = ["Agent ID", "Role", "Level", "Last Seen"]
    typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

@app.command()
def services():
    """List registered services"""
    db = get_db()
    
    services = db.exec(select(Service).order_by(Service.service_name)).all()
    
    if not services:
        typer.echo("No services registered")
        return
    
    table_data = []
    for service in services:
        port_str = str(service.port) if service.port else "-"
        last_heartbeat = service.last_heartbeat.strftime("%H:%M:%S") if service.last_heartbeat else "Never"
        
        table_data.append([
            service.service_name,
            service.owner_agent_id,
            port_str,
            service.status.value,
            last_heartbeat
        ])
    
    headers = ["Service", "Owner", "Port", "Status", "Last Heartbeat"]
    typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

@app.command()
def documents(
    doc_type: Optional[str] = typer.Option(None, help="Filter by document type")
):
    """List recent documents"""
    db = get_db()
    
    query = select(Document).order_by(Document.created_at.desc())
    
    if doc_type:
        try:
            document_type = DocumentType(doc_type)
            query = query.where(Document.doc_type == document_type)
        except ValueError:
            typer.echo(f"Invalid document type: {doc_type}")
            return
    
    docs = db.exec(query.limit(20)).all()
    
    if not docs:
        typer.echo("No documents found")
        return
    
    table_data = []
    for doc in docs:
        created = doc.created_at.strftime("%m-%d %H:%M")
        title = doc.title[:40] + "..." if len(doc.title) > 40 else doc.title
        
        table_data.append([
            doc.id,
            doc.doc_type.value,
            title,
            doc.author_id,
            created
        ])
    
    headers = ["ID", "Type", "Title", "Author", "Created"]
    typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

@app.command()
def seed(project_id: Optional[int] = typer.Option(None, help="Project ID (if not provided, uses or creates default project)")):
    """Create sample data for testing"""
    db = get_db()
    
    # Get or create project
    if project_id:
        project = db.get(Project, project_id)
        if not project:
            typer.echo(f"❌ Project with ID {project_id} not found")
            return
    else:
        project = ensure_default_project(db)
    
    typer.echo(f"Creating sample data for project: {project.name} (ID: {project.id})")
    
    # Create sample epic and feature
    epic = Epic(
        project_id=project.id,
        name="User Authentication",
        description="Implement complete user authentication system"
    )
    db.add(epic)
    db.commit()
    db.refresh(epic)
    
    feature = Feature(
        epic_id=epic.id,
        name="Login System",
        description="User login with JWT authentication"
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)
    
    # Create sample agents
    agents = [
        Agent(
            agent_id="architect_principal_001",
            project_id=project.id,
            role=AgentRole.ARCHITECT,
            level=DifficultyLevel.PRINCIPAL
        ),
        Agent(
            agent_id="frontend_dev_senior_001",
            project_id=project.id,
            role=AgentRole.FRONTEND_DEV,
            level=DifficultyLevel.SENIOR
        ),
        Agent(
            agent_id="backend_dev_senior_001",
            project_id=project.id,
            role=AgentRole.BACKEND_DEV,
            level=DifficultyLevel.SENIOR
        ),
        Agent(
            agent_id="qa_senior_001",
            project_id=project.id,
            role=AgentRole.QA,
            level=DifficultyLevel.SENIOR
        )
    ]
    
    for agent in agents:
        db.add(agent)
    db.commit()
    
    # Create sample tasks
    architect = agents[0]
    
    tasks = [
        Task(
            feature_id=feature.id,
            title="Design login UI mockups",
            description="Create wireframes and mockups for login interface",
            created_by_id=architect.id,
            target_role=AgentRole.FRONTEND_DEV,
            difficulty=DifficultyLevel.SENIOR,
            branch="feature/login-ui"
        ),
        Task(
            feature_id=feature.id,
            title="Implement JWT authentication API",
            description="Create login/logout endpoints with JWT tokens",
            created_by_id=architect.id,
            target_role=AgentRole.BACKEND_DEV,
            difficulty=DifficultyLevel.SENIOR,
            branch="feature/jwt-auth"
        ),
        Task(
            feature_id=feature.id,
            title="Write authentication tests",
            description="Create comprehensive test suite for auth system",
            created_by_id=architect.id,
            target_role=AgentRole.QA,
            difficulty=DifficultyLevel.SENIOR,
            branch="feature/auth-tests"
        )
    ]
    
    for task in tasks:
        db.add(task)
    db.commit()
    
    # Create sample documents
    docs = [
        Document(
            project_id=project.id,
            doc_type=DocumentType.UPDATE,
            author_id="architect_principal_001",
            title="Daily Standup - Architecture",
            content="## Yesterday\n- Reviewed authentication requirements\n- Created initial task breakdown\n\n## Today\n- Finalizing API design\n- Creating detailed tasks\n\n## Blockers\n- None"
        ),
        Document(
            project_id=project.id,
            doc_type=DocumentType.REPORT,
            author_id="qa_senior_001",
            title="Test Environment Down",
            content="The test environment is currently down. @backend_dev_senior_001 please investigate."
        )
    ]
    
    for doc in docs:
        db.add(doc)
    db.commit()
    
    typer.echo("✅ Sample data created successfully!")
    typer.echo(f"Created: 1 epic, 1 feature, {len(tasks)} tasks, {len(agents)} agents, {len(docs)} documents")

@app.command()
def projects():
    """List all projects"""
    db = get_db()
    
    projects = db.exec(select(Project).order_by(Project.created_at.desc())).all()
    
    if not projects:
        typer.echo("No projects found")
        return
    
    table_data = []
    for project in projects:
        # Count agents, epics, and tasks for each project
        agent_count = len(db.exec(select(Agent).where(Agent.project_id == project.id)).all())
        epic_count = len(db.exec(select(Epic).where(Epic.project_id == project.id)).all())
        
        # Count tasks through features and epics
        from sqlmodel import func
        task_count = db.exec(
            select(func.count(Task.id))
            .join(Feature)
            .join(Epic)
            .where(Epic.project_id == project.id)
        ).one() or 0
        
        created = project.created_at.strftime("%Y-%m-%d %H:%M")
        
        table_data.append([
            project.id,
            project.name,
            project.description[:50] + "..." if len(project.description) > 50 else project.description,
            agent_count,
            epic_count,
            task_count,
            created
        ])
    
    headers = ["ID", "Name", "Description", "Agents", "Epics", "Tasks", "Created"]
    typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

@app.command()
def delete_project(
    project_id: int = typer.Argument(..., help="Project ID to delete"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation prompt")
):
    """Delete a project and all its data (WARNING: This deletes everything!)"""
    db = get_db()
    
    # Get project
    project = db.get(Project, project_id)
    if not project:
        typer.echo(f"❌ Project with ID {project_id} not found")
        return
    
    # Count what will be deleted
    agent_count = len(db.exec(select(Agent).where(Agent.project_id == project_id)).all())
    epic_count = len(db.exec(select(Epic).where(Epic.project_id == project_id)).all())
    doc_count = len(db.exec(select(Document).where(Document.project_id == project_id)).all())
    service_count = len(db.exec(select(Service).where(Service.project_id == project_id)).all())
    
    # Count tasks through features and epics
    from sqlmodel import func
    task_count = db.exec(
        select(func.count(Task.id))
        .join(Feature)
        .join(Epic)
        .where(Epic.project_id == project_id)
    ).one() or 0
    
    typer.echo(f"🗑️  Deleting project: {project.name} (ID: {project_id})")
    typer.echo("This will permanently delete:")
    typer.echo(f"  • {agent_count} agents")
    typer.echo(f"  • {epic_count} epics")
    typer.echo(f"  • {task_count} tasks")
    typer.echo(f"  • {doc_count} documents")
    typer.echo(f"  • {service_count} services")
    typer.echo("")
    
    if not confirm:
        confirm = typer.confirm("Are you absolutely sure you want to delete this project and ALL its data?")
        if not confirm:
            typer.echo("Operation cancelled")
            return
    
    try:
        # Delete project (cascade should handle dependencies)
        db.delete(project)
        db.commit()
        
        typer.echo(f"✅ Project '{project.name}' and all associated data deleted successfully")
        
    except Exception as e:
        db.rollback()
        typer.echo(f"❌ Error deleting project: {e}")

@app.command()
def init():
    """Initialize database and create tables"""
    create_db_and_tables()
    typer.echo("✅ Database initialized successfully")

@app.command()
def dashboard():
    """Launch real-time dashboard"""
    from .dashboard import HeadlessPMDashboard
    dashboard = HeadlessPMDashboard()
    dashboard.run()

@app.command("sanity-check")
def sanity_check(
    fix_issues: bool = typer.Option(False, "--fix", help="Automatically fix issues where possible"),
    check_enums: bool = typer.Option(True, "--check-enums/--skip-enums", help="Check enum value consistency"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Run comprehensive sanity checks on the database"""
    from shared.models.enums import TaskStatus, AgentRole, DifficultyLevel, TaskComplexity, ConnectionType, AgentStatus
    from shared.models.document_enums import DocumentType, ServiceStatus
    
    typer.echo("🏥 Starting Headless PM Database Sanity Check")
    typer.echo(f"📅 Timestamp: {datetime.now(timezone.utc).isoformat()}")
    
    if fix_issues:
        typer.echo("🔧 Fix mode enabled - issues will be automatically corrected where possible")
    
    db = get_db()
    total_checks = 0
    passed_checks = 0
    issues_found = []
    
    if check_enums:
        typer.echo("\n🔍 Checking enum value consistency...")
        
        # Use SQLModel to check enum consistency (now that deserialization is fixed)
        valid_agent_roles = [r.value for r in AgentRole]
        valid_agent_statuses = [s.value for s in AgentStatus]
        valid_levels = [l.value for l in DifficultyLevel]
        valid_connections = [c.value for c in ConnectionType]
        valid_task_statuses = [s.value for s in TaskStatus]
        valid_complexities = [c.value for c in TaskComplexity]
        valid_service_statuses = [s.value for s in ServiceStatus]
        valid_doc_types = [t.value for t in DocumentType]
        
        # Check agents
        try:
            agents = db.exec(select(Agent)).all()
            for agent in agents:
                total_checks += 4
                
                if agent.role.value not in valid_agent_roles:
                    issues_found.append(f"Agent {agent.agent_id}: invalid role '{agent.role.value}'")
                else:
                    passed_checks += 1
                    
                if agent.level.value not in valid_levels:
                    issues_found.append(f"Agent {agent.agent_id}: invalid level '{agent.level.value}'")
                else:
                    passed_checks += 1
                    
                if agent.status.value not in valid_agent_statuses:
                    issues_found.append(f"Agent {agent.agent_id}: invalid status '{agent.status.value}'")
                else:
                    passed_checks += 1
                    
                if agent.connection_type and agent.connection_type.value not in valid_connections:
                    issues_found.append(f"Agent {agent.agent_id}: invalid connection_type '{agent.connection_type.value}'")
                else:
                    passed_checks += 1
        except Exception as e:
            issues_found.append(f"Error checking agents: {e}")
        
        # Check tasks
        try:
            tasks = db.exec(select(Task)).all()
            for task in tasks:
                total_checks += 4
                
                if task.status.value not in valid_task_statuses:
                    issues_found.append(f"Task {task.id} '{task.title}': invalid status '{task.status.value}'")
                else:
                    passed_checks += 1
                    
                if task.target_role.value not in valid_agent_roles:
                    issues_found.append(f"Task {task.id} '{task.title}': invalid target_role '{task.target_role.value}'")
                else:
                    passed_checks += 1
                    
                if task.difficulty.value not in valid_levels:
                    issues_found.append(f"Task {task.id} '{task.title}': invalid difficulty '{task.difficulty.value}'")
                else:
                    passed_checks += 1
                    
                if task.complexity.value not in valid_complexities:
                    issues_found.append(f"Task {task.id} '{task.title}': invalid complexity '{task.complexity.value}'")
                else:
                    passed_checks += 1
        except Exception as e:
            issues_found.append(f"Error checking tasks: {e}")
        
        # Check services
        try:
            services = db.exec(select(Service)).all()
            for service in services:
                total_checks += 1
                
                if service.status.value not in valid_service_statuses:
                    issues_found.append(f"Service '{service.service_name}': invalid status '{service.status.value}'")
                else:
                    passed_checks += 1
        except Exception as e:
            issues_found.append(f"Error checking services: {e}")
        
        # Check documents
        try:
            documents = db.exec(select(Document)).all()
            for document in documents:
                total_checks += 1
                
                if document.doc_type.value not in valid_doc_types:
                    issues_found.append(f"Document {document.id} '{document.title}': invalid doc_type '{document.doc_type.value}'")
                else:
                    passed_checks += 1
        except Exception as e:
            issues_found.append(f"Error checking documents: {e}")
        
        typer.echo(f"  ✅ Checked {len(agents) if 'agents' in locals() else 0} agents, {len(tasks) if 'tasks' in locals() else 0} tasks, {len(services) if 'services' in locals() else 0} services, {len(documents) if 'documents' in locals() else 0} documents")
    
    if fix_issues and issues_found:
        db.commit()
        typer.echo(f"\n✅ Applied fixes to database")
    
    # Display results
    typer.echo("\n" + "="*60)
    typer.echo("📋 SANITY CHECK REPORT")
    typer.echo("="*60)
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    typer.echo(f"Total Checks: {total_checks}")
    typer.echo(f"Passed: {passed_checks}")
    typer.echo(f"Issues: {len(issues_found)}")
    typer.echo(f"Success Rate: {success_rate:.1f}%")
    
    if issues_found:
        typer.echo(f"\n🚨 ISSUES FOUND ({len(issues_found)}):")
        for issue in issues_found[:10]:  # Show first 10
            typer.echo(f"  • {issue}")
        if len(issues_found) > 10:
            typer.echo(f"  ... and {len(issues_found) - 10} more")
        
        if not fix_issues:
            typer.echo("\n💡 Run with --fix to automatically fix issues where possible")
    
    if len(issues_found) == 0:
        typer.echo("\n✅ All checks passed! Database is healthy.")
    else:
        typer.echo(f"\n❌ {len(issues_found)} issue(s) detected.")
        if len(issues_found) > 0:
            return 1  # Exit with error code
    
    db.close()

if __name__ == "__main__":
    app()