import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.models.models import Document, Mention, Agent
from src.models.document_enums import DocumentType
from src.services.mention_service import extract_mentions

def test_extract_mentions():
    """Test mention extraction from text"""
    text = "Hey @frontend_dev_senior_001, can you check this? @backend_dev_junior_001 FYI"
    mentions = extract_mentions(text)
    assert mentions == {"frontend_dev_senior_001", "backend_dev_junior_001"}
    
    # Test with no mentions
    text = "This is a regular message without mentions"
    mentions = extract_mentions(text)
    assert mentions == set()
    
    # Test with duplicate mentions
    text = "@qa_senior_001 please test this. @qa_senior_001 thanks!"
    mentions = extract_mentions(text)
    assert mentions == {"qa_senior_001"}

def test_document_creation(session: Session, sample_data):
    """Test creating a document"""
    architect = sample_data["agents"]["architect"]
    
    doc = Document(
        doc_type=DocumentType.STANDUP,
        author_id=architect.agent_id,
        title="Daily Standup - Architect",
        content="## Today\n- Reviewed API design\n- Created new tasks\n\n## Tomorrow\n- Review PR",
        meta_data={"mood": "productive"}
    )
    session.add(doc)
    session.commit()
    
    saved_doc = session.get(Document, doc.id)
    assert saved_doc.doc_type == DocumentType.STANDUP
    assert saved_doc.author_id == "architect_principal_001"
    assert saved_doc.title == "Daily Standup - Architect"
    assert "Review PR" in saved_doc.content
    assert saved_doc.meta_data["mood"] == "productive"

def test_document_with_mentions(session: Session, sample_data):
    """Test document with mentions creates mention records"""
    architect = sample_data["agents"]["architect"]
    frontend_dev = sample_data["agents"]["frontend_dev"]
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create document with mentions
    doc = Document(
        doc_type=DocumentType.CRITICAL_ISSUE,
        author_id=architect.agent_id,
        title="API Service Down",
        content="The API is down! @frontend_dev_senior_001 @backend_dev_junior_001 please investigate immediately."
    )
    session.add(doc)
    session.commit()
    
    # Create mentions manually (in real app, this would be done by the API)
    from src.services.mention_service import create_mentions_for_document
    mentions = create_mentions_for_document(
        session, doc.id, doc.content, architect.agent_id
    )
    session.commit()
    
    # Verify mentions were created
    saved_mentions = session.exec(
        select(Mention).where(Mention.document_id == doc.id)
    ).all()
    assert len(saved_mentions) == 2
    
    mentioned_agents = {m.mentioned_agent_id for m in saved_mentions}
    assert mentioned_agents == {"frontend_dev_senior_001", "backend_dev_junior_001"}
    
    # Check all mentions are unread
    for mention in saved_mentions:
        assert mention.is_read is False
        assert mention.created_by == architect.agent_id

def test_document_expiration(session: Session, sample_data):
    """Test document with expiration date"""
    qa = sample_data["agents"]["qa"]
    
    # Create document that expires in 1 hour
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    doc = Document(
        doc_type=DocumentType.SERVICE_STATUS,
        author_id=qa.agent_id,
        title="Test Environment Status",
        content="Test environment is up and running on port 3000",
        expires_at=expiry_time
    )
    session.add(doc)
    session.commit()
    
    saved_doc = session.get(Document, doc.id)
    assert saved_doc.expires_at is not None
    assert saved_doc.expires_at > datetime.utcnow()

def test_document_update(session: Session, sample_data):
    """Test updating a document"""
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create initial document
    doc = Document(
        doc_type=DocumentType.UPDATE,
        author_id=backend_dev.agent_id,
        title="Backend Progress Update",
        content="Started working on authentication"
    )
    session.add(doc)
    session.commit()
    
    original_created_at = doc.created_at
    
    # Update document
    doc.content = "Started working on authentication\n\nUpdate: JWT implementation complete"
    doc.updated_at = datetime.utcnow()
    session.add(doc)
    session.commit()
    
    # Verify update
    updated_doc = session.get(Document, doc.id)
    assert "JWT implementation complete" in updated_doc.content
    assert updated_doc.created_at == original_created_at
    assert updated_doc.updated_at > updated_doc.created_at

def test_document_types(session: Session, sample_data):
    """Test different document types"""
    frontend_dev = sample_data["agents"]["frontend_dev"]
    
    # Create documents of each type
    doc_types = [
        (DocumentType.STANDUP, "Daily Standup"),
        (DocumentType.CRITICAL_ISSUE, "Build Failed"),
        (DocumentType.SERVICE_STATUS, "Frontend Service Status"),
        (DocumentType.UPDATE, "General Update")
    ]
    
    for doc_type, title in doc_types:
        doc = Document(
            doc_type=doc_type,
            author_id=frontend_dev.agent_id,
            title=title,
            content=f"Content for {doc_type.value}"
        )
        session.add(doc)
    
    session.commit()
    
    # Query by document type
    standup_docs = session.exec(
        select(Document).where(Document.doc_type == DocumentType.STANDUP)
    ).all()
    assert any(d.title == "Daily Standup" for d in standup_docs)
    
    critical_docs = session.exec(
        select(Document).where(Document.doc_type == DocumentType.CRITICAL_ISSUE)
    ).all()
    assert any(d.title == "Build Failed" for d in critical_docs)

def test_document_meta_data(session: Session, sample_data):
    """Test document meta_data storage"""
    qa = sample_data["agents"]["qa"]
    
    meta_data = {
        "test_results": {
            "passed": 45,
            "failed": 2,
            "skipped": 3
        },
        "duration": "2m 35s",
        "environment": "staging"
    }
    
    doc = Document(
        doc_type=DocumentType.UPDATE,
        author_id=qa.agent_id,
        title="Test Results Summary",
        content="Test run completed with 2 failures",
        meta_data=meta_data
    )
    session.add(doc)
    session.commit()
    
    saved_doc = session.get(Document, doc.id)
    assert saved_doc.meta_data["test_results"]["passed"] == 45
    assert saved_doc.meta_data["test_results"]["failed"] == 2
    assert saved_doc.meta_data["environment"] == "staging"