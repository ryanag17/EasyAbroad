from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

class ConsultantAvailabilityOut(BaseModel):
    days_of_week: List[int]
    start_time: str
    end_time: str

class AppointmentCreate(BaseModel):
    consultant_public_id: str    
    date: str
    start_time: str
    end_time: str
    reason: str
    info: Optional[str] = None
    platform: str
    rejection_reason: Optional[str] = None
    type: str

class AppointmentOut(BaseModel):
    id: int
    public_id: str    
    consultant_id: int
    consultant_public_id: Optional[str] = None
    student_id: int
    date: date 
    start_time: str
    end_time: str
    reason: str
    info: Optional[str] = None
    platform: str
    status: str
    meeting_link: Optional[str]
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    consultant_name: Optional[str] = None
    student_name: Optional[str] = None
    type: str
    
    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    public_id: str
    rating: int
    review_text: Optional[str]


class ReviewOut(BaseModel):
    id: int
    public_id: str
    booking_id: int
    student_id: int
    consultant_id: int
    rating: int
    review_text: Optional[str]
    submitted_at: datetime
    student_name: Optional[str] = None

    class Config:
        orm_mode = True