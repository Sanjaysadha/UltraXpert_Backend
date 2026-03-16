from typing import Optional
from pydantic import BaseModel

class ExportReportRequest(BaseModel):
    report_id: str
    notification_id: Optional[str] = None
    export_format: str = "PDF"   # PDF, DICOM, JPEG, CSV
    include_images: bool = True
    include_notes: bool = True
