import logging

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.integration import ActionItem
from app.services import ai_service, project_service, whatsapp_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """Meta webhook verification endpoint."""
    result = whatsapp_service.verify_webhook(hub_mode, hub_token, hub_challenge)
    if result:
        return Response(content=result, media_type="text/plain")
    return Response(status_code=403, content="Verification failed")


@router.post("/webhook")
def receive_webhook(payload: dict, db: Session = Depends(get_db)):
    """Handle incoming WhatsApp messages."""
    messages = whatsapp_service.parse_incoming(payload)

    if not messages:
        return {"status": "ok", "processed": 0}

    projects = project_service.list_projects(db)
    projects_data = [{"id": p.id, "name": p.name, "description": p.description} for p in projects]

    for msg in messages:
        text = f"From {msg.sender_name} ({msg.sender_phone}): {msg.text}"
        try:
            actions = ai_service.extract_action_items(text, projects_data)
        except Exception as e:
            logger.error(f"Failed to extract actions from WhatsApp: {e}")
            continue

        for action in actions:
            item = ActionItem(
                source="whatsapp",
                source_ref=msg.message_id,
                content=text[:500],
                extracted_action=action.get("action", ""),
                status="pending",
            )
            db.add(item)

    db.commit()
    return {"status": "ok", "processed": len(messages)}
