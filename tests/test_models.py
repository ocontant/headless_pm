import pytest
from datetime import datetime
from sqlmodel import Session, select
from src.models.models import Agent, Epic, Feature, Task, TaskEvaluation, Changelog
from src.models.enums import AgentRole, DifficultyLevel, TaskStatus

def test_agent_creation(session: Session):
    agent = Agent(
        agent_id="frontend_dev_senior_001",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent)
    session.commit()
    
    saved_agent = session.get(Agent, agent.id)
    assert saved_agent is not None
    assert saved_agent.agent_id == "frontend_dev_senior_001"
    assert saved_agent.role == AgentRole.FRONTEND_DEV
    assert saved_agent.level == DifficultyLevel.SENIOR
    assert isinstance(saved_agent.last_seen, datetime)

def test_epic_feature_relationship(session: Session):
    epic = Epic(name="User Dashboard", description="Build user dashboard")
    session.add(epic)
    session.commit()
    
    feature1 = Feature(epic_id=epic.id, name="Profile Widget", description="User profile display")
    feature2 = Feature(epic_id=epic.id, name="Stats Widget", description="User statistics")
    session.add_all([feature1, feature2])
    session.commit()
    
    # Test relationship
    saved_epic = session.get(Epic, epic.id)
    assert len(saved_epic.features) == 2
    assert saved_epic.features[0].name in ["Profile Widget", "Stats Widget"]

def test_task_creation_and_relationships(session: Session, sample_data):
    task = sample_data["tasks"][0]
    
    # Test task properties
    assert task.title == "Create login UI component"
    assert task.status == TaskStatus.CREATED
    assert task.target_role == AgentRole.FRONTEND_DEV
    assert task.difficulty == DifficultyLevel.JUNIOR
    
    # Test relationships
    assert task.feature.name == "Login Form"
    assert task.creator.agent_id == "architect_principal_001"
    assert task.locked_by_agent is None

def test_task_locking(session: Session, sample_data):
    task = sample_data["tasks"][0]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    
    # Lock the task
    task.locked_by_id = frontend_dev.id
    task.locked_at = datetime.utcnow()
    session.add(task)
    session.commit()
    
    # Verify lock
    locked_task = session.get(Task, task.id)
    assert locked_task.locked_by_id == frontend_dev.id
    assert locked_task.locked_by_agent.agent_id == "frontend_dev_senior_001"
    assert locked_task.locked_at is not None

def test_task_status_progression(session: Session, sample_data):
    task = sample_data["tasks"][0]
    
    # Progress through statuses
    statuses = [
        TaskStatus.CREATED,
        TaskStatus.EVALUATION,
        TaskStatus.APPROVED,
        TaskStatus.UNDER_WORK,
        TaskStatus.DEV_DONE,
        TaskStatus.QA_DONE,
        TaskStatus.DOCUMENTATION_DONE,
        TaskStatus.COMMITTED
    ]
    
    for status in statuses:
        task.status = status
        session.add(task)
        session.commit()
        
        saved_task = session.get(Task, task.id)
        assert saved_task.status == status

def test_task_evaluation(session: Session, sample_data):
    task = sample_data["tasks"][0]
    architect = sample_data["agents"]["architect"]
    
    # Create evaluation
    evaluation = TaskEvaluation(
        task_id=task.id,
        evaluated_by=architect.agent_id,
        approved=True,
        comment="Looks good, proceed with implementation"
    )
    session.add(evaluation)
    session.commit()
    
    # Verify evaluation
    saved_eval = session.get(TaskEvaluation, evaluation.id)
    assert saved_eval.approved is True
    assert saved_eval.evaluated_by == "architect_principal_001"
    assert saved_eval.task.id == task.id

def test_changelog_tracking(session: Session, sample_data):
    task = sample_data["tasks"][0]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    
    # Create changelog entry
    changelog = Changelog(
        task_id=task.id,
        old_status=TaskStatus.APPROVED,
        new_status=TaskStatus.UNDER_WORK,
        changed_by=frontend_dev.agent_id,
        notes="Starting work on login component"
    )
    session.add(changelog)
    session.commit()
    
    # Verify changelog
    saved_log = session.get(Changelog, changelog.id)
    assert saved_log.old_status == TaskStatus.APPROVED
    assert saved_log.new_status == TaskStatus.UNDER_WORK
    assert saved_log.changed_by == "frontend_dev_senior_001"

def test_task_assignment_by_role_and_level(session: Session, sample_data):
    # Query tasks for frontend developer
    tasks = session.exec(
        select(Task).where(
            Task.target_role == AgentRole.FRONTEND_DEV,
            Task.difficulty == DifficultyLevel.JUNIOR
        )
    ).all()
    
    assert len(tasks) == 1
    assert tasks[0].title == "Create login UI component"

def test_agent_unique_constraint(session: Session):
    # Create first agent
    agent1 = Agent(
        agent_id="qa_senior_001",
        role=AgentRole.QA,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent1)
    session.commit()
    
    # Try to create duplicate agent_id
    agent2 = Agent(
        agent_id="qa_senior_001",
        role=AgentRole.QA,
        level=DifficultyLevel.SENIOR
    )
    session.add(agent2)
    
    with pytest.raises(Exception):  # Should raise integrity error
        session.commit()