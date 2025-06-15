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



class SupportTicketReplyResponse(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    sender_name: str
    sender_role: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True

class SupportTicketDetailResponse(SupportTicketResponse):
    replies: list[SupportTicketReplyResponse] = []

class TicketReplyCreate(BaseModel):
    message: str
