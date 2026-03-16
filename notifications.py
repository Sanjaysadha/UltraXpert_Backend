"""
notifications.py – All notification REST endpoints.

Route ordering matters in FastAPI — fixed/named routes must come BEFORE
parameterized ones to avoid mismatching (e.g., /read-all vs /{id}/read).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api import dependencies
import models, schemas

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────────────
# GET  /notifications/          →  list all (sorted newest first)
# ──────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[schemas.Notification])
def get_notifications(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    notifications = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .all()
    )
    return notifications


# ──────────────────────────────────────────────────────────────────────────────
# POST /notifications/          →  create a notification (manual / admin)
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.Notification, status_code=status.HTTP_201_CREATED)
def create_notification(
    notif_in: schemas.NotificationCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    db_obj = models.Notification(**notif_in.dict(), user_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /notifications/read-all →  mark ALL as read   ← BEFORE /{id}/read
# ──────────────────────────────────────────────────────────────────────────────
@router.patch("/read-all", response_model=dict)
def mark_all_read(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    updated = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == current_user.id,
            models.Notification.is_read == False,   # noqa: E712
        )
        .update({"is_read": True})
    )
    db.commit()
    return {"updated": updated}


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /notifications/  →  delete all (Alternative for frontend convenience)
# ──────────────────────────────────────────────────────────────────────────────
@router.delete("/", status_code=status.HTTP_200_OK)
@router.delete("/clear-all", status_code=status.HTTP_200_OK)
def clear_all_notifications(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    deleted = (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .delete()
    )
    db.commit()
    # Return an empty list or success indicator to ensure frontend clears its state
    return {"deleted": deleted, "notifications": []}


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /notifications/{id}/read  →  mark single as read
# ──────────────────────────────────────────────────────────────────────────────
@router.patch("/{notification_id}/read", response_model=schemas.Notification)
def mark_as_read(
    notification_id: str,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    notif = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /notifications/{id}   →  delete single notification
# ──────────────────────────────────────────────────────────────────────────────
@router.delete("/{notification_id}", status_code=status.HTTP_200_OK)
def delete_notification(
    notification_id: str,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    notif = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"deleted": notification_id}
