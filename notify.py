"""
notify.py – Shared helper to create in-app notifications from anywhere in the backend.

Usage:
    from core.notify import push_notification
    push_notification(db, user_id="...", title="...", message="...", icon="...", type="...")
"""

import uuid
import datetime
from sqlalchemy.orm import Session
from models.notification import Notification


def push_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    icon: str = "bell.fill",
    type: str = "general",
    file_url: str = None,
) -> Notification:
    """Create and persist a notification for a user."""
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        message=message,
        icon=icon,
        type=type,
        is_read=False,
        file_url=file_url,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    print(f"DEBUG: Notification added to DB: {notif.title} - User: {notif.user_id} - FileURL: {notif.file_url}")
    return notif
