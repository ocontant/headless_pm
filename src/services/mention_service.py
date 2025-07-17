import re
from typing import List, Set
from sqlmodel import Session
from src.models.models import Mention

def extract_mentions(text: str) -> Set[str]:
    """Extract @mentions from text. Returns set of mentioned agent_ids."""
    # Match @word_word_word pattern (e.g., @frontend_dev_senior_001)
    pattern = r'@([a-zA-Z0-9_]+(?:_[a-zA-Z0-9_]+)*)'
    mentions = re.findall(pattern, text)
    return set(mentions)

def create_mentions_for_document(
    db: Session,
    document_id: int,
    content: str,
    created_by: str,
    project_id: int
) -> List[Mention]:
    """Create mention records for all @mentions in document content."""
    mentioned_agents = extract_mentions(content)
    mentions = []
    
    for agent_id in mentioned_agents:
        mention = Mention(
            project_id=project_id,
            document_id=document_id,
            mentioned_agent_id=agent_id,
            created_by=created_by
        )
        db.add(mention)
        mentions.append(mention)
    
    return mentions

def create_mentions_for_task(
    db: Session,
    task_id: int,
    content: str,
    created_by: str,
    project_id: int
) -> List[Mention]:
    """Create mention records for all @mentions in task content."""
    mentioned_agents = extract_mentions(content)
    mentions = []
    
    for agent_id in mentioned_agents:
        mention = Mention(
            project_id=project_id,
            task_id=task_id,
            mentioned_agent_id=agent_id,
            created_by=created_by
        )
        db.add(mention)
        mentions.append(mention)
    
    return mentions