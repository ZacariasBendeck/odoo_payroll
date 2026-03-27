"""WhatsApp Business API integration service.

This is a webhook-based integration stub. To activate:
1. Set WHATSAPP_API_TOKEN and WHATSAPP_VERIFY_TOKEN in .env
2. Register the webhook URL (/api/whatsapp/webhook) with Meta Business API
3. The incoming message handler will extract text and pass it to AI for action items
"""

import logging
from dataclasses import dataclass

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

WHATSAPP_API_BASE = "https://graph.facebook.com/v18.0"


@dataclass
class WhatsAppMessage:
    sender_phone: str
    sender_name: str
    text: str
    timestamp: str
    message_id: str


def verify_webhook(mode: str, token: str, challenge: str) -> str | None:
    """Verify the webhook with Meta's challenge-response."""
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        return challenge
    return None


def parse_incoming(payload: dict) -> list[WhatsAppMessage]:
    """Parse incoming webhook payload into messages."""
    messages = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") == "text":
                    contact = value.get("contacts", [{}])[0]
                    messages.append(
                        WhatsAppMessage(
                            sender_phone=msg.get("from", ""),
                            sender_name=contact.get("profile", {}).get("name", ""),
                            text=msg.get("text", {}).get("body", ""),
                            timestamp=msg.get("timestamp", ""),
                            message_id=msg.get("id", ""),
                        )
                    )
    return messages


def send_message(phone: str, text: str) -> bool:
    """Send a WhatsApp message (requires configured API token)."""
    if not settings.whatsapp_api_token or not settings.whatsapp_phone_number_id:
        logger.warning("WhatsApp not configured. Set WHATSAPP_API_TOKEN in .env")
        return False

    url = f"{WHATSAPP_API_BASE}/{settings.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_api_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }

    try:
        resp = httpx.post(url, json=data, headers=headers, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False
