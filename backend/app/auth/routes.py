from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Request,
    Body,
)
from app.auth.token_verification import token_required
from app.auth.models import (
    UserLogin,
    UserCreate,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.auth.controller import (
    register,
    login,
    forgot_password,
    reset_password,
    get_student_profile,
    update_student_profile,
)
import os
import uuid

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
def get_current_user(current_user: dict = Depends(token_required)):
    # We return both the user id AND role so your front‐end can
    # branch on Student vs Consultant, etc.
    return {"id": current_user["sub"], "role": current_user["role"]}


@router.post("/students/me/picture")
async def upload_picture(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(token_required),
):
    # Only students may do this:
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can upload pictures")

    # Save the file
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    save_dir = os.path.join("static", "profile_pics")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, fname)

    with open(save_path, "wb") as out:
        out.write(await file.read())

    # Build public URL
    base_url = str(request.base_url).rstrip("/")  # e.g. http://localhost:8000
    pic_url = f"{base_url}/static/profile_pics/{fname}"

    # Persist
    update_student_profile(current_user["sub"], {"profile_picture": pic_url})

    return {"profile_picture": pic_url}


@router.get("/students/me")
def api_get_my_profile(current_user: dict = Depends(token_required)):
    # Fetch the student row
    profile = get_student_profile(current_user["sub"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/students/me")
def api_update_my_profile(
    payload: dict = Body(...),
    current_user: dict = Depends(token_required),
):
    # Only these keys are expected:
    allowed = {"city", "country", "gender", "languages", "first_name", "last_name", "birthday", "email"}
    body = {k: v for k, v in payload.items() if k in allowed}

    success = update_student_profile(current_user["sub"], body)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to save profile")
    return {"success": True}
