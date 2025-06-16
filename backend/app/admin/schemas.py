from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
