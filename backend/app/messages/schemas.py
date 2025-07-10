from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SendMessageSchema(BaseModel):
    receiver_id: int
    message: str
    booking_id: Optional[int] = None

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    from_me: bool
    sent_at: datetime
    first_name: str
    last_name: str