from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DownloadBase(BaseModel):
    patient_name: str
    report_id: str
    file_name: str
    file_url: str
    file_type: str

class DownloadCreate(DownloadBase):
    pass

class Download(DownloadBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
