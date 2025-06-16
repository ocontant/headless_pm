import pytest
from sqlmodel import Session
from src.services.mention_service import (
    extract_mentions, 
    create_mentions_for_document,
    create_mentions_for_task
)
from src.models.models import Document, Task, Mention, Agent, Epic, Feature
from src.models.enums import AgentRole, DifficultyLevel
from src.models.document_enums import DocumentType

def test_extract_mentions_single():
    """Test extracting a single mention"""
    text = "Hey @frontend_dev_senior_001, can you check this?"
    mentions = extract_mentions(text)
    assert mentions == {"frontend_dev_senior_001"}

def test_extract_mentions_multiple():
    """Test extracting multiple mentions"""
    text = "Hey @frontend_dev_senior_001 and @backend_dev_junior_001, please review"
    mentions = extract_mentions(text)
    assert mentions == {"frontend_dev_senior_001", "backend_dev_junior_001"}

def test_extract_mentions_none():
    """Test extracting mentions when there are none"""
    text = "This is a regular message without any mentions"
    mentions = extract_mentions(text)
    assert mentions == set()

def test_extract_mentions_duplicates():
    """Test extracting mentions with duplicates"""
    text = "@qa_senior_001 please test this. @qa_senior_001 thanks!"
    mentions = extract_mentions(text)
    assert mentions == {"qa_senior_001"}

def test_extract_mentions_complex_patterns():
    """Test extracting mentions with various patterns"""
    text = "Contact @user_123, @test_agent_001, and @simple for help"
    mentions = extract_mentions(text)
    assert mentions == {"user_123", "test_agent_001", "simple"}

def test_extract_mentions_with_punctuation():
    """Test extracting mentions surrounded by punctuation"""
    text = "(@frontend_dev_001) and [@backend_dev_002], also @qa_003."
    mentions = extract_mentions(text)
    assert mentions == {"frontend_dev_001", "backend_dev_002", "qa_003"}

def test_create_mentions_for_document(session: Session, sample_data):
    """Test creating mentions for a document"""
    # Create a document
    doc = Document(
        doc_type=DocumentType.UPDATE,
        author_id="test_author",
        title="Test Document",
        content="Hey @frontend_dev_senior_001, please review this @backend_dev_junior_001"
    )
    session.add(doc)
    session.commit()
    
    # Create mentions
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, "test_author"
    )
    session.commit()
    
    # Verify mentions were created
    assert len(mentions) == 2
    mentioned_agents = {m.mentioned_agent_id for m in mentions}
    assert mentioned_agents == {"frontend_dev_senior_001", "backend_dev_junior_001"}
    
    # Verify all mentions have correct properties
    for mention in mentions:
        assert mention.document_id == doc.id
        assert mention.task_id is None
        assert mention.created_by == "test_author"
        assert mention.is_read is False

def test_create_mentions_for_task(session: Session, sample_data):
    """Test creating mentions for a task"""
    task = sample_data["tasks"][0]
    
    # Create mentions from task comment
    comment = "Tests are failing @frontend_dev_senior_001, also @qa_senior_001 please help"
    mentions = create_mentions_for_task(
        session, task.id, comment, "test_commenter"
    )
    session.commit()
    
    # Verify mentions were created
    assert len(mentions) == 2
    mentioned_agents = {m.mentioned_agent_id for m in mentions}
    assert mentioned_agents == {"frontend_dev_senior_001", "qa_senior_001"}
    
    # Verify all mentions have correct properties
    for mention in mentions:
        assert mention.task_id == task.id
        assert mention.document_id is None
        assert mention.created_by == "test_commenter"
        assert mention.is_read is False

def test_create_mentions_no_mentions(session: Session, sample_data):
    """Test creating mentions when text has no mentions"""
    task = sample_data["tasks"][0]
    
    # Create mentions from text with no mentions
    comment = "This is a regular comment without any mentions"
    mentions = create_mentions_for_task(
        session, task.id, comment, "test_commenter"
    )
    session.commit()
    
    # Verify no mentions were created
    assert len(mentions) == 0

def test_create_mentions_empty_text(session: Session, sample_data):
    """Test creating mentions from empty text"""
    task = sample_data["tasks"][0]
    
    # Create mentions from empty text
    mentions = create_mentions_for_task(
        session, task.id, "", "test_commenter"
    )
    session.commit()
    
    # Verify no mentions were created
    assert len(mentions) == 0