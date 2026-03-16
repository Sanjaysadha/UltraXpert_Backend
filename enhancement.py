from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class EnhancementBase(BaseModel):
    original_image_url: Optional[str] = None
    enhanced_image_url: Optional[str] = None
    improvement_percentage: Optional[str] = None
    patient_id: Optional[str] = None

class EnhancementCreate(EnhancementBase):
    patient_id: str
    original_image_url: str
    enhanced_image_url: str

class EnhancementUpdate(EnhancementBase):
    pass

class EnhancementInDBBase(EnhancementBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Enhancement(EnhancementInDBBase):
    pass
