from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import dependencies
from core.notify import push_notification
import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Retrieve patients."""
    patients = (
        db.query(models.Patient)
        .filter(models.Patient.doctor_id == current_user.id)
        .all()
    )
    return patients


@router.post("/", response_model=schemas.Patient)
def create_patient(
    patient_in: schemas.PatientCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Create new patient."""
    db_obj = models.Patient(**patient_in.dict(), doctor_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 🔔 Notification: New patient added
    patient_name = getattr(db_obj, "name", None) or getattr(db_obj, "full_name", None) or "a new patient"
    push_notification(
        db=db,
        user_id=current_user.id,
        title="👤 Patient Added",
        message=f"{patient_name} has been added to your patient list successfully.",
        icon="person.badge.plus",
        type="patient_added",
    )

    return db_obj
