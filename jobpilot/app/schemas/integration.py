from datetime import datetime

from pydantic import BaseModel


class ActionItemResponse(BaseModel):
    id: int
    source: str
    source_ref: str | None
    content: str
    extracted_action: str
    project_id: int | None
    task_id: int | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailSyncRequest(BaseModel):
    max_emails: int = 20


class EmailSyncResponse(BaseModel):
    synced: int
    action_items_created: int


class WhatsAppWebhookPayload(BaseModel):
    entry: list[dict] = []
