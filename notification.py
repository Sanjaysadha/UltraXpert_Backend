from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    icon: Optional[str] = "bell.fill"
    type: Optional[str] = "general"
    is_read: bool = False
    file_url: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationInDB(NotificationBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class Notification(NotificationInDB):
    pass
