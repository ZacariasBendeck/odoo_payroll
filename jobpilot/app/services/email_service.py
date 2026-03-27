"""Email integration service.

Provides IMAP email fetching and AI-powered action item extraction.
Configure via .env: IMAP_SERVER, IMAP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD
"""

import email
import imaplib
import logging
from dataclasses import dataclass
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    subject: str
    sender: str
    body: str
    date: datetime | None
    message_id: str


def connect() -> imaplib.IMAP4_SSL | None:
    """Connect to the configured IMAP server."""
    if not settings.imap_server or not settings.email_address:
        logger.warning("Email not configured. Set IMAP_SERVER and EMAIL_ADDRESS in .env")
        return None
    try:
        mail = imaplib.IMAP4_SSL(settings.imap_server, settings.imap_port)
        mail.login(settings.email_address, settings.email_password)
        return mail
    except Exception as e:
        logger.error(f"Failed to connect to email: {e}")
        return None


def fetch_unread(max_emails: int = 20) -> list[EmailMessage]:
    """Fetch unread emails from the inbox."""
    mail = connect()
    if not mail:
        return []

    messages = []
    try:
        mail.select("INBOX")
        _, data = mail.search(None, "UNSEEN")
        email_ids = data[0].split()[-max_emails:] if data[0] else []

        for eid in email_ids:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            if msg_data[0] is None:
                continue
            msg = email.message_from_bytes(msg_data[0][1])

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="replace")

            messages.append(
                EmailMessage(
                    subject=msg.get("Subject", ""),
                    sender=msg.get("From", ""),
                    body=body[:2000],  # limit body size
                    date=None,
                    message_id=msg.get("Message-ID", ""),
                )
            )
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")
    finally:
        try:
            mail.logout()
        except Exception:
            pass

    return messages
