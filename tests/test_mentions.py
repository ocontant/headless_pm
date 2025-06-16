import pytest
from datetime import datetime
from sqlmodel import Session, select
from src.models.models import Mention, Document, Task, Agent
from src.models.document_enums import DocumentType
from src.services.mention_service import create_mentions_for_document, create_mentions_for_task

def test_mention_in_document(session: Session, sample_data):
    """Test creating mentions in a document"""
    architect = sample_data["agents"]["architect"]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    
    # Create document with mention
    doc = Document(
        doc_type=DocumentType.CRITICAL_ISSUE,
        author_id=architect.agent_id,
        title="UI Bug Found",
        content="There's a critical bug in the login form @frontend_dev_senior_001"
    )
    session.add(doc)
    session.commit()
    
    # Create mentions
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, architect.agent_id
    )
    session.commit()
    
    # Verify mention
    assert len(mentions) == 1
    mention = mentions[0]
    assert mention.mentioned_agent_id == "frontend_dev_senior_001"
    assert mention.created_by == architect.agent_id
    assert mention.document_id == doc.id
    assert mention.task_id is None
    assert mention.is_read is False

def test_mention_in_task_comment(session: Session, sample_data):
    """Test creating mentions in task comments"""
    task = sample_data["tasks"][0]
    qa = sample_data["agents"]["qa"]
    
    # Add comment with mention
    comment = "Tests are failing @frontend_dev_senior_001, please fix"
    
    # Create mentions
    mentions = create_mentions_for_task(
        session, task.id, comment, qa.agent_id
    )
    session.commit()
    
    # Verify mention
    assert len(mentions) == 1
    mention = mentions[0]
    assert mention.mentioned_agent_id == "frontend_dev_senior_001"
    assert mention.created_by == qa.agent_id
    assert mention.task_id == task.id
    assert mention.document_id is None

def test_multiple_mentions(session: Session, sample_data):
    """Test multiple mentions in one document"""
    pm = Agent(
        agent_id="pm_principal_001",
        role="pm",
        level="principal"
    )
    session.add(pm)
    session.commit()
    
    # Create document with multiple mentions
    doc = Document(
        doc_type=DocumentType.UPDATE,
        author_id=pm.agent_id,
        title="Team Update",
        content="Great work team! @frontend_dev_senior_001 finished the UI, "
                "@backend_dev_junior_001 fixed the API, and @qa_senior_001 "
                "completed testing. @architect_principal_001 please review."
    )
    session.add(doc)
    session.commit()
    
    # Create mentions
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, pm.agent_id
    )
    session.commit()
    
    # Verify all mentions
    assert len(mentions) == 4
    mentioned_ids = {m.mentioned_agent_id for m in mentions}
    expected_ids = {
        "frontend_dev_senior_001",
        "backend_dev_junior_001",
        "qa_senior_001",
        "architect_principal_001"
    }
    assert mentioned_ids == expected_ids

def test_mention_read_status(session: Session, sample_data):
    """Test marking mentions as read"""
    architect = sample_data["agents"]["architect"]
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create document with mention
    doc = Document(
        doc_type=DocumentType.CRITICAL_ISSUE,
        author_id=architect.agent_id,
        title="Database Issue",
        content="Database connection failing @backend_dev_junior_001"
    )
    session.add(doc)
    session.commit()
    
    # Create mention
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, architect.agent_id
    )
    session.commit()
    
    mention = mentions[0]
    assert mention.is_read is False
    
    # Mark as read
    mention.is_read = True
    session.add(mention)
    session.commit()
    
    # Verify read status
    updated_mention = session.get(Mention, mention.id)
    assert updated_mention.is_read is True

def test_query_mentions_for_agent(session: Session, sample_data):
    """Test querying all mentions for a specific agent"""
    architect = sample_data["agents"]["architect"]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    qa = sample_data["agents"]["qa"]
    
    # Create multiple documents mentioning frontend_dev
    docs = [
        Document(
            doc_type=DocumentType.UPDATE,
            author_id=architect.agent_id,
            title="Architecture Review",
            content="@frontend_dev_senior_001 please implement the new design"
        ),
        Document(
            doc_type=DocumentType.CRITICAL_ISSUE,
            author_id=qa.agent_id,
            title="UI Test Failure",
            content="Login button test failing @frontend_dev_senior_001"
        )
    ]
    
    for doc in docs:
        session.add(doc)
        session.commit()
        create_mentions_for_document(session, doc.id, doc.content, doc.author_id)
    
    session.commit()
    
    # Query all mentions for frontend_dev
    frontend_mentions = session.exec(
        select(Mention).where(
            Mention.mentioned_agent_id == "frontend_dev_senior_001"
        )
    ).all()
    
    assert len(frontend_mentions) >= 2
    
    # Query unread mentions only
    unread_mentions = session.exec(
        select(Mention).where(
            Mention.mentioned_agent_id == "frontend_dev_senior_001",
            Mention.is_read == False
        )
    ).all()
    
    assert len(unread_mentions) >= 2

def test_no_self_mention(session: Session, sample_data):
    """Test that self-mentions are still created (agents might want to bookmark)"""
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create document where author mentions themselves
    doc = Document(
        doc_type=DocumentType.UPDATE,
        author_id=backend_dev.agent_id,
        title="Note to Self",
        content="Remember to check this later @backend_dev_junior_001"
    )
    session.add(doc)
    session.commit()
    
    # Create mentions
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, backend_dev.agent_id
    )
    session.commit()
    
    # Self-mentions are created
    assert len(mentions) == 1
    assert mentions[0].mentioned_agent_id == backend_dev.agent_id
    assert mentions[0].created_by == backend_dev.agent_id