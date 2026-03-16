from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class AppointmentBase(BaseModel):
    type: Optional[str] = None
    time: Optional[str] = None
    scheduled_at: Optional[datetime] = None   # ISO8601 datetime
    room: Optional[str] = None
    status: str = "Upcoming"
    notes: Optional[str] = None
    patient_id: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: str
    time: str

class AppointmentUpdate(AppointmentBase):
    pass

class AppointmentInDBBase(AppointmentBase):
    id: Optional[str] = None
    doctor_id: Optional[str] = None
    reminder_sent: Optional[bool] = False

    class Config:
        from_attributes = True

class Appointment(AppointmentInDBBase):
    pass

