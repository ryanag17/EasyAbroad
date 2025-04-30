from fastapi import APIRouter, Depends
from app.auth.token_verification import token_required
from app.auth.models import UserLogin, UserCreate, ForgotPasswordRequest, ResetPasswordRequest
from app.auth.controller import register, login, forgot_password, reset_password

router = APIRouter(tags=["auth"])

@router.post("/register")
def register_user(user: UserCreate):
    return register(user)

@router.post("/login")
def login_user(user: UserLogin):
    return login(user)

@router.post("/forgot-password")
def forgot_password_user(data: ForgotPasswordRequest):
    return forgot_password(data.email)

@router.post("/reset-password")
def reset_password_user(data: ResetPasswordRequest):
    return reset_password(data.token, data.password)

@router.get("/me")
async def get_current_user(current_user: dict = Depends(token_required)):
    return {
        "id": current_user["id"],
        "role": current_user["role"]
    }
