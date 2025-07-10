from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SendMessageSchema(BaseModel):
    receiver_id: Optional[int] = None
    conversation_id: Optional[str] = None
    message: str
    booking_id: Optional[int] = None

class MessageOut(BaseModel):
    public_id: str
    sender_id: int
    receiver_id: int
    message: str
    from_me: bool
    sent_at: datetime
    first_name: str
    last_name: str
    conversation_public_id: str

    class Config:
        orm_mode = True

class ConversationOut(BaseModel):
    id: int
    public_id: str
    user_a_id: int
    user_b_id: int
    created_at: datetime
