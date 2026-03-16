import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import dependencies
from core.notify import push_notification
import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Appointment])
def read_appointments(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    appointments = (
        db.query(models.Appointment)
        .filter(models.Appointment.doctor_id == current_user.id)
        .all()
    )
    return appointments


@router.post("/", response_model=schemas.Appointment)
def create_appointment(
    appt_in: schemas.AppointmentCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    appt_data = appt_in.dict()

    # ── Derive scheduled_at DateTime from the time string if not provided ──
    # If the iOS app sends a scheduled_at ISO datetime, use it.
    # Otherwise, try to parse the time string and use today's date.
    if not appt_data.get("scheduled_at") and appt_data.get("time"):
        try:
            time_str = appt_data["time"]  # e.g. "10:25 AM"
            today = datetime.date.today()
            t = datetime.datetime.strptime(time_str, "%I:%M %p")
            appt_data["scheduled_at"] = datetime.datetime.combine(today, t.time())
        except Exception:
            appt_data["scheduled_at"] = None

    db_obj = models.Appointment(**appt_data, doctor_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 🔔 Notification: Appointment scheduled
    push_notification(
        db=db,
        user_id=current_user.id,
        title="📅 Appointment Scheduled",
        message=(
            f"New {appt_in.type or 'appointment'} has been scheduled for "
            f"{appt_in.time or 'today'} in {appt_in.room or 'Room TBD'}. "
            f"You'll receive a reminder 30 minutes before."
        ),
        icon="calendar.badge.plus",
        type="appointment_scheduled",
    )

    return db_obj
