from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ReportBase(BaseModel):
    scan_type: Optional[str] = None
    modality: Optional[str] = None
    body_part: Optional[str] = None
    status: str = "Completed"
    findings: Optional[str] = None
    impression: Optional[str] = None
    recommendations: Optional[str] = None
    patient_id: Optional[str] = None

class ReportCreate(ReportBase):
    patient_id: str
    scan_type: str

class ReportUpdate(ReportBase):
    pass

class ReportInDBBase(ReportBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Report(ReportInDBBase):
    pass
