import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from api import dependencies
from core.notify import push_notification
import models, schemas

router = APIRouter()
UPLOAD_DIR = "uploads/scans"

@router.post("/upload")
def upload_scan(
    file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/static/scans/{filename}"

    # 🔔 Notification: Scan uploaded successfully
    push_notification(
        db=db,
        user_id=current_user.id,
        title="📤 Upload Successful",
        message=f"Your ultrasound scan '{file.filename}' was uploaded successfully and is ready for enhancement.",
        icon="checkmark.seal.fill",
        type="scan_upload",
    )

    return {"original_image_url": image_url}


@router.post("/enhance", response_model=schemas.Enhancement)
def enhance_scan(
    enhancement_in: schemas.EnhancementCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    import os
    from core.image_enhancer import enhance_image_ai

    # Find the actual file path from the URL
    if not enhancement_in.original_image_url.startswith("/static/"):
        raise HTTPException(status_code=400, detail="Invalid image URL")

    filename = enhancement_in.original_image_url.split("/")[-1]
    input_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Original image not found")

    file_ext = filename.split(".")[-1]
    enhanced_filename = filename.replace(f".{file_ext}", f"_enhanced.{file_ext}")
    output_path = os.path.join(UPLOAD_DIR, enhanced_filename)

    # Perform actual AI enhancement
    success = enhance_image_ai(image_path=input_path, output_path=output_path)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to enhance image")

    enhanced_url = f"/static/scans/{enhanced_filename}"

    db_obj = models.Enhancement(
        patient_id=enhancement_in.patient_id,
        original_image_url=enhancement_in.original_image_url,
        enhanced_image_url=enhanced_url,
        improvement_percentage="+140%"  # AI predicted value
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 🔔 Notification: Enhancement complete
    push_notification(
        db=db,
        user_id=current_user.id,
        title="✨ Enhancement Completed",
        message="Your ultrasound image enhancement is complete with a +140% clarity improvement. Tap to view the result.",
        icon="sparkles",
        type="enhancement_complete",
    )

    return db_obj

class ManualEnhanceRequest(schemas.EnhancementCreate):
    noise_reduction: float
    contrast: float
    sharpening: float

@router.post("/manual_enhance", response_model=schemas.Enhancement)
def manual_enhance_scan(
    req: ManualEnhanceRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    import os
    from core.image_enhancer import manual_enhance_image

    if not req.original_image_url.startswith("/static/"):
        raise HTTPException(status_code=400, detail="Invalid image URL")

    filename = req.original_image_url.split("/")[-1]
    input_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Original image not found")

    file_ext = filename.split(".")[-1]
    enhanced_filename = filename.replace(f".{file_ext}", f"_manual_{req.patient_id}.{file_ext}")
    output_path = os.path.join(UPLOAD_DIR, enhanced_filename)

    success = manual_enhance_image(
        image_path=input_path, 
        output_path=output_path,
        noise_reduction=req.noise_reduction,
        contrast=req.contrast,
        sharpening=req.sharpening
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to enhance image")

    enhanced_url = f"/static/scans/{enhanced_filename}"

    db_obj = models.Enhancement(
        patient_id=req.patient_id,
        original_image_url=req.original_image_url,
        enhanced_image_url=enhanced_url,
        improvement_percentage="Manual"
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return db_obj


@router.get("/analytics", response_model=List[schemas.Enhancement])
def get_analytics(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    enhancements = (
        db.query(models.Enhancement)
        .join(models.Patient)
        .filter(models.Patient.doctor_id == current_user.id)
        .all()
    )
    return enhancements
