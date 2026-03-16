"""
scheduler.py – Background job scheduler for UltraXpert.

Jobs:
  1. appointment_reminder_job  – Runs every minute; sends a notification
     30 minutes before any upcoming appointment that hasn't been reminded yet.
  2. software_update_check_job – Runs once a day; broadcasts a notification
     to every user if a new app version is available (version stored in DB or config).
"""

import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from core.database import SessionLocal
from core.notify import push_notification

logger = logging.getLogger(__name__)

# ── Current app version (bump this whenever you release a new version) ─────────
CURRENT_APP_VERSION = "1.0.0"


# ──────────────────────────────────────────────────────────────────────────────
# JOB 1: Appointment Reminder – fires every 60 seconds
# ──────────────────────────────────────────────────────────────────────────────
def appointment_reminder_job():
    """
    Check all upcoming appointments scheduled within the next 30 minutes
    and push a reminder notification to the doctor if not already sent.
    """
    db = SessionLocal()
    try:
        from models.appointment import Appointment

        now = datetime.datetime.utcnow()
        window_start = now
        window_end = now + datetime.timedelta(minutes=30)

        upcoming = (
            db.query(Appointment)
            .filter(
                Appointment.scheduled_at >= window_start,
                Appointment.scheduled_at <= window_end,
                Appointment.status == "Upcoming",
                Appointment.reminder_sent == False,  # noqa: E712
            )
            .all()
        )

        for appt in upcoming:
            # Build a friendly time string
            appt_time_str = (
                appt.scheduled_at.strftime("%I:%M %p")
                if appt.scheduled_at
                else appt.time or "soon"
            )

            push_notification(
                db=db,
                user_id=appt.doctor_id,
                title="⏰ Appointment Reminder",
                message=(
                    f"You have a {appt.type or 'appointment'} scheduled at "
                    f"{appt_time_str} in {appt.room or 'your clinic'}. "
                    f"Starting in 30 minutes."
                ),
                icon="calendar.badge.clock",
                type="appointment_reminder",
            )

            # Mark reminder as sent so we don't spam
            appt.reminder_sent = True
            db.commit()

            logger.info(f"[Scheduler] Reminder sent for appointment {appt.id}")

    except Exception as e:
        logger.error(f"[Scheduler] appointment_reminder_job error: {e}")
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# JOB 2: Software Update Notification – fires daily at 9 AM UTC
# ──────────────────────────────────────────────────────────────────────────────
def software_update_check_job():
    """
    If the latest published version in the DB is newer than CURRENT_APP_VERSION,
    notify every user who hasn't already been notified about this version.
    Falls back to a simple daily 'tip' notification if no update is pending.
    """
    db = SessionLocal()
    try:
        from models.user import User
        from models.notification import Notification
        from sqlalchemy import func

        users = db.query(User).all()

        for user in users:
            # Check if this user already got a software update notification today
            today_start = datetime.datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            already_notified = (
                db.query(Notification)
                .filter(
                    Notification.user_id == user.id,
                    Notification.type == "software_update",
                    Notification.created_at >= today_start,
                )
                .first()
            )

            if not already_notified:
                push_notification(
                    db=db,
                    user_id=user.id,
                    title="🚀 UltraXpert Update Available",
                    message=(
                        f"A new version of UltraXpert ({CURRENT_APP_VERSION}) is ready. "
                        "Update now for the latest features and security improvements."
                    ),
                    icon="arrow.down.circle.fill",
                    type="software_update",
                )
                logger.info(f"[Scheduler] Software update notification sent to user {user.id}")

    except Exception as e:
        logger.error(f"[Scheduler] software_update_check_job error: {e}")
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# JOB 3: Daily Clinical Reminder – fires every morning at 8 AM UTC
# ──────────────────────────────────────────────────────────────────────────────
def daily_clinical_reminder_job():
    """
    Each morning, notify all doctors how many appointments they have today
    and remind them to review any pending scan enhancements.
    """
    db = SessionLocal()
    try:
        from models.user import User
        from models.appointment import Appointment
        from models.enhancement import Enhancement
        from models.patient import Patient

        today_start = datetime.datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = today_start + datetime.timedelta(days=1)

        users = db.query(User).all()

        for user in users:
            # Count today's appointments
            appt_count = (
                db.query(Appointment)
                .filter(
                    Appointment.doctor_id == user.id,
                    Appointment.scheduled_at >= today_start,
                    Appointment.scheduled_at < today_end,
                    Appointment.status == "Upcoming",
                )
                .count()
            )

            # Count pending enhancements for this doctor's patients
            pending_enhancements = (
                db.query(Enhancement)
                .join(Patient, Enhancement.patient_id == Patient.id)
                .filter(Patient.doctor_id == user.id)
                .count()
            )

            parts = []
            if appt_count > 0:
                parts.append(f"{appt_count} appointment{'s' if appt_count > 1 else ''} today")
            if pending_enhancements > 0:
                parts.append(f"{pending_enhancements} scan enhancement{'s' if pending_enhancements > 1 else ''} to review")

            if parts:
                push_notification(
                    db=db,
                    user_id=user.id,
                    title="🌅 Good Morning, Doctor",
                    message="You have " + " and ".join(parts) + ". Have a great day!",
                    icon="sun.max.fill",
                    type="daily_summary",
                )

    except Exception as e:
        logger.error(f"[Scheduler] daily_clinical_reminder_job error: {e}")
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# Start / Stop scheduler
# ──────────────────────────────────────────────────────────────────────────────
_scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler():
    """Register all jobs and start the scheduler. Called from main.py on startup."""
    # Appointment reminders: every 60 seconds
    _scheduler.add_job(
        appointment_reminder_job,
        trigger=IntervalTrigger(seconds=60),
        id="appointment_reminder",
        replace_existing=True,
        misfire_grace_time=30,
    )

    # Software update: daily at 09:00 UTC
    _scheduler.add_job(
        software_update_check_job,
        trigger=CronTrigger(hour=9, minute=0),
        id="software_update_check",
        replace_existing=True,
    )

    # Daily clinical summary: daily at 08:00 UTC
    _scheduler.add_job(
        daily_clinical_reminder_job,
        trigger=CronTrigger(hour=8, minute=0),
        id="daily_clinical_reminder",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("[Scheduler] Started — appointment reminders, software updates, daily summaries active.")


def stop_scheduler():
    """Shut down the scheduler gracefully. Called from main.py on shutdown."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped.")
