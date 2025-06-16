from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.admin.controller import fetch_all_users
from app.admin.schemas import UserOut

router = APIRouter(
    prefix="/admin",
    tags=["admin-user-management"]
)

# ✅ Admin check
def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user  # return the user dict if needed in the route

# ✅ Secure route
@router.get("/users", response_model=list[UserOut])
async def get_all_users(
    search: str = Query(None),
    role: str = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),  # 👈 this enforces admin role
):
    return await fetch_all_users(db, search=search, role=role, status=status)
