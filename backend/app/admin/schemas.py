from pydantic import BaseModel
from datetime import datetime
from app.auth.schemas import UserCreate


# Defines shape of user data returned to the frontend
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


# Inherits everthing from UserCreate -> reuses it in admin-specific context with admin_create_user route.
class AdminCreateUser(UserCreate):
    pass
