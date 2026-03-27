import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.integration import ActionItem
from app.schemas.integration import ActionItemResponse, EmailSyncRequest, EmailSyncResponse
from app.services import ai_service, email_service, project_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/sync", response_model=EmailSyncResponse)
def sync_emails(data: EmailSyncRequest, db: Session = Depends(get_db)):
    """Fetch unread emails, extract action items via AI, and store them."""
    emails = email_service.fetch_unread(max_emails=data.max_emails)

    if not emails:
        return EmailSyncResponse(synced=0, action_items_created=0)

    projects = project_service.list_projects(db)
    projects_data = [{"id": p.id, "name": p.name, "description": p.description} for p in projects]

    action_count = 0
    for msg in emails:
        text = f"Subject: {msg.subject}\nFrom: {msg.sender}\n\n{msg.body}"
        try:
            actions = ai_service.extract_action_items(text, projects_data)
        except Exception as e:
            logger.error(f"Failed to extract actions from email: {e}")
            continue

        for action in actions:
            item = ActionItem(
                source="email",
                source_ref=msg.message_id,
                content=text[:500],
                extracted_action=action.get("action", ""),
                status="pending",
            )
            db.add(item)
            action_count += 1

    db.commit()
    return EmailSyncResponse(synced=len(emails), action_items_created=action_count)


@router.get("/action-items", response_model=list[ActionItemResponse])
def list_action_items(
    status: str | None = None,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(ActionItem)
    if status:
        q = q.filter(ActionItem.status == status)
    if source:
        q = q.filter(ActionItem.source == source)
    return [ActionItemResponse.model_validate(i) for i in q.order_by(ActionItem.created_at.desc()).all()]
