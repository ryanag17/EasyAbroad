import bcrypt, secrets, shutil
from pathlib import Path

from fastapi import HTTPException, Depends, APIRouter, UploadFile, File, Query, status
from sqlalchemy import select, delete, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import (
    User, UserLanguage, Language, Country, RefreshToken
)
from app.auth.schemas import (
    UserCreate, UserLogin, UserUpdateProfile, ChangePasswordRequest, DeleteAccountRequest
)
from app.auth.token_service import create_access_token, create_refresh_token
from app.auth.token_verification import get_current_user
from app.db import get_db
import uuid
from PIL import Image
import io


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)

UPLOAD_DIR = Path("static/uploads/profile_pictures")


@router.post("/upload-picture", summary="Upload profile picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    ext = file.filename.split(".")[-1].lower()
    if ext not in {"jpg", "jpeg", "png"}:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a secure UUID for file name
    unique_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{unique_id}.jpg"

    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Convert to RGB if needed
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")

    image.thumbnail((800, 800))

    buffer = io.BytesIO()
    quality = 85

    while True:
        buffer.seek(0)
        buffer.truncate(0)
        image.save(buffer, format="JPEG", quality=quality)
        size_in_mb = buffer.tell() / (1024 * 1024)
        if size_in_mb <= 2 or quality <= 40:
            break
        quality -= 5

    with file_path.open("wb") as f:
        f.write(buffer.getvalue())

    relative_path = f"/static/uploads/profile_pictures/{file_path.name}"

    await db.execute(
        text("UPDATE users SET profile_picture=:pic WHERE id=:uid"),
        {"pic": relative_path, "uid": user_id}
    )
    await db.commit()

    return {"message": "Profile picture updated", "url": relative_path}



@router.put("/password", summary="Change your password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    stmt = select(User.password_hash).where(User.id == user_id)
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(404, "User not found")

    if not bcrypt.checkpw(payload.old_password.encode(), row.password_hash.encode()):
        raise HTTPException(400, "Old password is incorrect")

    # ← Prevent reuse of the old password
    if bcrypt.checkpw(payload.new_password.encode(), row.password_hash.encode()):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the old password."
        )

    
    new_hash = bcrypt.hashpw(payload.new_password.encode(), bcrypt.gensalt()).decode()
    await db.execute(
        update(User).
        where(User.id == user_id).
        values(password_hash=new_hash)
    )
    await db.commit()

    return {"message": "Password changed successfully"}


@router.get("/student", response_model=dict, summary="Get the logged-in student’s profile")
async def get_student_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    if current_user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Not a student")

    stmt = select(
        User.first_name, User.last_name, User.email,
        User.city, User.country_name, User.birthday, User.gender,
        User.profile_picture
    ).where(User.id == user_id, User.role == "student")
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    lang_stmt = (
        select(Language.language_name)
        .join(UserLanguage, UserLanguage.language_id == Language.id)
        .where(UserLanguage.user_id == user_id)
    )
    lang_result = await db.execute(lang_stmt)
    languages = list(lang_result.scalars().all())

    return {
        "first_name": row.first_name,
        "last_name": row.last_name,
        "email": row.email,
        "city": row.city,
        "country": row.country_name,
        "birthday": row.birthday.isoformat() if row.birthday else None,
        "gender": row.gender,
        "profile_picture": row.profile_picture,
        "languages": languages
    }


@router.get("/languages", response_model=list[dict], summary="Return all available languages (id + name) for the multi-select")
async def list_all_languages(db: AsyncSession = Depends(get_db)):
    stmt = select(Language.id, Language.language_name)
    result = await db.execute(stmt)
    rows = result.all()
    return [{"id": r[0], "language_name": r[1]} for r in rows]


@router.get("/countries", response_model=list[str], summary="Get all countries")
async def list_countries(db: AsyncSession = Depends(get_db)):
    stmt = select(Country.country_name).order_by(Country.country_name)
    result = await db.execute(stmt)
    return result.scalars().all()






@router.put("/student", response_model=dict)
async def update_student_profile(
    payload: UserUpdateProfile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    if current_user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Not a student")
    # 1) Fetch user row (must be a student)
    result = await db.execute(
        select(User).where(User.id == user_id, User.role == "student")
    )
    user_obj = result.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # 2) Update allowed columns if provided
    if payload.first_name is not None:
        user_obj.first_name = payload.first_name
    if payload.last_name is not None:
        user_obj.last_name = payload.last_name
    if payload.city is not None:
        user_obj.city = payload.city
    if payload.country_name is not None:
        user_obj.country_name = payload.country_name
    if payload.gender is not None:
        user_obj.gender = payload.gender

    # 3) Replace languages if list is provided
    if payload.languages is not None:
        # Delete existing links
        await db.execute(delete(UserLanguage).where(UserLanguage.user_id == user_id))
        # Re-insert new language links
        for lang_id in payload.languages:
            # (Optional) Check that the language exists
            lang_check = await db.execute(select(Language.id).where(Language.id == lang_id))
            if not lang_check.scalar_one_or_none():
                raise HTTPException(status_code=400, detail=f"Language ID {lang_id} does not exist")
            new_link = UserLanguage(user_id=user_id, language_id=lang_id)
            db.add(new_link)

    await db.commit()
    await db.refresh(user_obj)

    # 4) Return updated profile fields (including language names)
    lang_q = await db.execute(
        select(Language.language_name).join(UserLanguage).where(UserLanguage.user_id == user_id)
    )
    language_names = lang_q.scalars().all()

    return {
        "first_name": user_obj.first_name,
        "last_name" : user_obj.last_name,
        "city"      : user_obj.city,
        "country"   : user_obj.country_name,
        "gender"    : user_obj.gender,
        "languages" : language_names
    }

@router.get(
    "/consultant",
    response_model=dict,
    summary="Get the logged-in consultant’s profile"
)
async def get_consultant_profile_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    if current_user.get("role") != "consultant":
        raise HTTPException(status_code=403, detail="Not a consultant")

    # Reuse your helper
    data = await get_consultant_profile(db, user_id)
    # Ensure birthday is ISO string
    data["birthday"] = data["birthday"].isoformat() if data["birthday"] else None
    return data

# PUT /profile/consultant 
@router.put("/consultant", response_model=dict)
async def update_consultant_profile(
    payload: UserUpdateProfile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    if current_user.get("role") != "consultant":
        raise HTTPException(status_code=403, detail="Not a consultant")

    # Fetch the user row
    result = await db.execute(
        select(User).where(User.id == user_id, User.role == "consultant")
    )
    user_obj = result.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Consultant profile not found")

    # Update same fields as student
    if payload.first_name   is not None: user_obj.first_name   = payload.first_name
    if payload.last_name    is not None: user_obj.last_name    = payload.last_name
    if payload.city         is not None: user_obj.city         = payload.city
    if payload.country_name is not None: user_obj.country_name = payload.country_name
    if payload.gender       is not None: user_obj.gender       = payload.gender

    # Replace languages
    if payload.languages is not None:
        await db.execute(delete(UserLanguage).where(UserLanguage.user_id == user_id))
        for lang_id in payload.languages:
            # verify language exists
            chk = await db.execute(select(Language.id).where(Language.id == lang_id))
            if not chk.scalar_one_or_none():
                raise HTTPException(status_code=400, detail=f"Language ID {lang_id} does not exist")
            db.add(UserLanguage(user_id=user_id, language_id=lang_id))

    await db.commit()
    await db.refresh(user_obj)

    # Return names
    lang_q = await db.execute(
        select(Language.language_name).join(UserLanguage).where(UserLanguage.user_id == user_id)
    )
    return {
        "first_name": user_obj.first_name,
        "last_name" : user_obj.last_name,
        "city"      : user_obj.city,
        "country"   : user_obj.country_name,
        "gender"    : user_obj.gender,
        "languages" : lang_q.scalars().all()
    }





# ────────── GET /profile/admin ──────────
@router.get(
    "/admin",
    response_model=dict,
    summary="Get the logged-in admin’s profile"
)
async def get_admin_profile_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")

    stmt = select(
        User.first_name, User.last_name, User.email,
        User.city, User.country_name, User.birthday, User.gender,
        User.profile_picture
    ).where(User.id == user_id, User.role == "admin")
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    # fetch language names
    lang_stmt = (
        select(Language.language_name)
        .join(UserLanguage, UserLanguage.language_id == Language.id)
        .where(UserLanguage.user_id == user_id)
    )
    lang_result = await db.execute(lang_stmt)
    languages = lang_result.scalars().all()

    return {
        "first_name"      : row.first_name,
        "last_name"       : row.last_name,
        "email"           : row.email,
        "city"            : row.city,
        "country"         : row.country_name,
        "birthday"        : row.birthday.isoformat() if row.birthday else None,
        "gender"          : row.gender,
        "profile_picture" : row.profile_picture,
        "languages"       : languages
    }

# PUT /profile/admin 
@router.put("/admin", response_model=dict)
async def update_admin_profile(
    payload: UserUpdateProfile,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not an admin")

    # 1) fetch the admin row
    result = await db.execute(
        select(User).where(User.id == user_id, User.role == "admin")
    )
    user_obj = result.scalars().first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Admin profile not found")

    # 2) update allowed fields
    if payload.first_name   is not None: user_obj.first_name   = payload.first_name
    if payload.last_name    is not None: user_obj.last_name    = payload.last_name
    if payload.city         is not None: user_obj.city         = payload.city
    if payload.country_name is not None: user_obj.country_name = payload.country_name
    if payload.gender       is not None: user_obj.gender       = payload.gender

    # 3) replace languages
    if payload.languages is not None:
        await db.execute(delete(UserLanguage).where(UserLanguage.user_id == user_id))
        for lang_id in payload.languages:
            # ensure language exists
            check = await db.execute(select(Language.id).where(Language.id == lang_id))
            if not check.scalar_one_or_none():
                raise HTTPException(status_code=400, detail=f"Language ID {lang_id} does not exist")
            db.add(UserLanguage(user_id=user_id, language_id=lang_id))

    await db.commit()
    await db.refresh(user_obj)

    # 4) return updated names
    lang_q = await db.execute(
        select(Language.language_name).join(UserLanguage).where(UserLanguage.user_id == user_id)
    )
    return {
        "first_name": user_obj.first_name,
        "last_name" : user_obj.last_name,
        "city"      : user_obj.city,
        "country"   : user_obj.country_name,
        "gender"    : user_obj.gender,
        "languages" : lang_q.scalars().all()
    }


async def get_consultant_profile(db: AsyncSession, user_id: int):
    stmt = select(
        User.first_name, User.last_name, User.email,
        User.city, User.country_name, User.birthday, User.gender,
        User.profile_picture
    ).where(User.id == user_id, User.role == "consultant")
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    lang_stmt = (
        select(Language.language_name)
        .join(UserLanguage, UserLanguage.language_id == Language.id)
        .where(UserLanguage.user_id == user_id)
    )
    lang_result = await db.execute(lang_stmt)
    languages = [r for r in lang_result.scalars().all()]


    return {
        "first_name"      : row.first_name,
        "last_name"       : row.last_name,
        "email"           : row.email,
        "city"            : row.city,
        "country"         : row.country_name,
        "birthday"        : row.birthday,
        "gender"          : row.gender,
        "profile_picture" : row.profile_picture,
        "languages"       : languages
    }


from app.auth.models import RefreshToken
from pathlib import Path
from sqlalchemy import delete

@router.delete("", summary="Delete your account")
async def delete_account(
    payload: DeleteAccountRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # Load the user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    # Verify email & password
    if payload.email.lower() != user.email.lower() \
       or not bcrypt.checkpw(payload.password.encode(), user.password_hash.encode()):
        raise HTTPException(400, "Email or password is incorrect")

    # Delete linked data
    await db.execute(text("DELETE FROM Education WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM Internship WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM consultant_availability WHERE consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("""
        DELETE FROM support_tickets WHERE user_id = :uid;
        DELETE FROM support_ticket_messages WHERE sender_id = :uid;
    """), {"uid": user_id})
    await db.execute(text("DELETE FROM appointments WHERE student_id = :uid OR consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM consultant_reviews WHERE student_id = :uid OR consultant_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM notifications WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM refresh_tokens WHERE user_id = :uid"), {"uid": user_id})
    await db.execute(text("DELETE FROM user_languages WHERE user_id = :uid"), {"uid": user_id})

    # Delete old messages only
    await db.execute(text("""
        DELETE FROM messages
        WHERE (sender_id = :uid OR receiver_id = :uid)
        AND sent_at < DATE_SUB(NOW(), INTERVAL 3 YEAR)
    """), {"uid": user_id})

    # Delete profile picture file
    if user.profile_picture:
        pic = Path(".") / user.profile_picture.lstrip("/")
        if pic.exists():
            pic.unlink()

    # Soft delete
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active="deleted")
    )
    await db.commit()


    return {"message": "Account deleted successfully"}