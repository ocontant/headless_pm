import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.models.models import Agent, Task, TaskEvaluation, Changelog
from src.models.enums import TaskStatus, AgentRole, DifficultyLevel

def test_complete_task_lifecycle(session: Session, sample_data):
    """Test a task going through the complete lifecycle"""
    task = sample_data["tasks"][0]
    architect = sample_data["agents"]["architect"]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    qa = sample_data["agents"]["qa"]
    
    # Step 1: Task created (already done in sample_data)
    assert task.status == TaskStatus.CREATED
    
    # Step 2: Move to evaluation
    task.status = TaskStatus.EVALUATION
    changelog1 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.CREATED,
        new_status=TaskStatus.EVALUATION,
        changed_by=architect.agent_id
    )
    session.add_all([task, changelog1])
    session.commit()
    
    # Step 3: Evaluate and approve
    evaluation = TaskEvaluation(
        task_id=task.id,
        evaluated_by=architect.agent_id,
        approved=True,
        comment="Good task definition"
    )
    task.status = TaskStatus.APPROVED
    changelog2 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.EVALUATION,
        new_status=TaskStatus.APPROVED,
        changed_by=architect.agent_id
    )
    session.add_all([evaluation, task, changelog2])
    session.commit()
    
    # Step 4: Developer locks and starts work
    task.locked_by_id = frontend_dev.id
    task.locked_at = datetime.utcnow()
    task.status = TaskStatus.UNDER_WORK
    changelog3 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.APPROVED,
        new_status=TaskStatus.UNDER_WORK,
        changed_by=frontend_dev.agent_id
    )
    session.add_all([task, changelog3])
    session.commit()
    
    # Step 5: Developer completes work
    task.status = TaskStatus.DEV_DONE
    task.locked_by_id = None  # Release lock
    task.locked_at = None
    changelog4 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.UNDER_WORK,
        new_status=TaskStatus.DEV_DONE,
        changed_by=frontend_dev.agent_id,
        notes="Component implemented and tested locally"
    )
    session.add_all([task, changelog4])
    session.commit()
    
    # Step 6: QA testing
    task.status = TaskStatus.QA_DONE
    changelog5 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.DEV_DONE,
        new_status=TaskStatus.QA_DONE,
        changed_by=qa.agent_id,
        notes="All tests passing"
    )
    session.add_all([task, changelog5])
    session.commit()
    
    # Step 7: Documentation
    task.status = TaskStatus.DOCUMENTATION_DONE
    changelog6 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.QA_DONE,
        new_status=TaskStatus.DOCUMENTATION_DONE,
        changed_by=frontend_dev.agent_id
    )
    session.add_all([task, changelog6])
    session.commit()
    
    # Step 8: Commit
    task.status = TaskStatus.COMMITTED
    changelog7 = Changelog(
        task_id=task.id,
        old_status=TaskStatus.DOCUMENTATION_DONE,
        new_status=TaskStatus.COMMITTED,
        changed_by=frontend_dev.agent_id,
        notes="Merged to main branch"
    )
    session.add_all([task, changelog7])
    session.commit()
    
    # Verify final state
    final_task = session.get(Task, task.id)
    assert final_task.status == TaskStatus.COMMITTED
    assert final_task.locked_by_id is None
    
    # Verify changelog
    changelogs = session.exec(
        select(Changelog).where(Changelog.task_id == task.id)
    ).all()
    assert len(changelogs) == 7
    
    # Verify evaluation
    evaluations = session.exec(
        select(TaskEvaluation).where(TaskEvaluation.task_id == task.id)
    ).all()
    assert len(evaluations) == 1
    assert evaluations[0].approved is True

def test_task_rejection_flow(session: Session, sample_data):
    """Test task rejection during evaluation"""
    task = sample_data["tasks"][1]
    pm = Agent(
        agent_id="pm_principal_001",
        role=AgentRole.PM,
        level=DifficultyLevel.PRINCIPAL
    )
    session.add(pm)
    session.commit()
    
    # Move to evaluation
    task.status = TaskStatus.EVALUATION
    session.add(task)
    session.commit()
    
    # Reject the task
    evaluation = TaskEvaluation(
        task_id=task.id,
        evaluated_by=pm.agent_id,
        approved=False,
        comment="Need more detailed requirements"
    )
    task.status = TaskStatus.CREATED  # Back to created
    task.notes = "Rejected: Need more detailed requirements"
    
    changelog = Changelog(
        task_id=task.id,
        old_status=TaskStatus.EVALUATION,
        new_status=TaskStatus.CREATED,
        changed_by=pm.agent_id,
        notes="Task rejected"
    )
    
    session.add_all([evaluation, task, changelog])
    session.commit()
    
    # Verify rejection
    rejected_task = session.get(Task, task.id)
    assert rejected_task.status == TaskStatus.CREATED
    assert "Rejected" in rejected_task.notes
    
    evaluations = session.exec(
        select(TaskEvaluation).where(TaskEvaluation.task_id == task.id)
    ).all()
    assert len(evaluations) == 1
    assert evaluations[0].approved is False

def test_lock_prevents_duplicate_work(session: Session, sample_data):
    """Test that locked tasks cannot be picked up by other agents"""
    task = sample_data["tasks"][0]
    frontend_dev1 = sample_data["agents"]["frontend_dev"]
    
    # Create another frontend developer
    frontend_dev2 = Agent(
        agent_id="frontend_dev_senior_002",
        role=AgentRole.FRONTEND_DEV,
        level=DifficultyLevel.SENIOR
    )
    session.add(frontend_dev2)
    session.commit()
    
    # First developer locks the task
    task.status = TaskStatus.APPROVED
    task.locked_by_id = frontend_dev1.id
    task.locked_at = datetime.utcnow()
    session.add(task)
    session.commit()
    
    # Query for available tasks (should exclude locked ones)
    available_tasks = session.exec(
        select(Task).where(
            Task.status == TaskStatus.APPROVED,
            Task.target_role == AgentRole.FRONTEND_DEV,
            Task.locked_by_id.is_(None)
        )
    ).all()
    
    assert len(available_tasks) == 0  # Task is locked

def test_auto_unlock_on_status_change(session: Session, sample_data):
    """Test that lock is released when task moves from UNDER_WORK"""
    task = sample_data["tasks"][0]
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Lock and start work
    task.status = TaskStatus.UNDER_WORK
    task.locked_by_id = backend_dev.id
    task.locked_at = datetime.utcnow()
    session.add(task)
    session.commit()
    
    # Complete work (should release lock)
    task.status = TaskStatus.DEV_DONE
    task.locked_by_id = None
    task.locked_at = None
    session.add(task)
    session.commit()
    
    # Verify lock is released
    updated_task = session.get(Task, task.id)
    assert updated_task.locked_by_id is None
    assert updated_task.locked_at is None

def test_skill_level_filtering(session: Session, sample_data):
    """Test that agents only see tasks at or below their skill level"""
    feature = sample_data["feature"]
    architect = sample_data["agents"]["architect"]
    
    # Create tasks of different difficulty levels
    junior_task = Task(
        feature_id=feature.id,
        title="Fix button color",
        description="Change button from blue to green",
        created_by_id=architect.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.JUNIOR,
        branch="fix/button-color",
        status=TaskStatus.APPROVED
    )
    
    senior_task = Task(
        feature_id=feature.id,
        title="Implement state management",
        description="Add Redux for form state",
        created_by_id=architect.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.SENIOR,
        branch="feature/redux-state",
        status=TaskStatus.APPROVED
    )
    
    principal_task = Task(
        feature_id=feature.id,
        title="Architect micro-frontend",
        description="Design micro-frontend architecture",
        created_by_id=architect.id,
        target_role=AgentRole.FRONTEND_DEV,
        difficulty=DifficultyLevel.PRINCIPAL,
        branch="feature/micro-frontend",
        status=TaskStatus.APPROVED
    )
    
    session.add_all([junior_task, senior_task, principal_task])
    session.commit()
    
    # Junior developer can only see junior tasks
    junior_tasks = session.exec(
        select(Task).where(
            Task.target_role == AgentRole.FRONTEND_DEV,
            Task.difficulty == DifficultyLevel.JUNIOR,
            Task.status == TaskStatus.APPROVED
        )
    ).all()
    assert len(junior_tasks) == 1
    
    # Senior developer can see junior and senior tasks
    senior_level_tasks = session.exec(
        select(Task).where(
            Task.target_role == AgentRole.FRONTEND_DEV,
            Task.difficulty.in_([DifficultyLevel.JUNIOR, DifficultyLevel.SENIOR]),
            Task.status == TaskStatus.APPROVED
        )
    ).all()
    assert len(senior_level_tasks) == 2