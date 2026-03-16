import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core import security
from core.config import settings
from api import dependencies
from core.email import send_otp_email
import models, schemas

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=schemas.User)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db)
):
    """
    Create new user.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    db_obj = models.User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        medical_license_id=user_in.medical_license_id,
        role=user_in.role,
        phone_number=user_in.phone_number,
        hospital_name=user_in.hospital_name,
        specialization=user_in.specialization,
        enable_notifications=user_in.enable_notifications,
        scan_updates=user_in.scan_updates
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/forgot-password")
def forgot_password(
    data: schemas.ForgotPassword,
    db: Session = Depends(dependencies.get_db)
):
    """
    Generate OTP and send it via email.
    """
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        # We don't want to leak if a user exists or not, but for internal apps it's fine
        # For security, we usually say "Email sent if user exists"
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    
    db.add(user)
    db.commit()
    
    try:
        send_otp_email(user.email, otp)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
        
    return {"message": "OTP sent to your email"}

@router.post("/verify-otp")
def verify_otp(
    data: schemas.VerifyOTP,
    db: Session = Depends(dependencies.get_db)
):
    """
    Verify the OTP provided by the user.
    """
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    return {"message": "OTP verified successfully"}

@router.post("/reset-password")
def reset_password(
    data: schemas.ResetPassword,
    db: Session = Depends(dependencies.get_db)
):
    """
    Reset password using verified OTP.
    """
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    # Update password
    user.hashed_password = security.get_password_hash(data.new_password)
    # Clear OTP
    user.otp_code = None
    user.otp_expiry = None
    
    db.add(user)
    db.commit()
    
    return {"message": "Password reset successfully"}
