from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api import dependencies
from core.notify import push_notification
import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Report])
def read_reports(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    reports = (
        db.query(models.Report)
        .join(models.Patient)
        .filter(models.Patient.doctor_id == current_user.id)
        .all()
    )
    return reports


@router.post("/", response_model=schemas.Report)
def create_report(
    report_in: schemas.ReportCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    db_obj = models.Report(**report_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 🔔 Notification: Report generated
    push_notification(
        db=db,
        user_id=current_user.id,
        title="📋 Report Generated",
        message="A new medical report has been generated and saved successfully. You can export or share it anytime.",
        icon="doc.text.fill",
        type="report_generated",
    )

    return db_obj


@router.post("/export")
def export_report_alias(
    export_in: schemas.ExportReportRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Alias for the dedicated export endpoint to improve app connectivity."""
    from api.v1.endpoints.export_report import export_report
    return export_report(export_in=export_in, db=db, current_user=current_user)
