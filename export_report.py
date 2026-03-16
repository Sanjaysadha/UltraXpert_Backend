import os
import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from api import dependencies
import models, schemas
from schemas.export import ExportReportRequest

from core.report_generator import (
    generate_medical_report_pdf,
    generate_medical_report_csv,
    generate_medical_report_jpeg,
    generate_medical_report_dicom
)
from core.notify import push_notification

router = APIRouter()


@router.post("/report")
def export_report(
    export_in: ExportReportRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
):
    # 🔍 1. Verify Report & Authorization
    print(f"DEBUG: Export requested for report: {export_in.report_id} - Format: {export_in.export_format}")
    report = db.query(models.Report).filter(models.Report.id == export_in.report_id).first()
    if not report:
         raise HTTPException(status_code=404, detail="Report not found")
    
    patient = db.query(models.Patient).filter(models.Patient.id == report.patient_id).first()
    if not patient or patient.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this report")

    # 🧨 2. Optional: Remove old notification (requested earlier)
    if export_in.notification_id:
        notification = db.query(models.Notification).filter(
            models.Notification.id == export_in.notification_id,
            models.Notification.user_id == current_user.id
        ).first()
        if notification:
            db.delete(notification)
            db.commit()

    # 🖼️ 3. Find associated images if needed
    image_path = None
    latest_enhancement = db.query(models.Enhancement).filter(
        models.Enhancement.patient_id == report.patient_id
    ).order_by(models.Enhancement.created_at.desc()).first()
    
    if latest_enhancement:
        url_part = latest_enhancement.enhanced_image_url.split("/static/scans/")[-1]
        image_path = os.path.join("uploads", "scans", url_part)

    print(f"DEBUG: Starting export process for report {report.id}")
    
    # 📄 4. Professional Export based on Format
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    format_lower = export_in.export_format.lower()
    ext = format_lower
    if "jpeg" in format_lower: ext = "jpg"
    elif "csv" in format_lower: ext = "csv"
    elif "dicom" in format_lower: ext = "dcm"
    else: ext = "pdf"

    filename = f"Report_{report.id[:8]}_{uuid.uuid4().hex[:4]}.{ext}"
    file_path = os.path.join(export_dir, filename)
    
    try:
        # Selection logic for the 4 formats
        if ext == "pdf":
            generate_medical_report_pdf(
                report_obj=report,
                patient_obj=patient,
                doctor_full_name=current_user.full_name or "Doctor",
                file_path=file_path,
                enhanced_image_path=image_path if export_in.include_images else None,
                include_notes=export_in.include_notes
            )
        elif ext == "csv":
            generate_medical_report_csv(
                report_obj=report,
                patient_obj=patient,
                doctor_full_name=current_user.full_name or "Doctor",
                file_path=file_path,
                include_notes=export_in.include_notes
            )
        elif ext == "jpg":
            generate_medical_report_jpeg(
                enhanced_image_path=image_path if export_in.include_images else None,
                file_path=file_path,
                include_notes=export_in.include_notes,
                patient_name=patient.name
            )
        elif ext == "dcm":
            generate_medical_report_dicom(
                report_obj=report,
                patient_obj=patient,
                enhanced_image_path=image_path if export_in.include_images else None,
                file_path=file_path,
                include_notes=export_in.include_notes
            )
    except Exception as e:
        print(f"ERROR: Export generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate {export_in.export_format} file")

    # 📥 5. Create File URL
    # Use the appropriate host (if accessed from mobile simulator use computer IP or 127.0.0.1)
    base_url = "http://127.0.0.1:8000"
    file_url = f"{base_url}/static/exports/{filename}"
    
    # 💾 6. Save to Downloads Table
    download_record = models.Download(
        user_id=current_user.id,
        patient_name=patient.name,
        report_id=report.id,
        file_name=filename,
        file_url=file_url,
        file_type=export_in.export_format.upper()
    )
    db.add(download_record)
    
    # 🔔 7. Create Notification for the Exported File
    notif = push_notification(
        db=db,
        user_id=current_user.id,
        title=f"📥 {export_in.export_format.upper()} Export Ready",
        message=f"Export for {patient.name} is complete.",
        icon="doc.text.fill",
        type="report_generated",
        file_url=file_url
    )
    
    db.commit()
    db.refresh(download_record)
    
    print(f"DEBUG: Export successful for report {report.id}. ID: {download_record.id}")

    return {
        "status": "success",
        "message": f"Report exported as {export_in.export_format}",
        "file_url": file_url,
        "notification": notif,
        "download_id": download_record.id
    }


@router.get("/downloads")
def list_downloads(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Returns all exported reports formatted as notifications for the app's Downloads screen."""
    downloads = db.query(models.Download).filter(
        models.Download.user_id == current_user.id
    ).order_by(models.Download.created_at.desc()).all()
    
    # Map to Notification-like structure for app compatibility
    response = []
    for d in downloads:
        # Determine icon based on file type
        icon = "doc.richtext.fill"
        if "CSV" in d.file_type.upper(): icon = "tablecells.fill"
        elif "JPEG" in d.file_type.upper() or "JPG" in d.file_type.upper(): icon = "photo.fill"
        elif "DICOM" in d.file_type.upper(): icon = "doc.append.fill"
        
        response.append({
            "id": d.id,
            "user_id": d.user_id,
            "title": f"📥 {d.file_type} Document",
            "message": f"Report exported for {d.patient_name}",
            "icon": icon,
            "type": "report_export",
            "is_read": True,
            "file_url": d.file_url,
            "created_at": d.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        })
    
    print(f"DEBUG: Returning {len(response)} downloads for user {current_user.id}")
    return response
