from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PatientBase(BaseModel):
    patient_identifier: Optional[str] = None
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None

class PatientCreate(PatientBase):
    patient_identifier: str
    name: str

class PatientUpdate(PatientBase):
    pass

class PatientInDBBase(PatientBase):
    id: Optional[str] = None
    doctor_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Patient(PatientInDBBase):
    pass
