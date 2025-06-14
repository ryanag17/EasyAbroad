from pydantic import BaseModel
from datetime import datetime

class SupportTicketCreate(BaseModel):
    subject: str
    description: str

class SupportTicketResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    resolved_by: int | None = None
    resolved_at: datetime | None = None

    class Config:
        orm_mode = True
