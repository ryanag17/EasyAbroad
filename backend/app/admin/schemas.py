from pydantic import BaseModel
from datetime import datetime
from app.auth.schemas import UserCreate
from typing import Union

# Defines shape of user data returned to the frontend
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: Union[str, bool] 
    created_at: datetime

    class Config:
        from_attributes = True


# Inherits everthing from UserCreate -> reuses it in admin-specific context with admin_create_user route.
class AdminCreateUser(UserCreate):
    pass
