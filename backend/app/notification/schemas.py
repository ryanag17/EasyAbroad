from datetime import datetime
from pydantic import BaseModel

class NotificationBase(BaseModel):
    content: str
    type: str = "info"
    redirect_url: str = "#"

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationOut(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True