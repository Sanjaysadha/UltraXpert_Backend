from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any

from api import dependencies
import models
import schemas

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Update current user.
    """
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        from core.security import get_password_hash
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
        
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
            
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

import os
import shutil

@router.post("/me/image", response_model=schemas.User)
def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Upload profile image.
    """
    os.makedirs("uploads/profiles", exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join("uploads/profiles", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    current_user.profile_image_url = f"/static/profiles/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
