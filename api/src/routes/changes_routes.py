from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from shared.models.database import get_session
from shared.models.models import Document, Task, Service, Mention, Changelog, Feature, Epic
from shared.schemas.dependencies import verify_api_key

router = APIRouter(prefix="/api/v1", tags=["Changes"], dependencies=[Depends(verify_api_key)])

class ChangeEvent(BaseModel):
    type: str  # document_created, task_updated, service_updated, new_mention
    timestamp: datetime
    data: Dict[str, Any]

class ChangesResponse(BaseModel):
    changes: List[ChangeEvent]
    last_timestamp: datetime

@router.get("/changes", response_model=ChangesResponse,
    summary="Poll for changes",
    description="Get all changes since a given timestamp for efficient polling")
def get_changes(
    since: datetime = Query(..., description="Get changes after this timestamp"),
    agent_id: str = Query(..., description="Agent ID requesting changes"),
    project_id: int = Query(..., description="Project ID to filter changes"),
    db: Session = Depends(get_session)
):
    try:
        changes = []
        latest_timestamp = since
        
        # Check for new documents
        new_documents = db.exec(
            select(Document).where(
                Document.created_at > since,
                Document.project_id == project_id
            ).order_by(Document.created_at)
        ).all()
        
        for doc in new_documents:
            changes.append(ChangeEvent(
                type="document_created",
                timestamp=doc.created_at,
                data={
                    "document_id": doc.id,
                    "doc_type": doc.doc_type.value,
                    "title": doc.title,
                    "author_id": doc.author_id
                }
            ))
            if doc.created_at > latest_timestamp:
                latest_timestamp = doc.created_at
        
        # Check for updated documents
        updated_documents = db.exec(
            select(Document).where(
                Document.updated_at > since,
                Document.updated_at != Document.created_at,  # Exclude newly created
                Document.project_id == project_id
            ).order_by(Document.updated_at)
        ).all()
        
        for doc in updated_documents:
            changes.append(ChangeEvent(
                type="document_updated",
                timestamp=doc.updated_at,
                data={
                    "document_id": doc.id,
                    "doc_type": doc.doc_type.value,
                    "title": doc.title,
                    "author_id": doc.author_id
                }
            ))
            if doc.updated_at > latest_timestamp:
                latest_timestamp = doc.updated_at
        
        # Check for task status changes via changelog (filtered by project)
        task_changes = db.exec(
            select(Changelog)
            .join(Task, Changelog.task_id == Task.id)
            .join(Feature, Task.feature_id == Feature.id)
            .join(Epic, Feature.epic_id == Epic.id)
            .where(
                Changelog.changed_at > since,
                Epic.project_id == project_id
            )
            .order_by(Changelog.changed_at)
        ).all()
        
        for changelog in task_changes:
            task = db.get(Task, changelog.task_id)
            if task:
                changes.append(ChangeEvent(
                    type="task_updated",
                    timestamp=changelog.changed_at,
                    data={
                        "task_id": task.id,
                        "title": task.title,
                        "old_status": changelog.old_status.value,
                        "new_status": changelog.new_status.value,
                        "changed_by": changelog.changed_by,
                        "notes": changelog.notes
                    }
                ))
            if changelog.changed_at > latest_timestamp:
                latest_timestamp = changelog.changed_at
        
        # Sort all changes by timestamp
        changes.sort(key=lambda x: x.timestamp)
        
        return ChangesResponse(
            changes=changes,
            last_timestamp=latest_timestamp
        )
    except Exception as e:
        # Return empty changes on error
        return ChangesResponse(
            changes=[],
            last_timestamp=since
        )