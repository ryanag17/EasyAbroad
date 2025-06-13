from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pathlib import Path
import shutil

from app.auth.token_verification import get_current_user
from app.db import get_db
from app.consultancy.schemas import EducationCreate

consultancy_router = APIRouter(prefix="/consultancy", tags=["consultancy"])
BASE_UPLOAD_DIR = Path("static/uploads/proof_documents")

def save_proof_file(file: UploadFile, user_id: int, category: str):
    ext = file.filename.split(".")[-1].lower()
    if ext not in {"pdf", "jpg", "jpeg", "png"}:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    user_dir = BASE_UPLOAD_DIR / category / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)

    # Delete any existing files in the user's folder
    for existing_file in user_dir.glob("*"):
        try:
            existing_file.unlink()
        except Exception as e:
            print(f"Failed to delete old file: {existing_file} — {e}")

    # Define standardized filename
    renamed_filename = f"{user_id}_proofdocument_{category}.{ext}"

    file_path = user_dir / renamed_filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/proof_documents/{category}/user_{user_id}/{renamed_filename}"


@consultancy_router.post("/upload-proof/study", summary="Consultant: Upload proof of study")
async def upload_study_proof(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    relative_path = save_proof_file(file, user_id, "study")
    return {"message": "Study proof uploaded successfully", "path": relative_path}

@consultancy_router.post("/upload-proof/internship", summary="Consultant: Upload proof of internship")
async def upload_internship_proof(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    relative_path = save_proof_file(file, user_id, "internship")
    return {"message": "Internship proof uploaded successfully", "path": relative_path}

from fastapi import Form, File, UploadFile

@consultancy_router.post("/study", summary="Consultant: Submit education consultancy")
async def submit_study_info(
    university_name: str = Form(...),
    course_name: str = Form(...),
    education_start: str = Form(...),
    education_finish: str = Form(...),
    city_of_study: str = Form(...),
    country_of_study: str = Form(...),
    proof_of_education: UploadFile = File(...),
    accommodation: bool = Form(False),
    social_life: bool = Form(False),
    uni_info: bool = Form(False),
    travel_info: bool = Form(False),
    zoom: bool = Form(False),
    microsoft_teams: bool = Form(False),
    google_meet: bool = Form(False),
    apple_facetime: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Save file
    user_id = current_user["user_id"]
    proof_path = save_proof_file(proof_of_education, user_id, "study")

    # Optional: validate or convert dates
    from datetime import datetime
    start = datetime.strptime(education_start, "%Y-%m")
    finish = datetime.strptime(education_finish, "%Y-%m")

    # Insert into DB
    await db.execute(text("""
        INSERT INTO Education (
            user_id, city_of_study, country_of_study, university_name, course_name,
            education_start, education_finish,
            accommodation, social_life, uni_info, travel_info,
            zoom, microsoft_teams, google_meet, apple_facetime,
            proof_of_education, status
        ) VALUES (
            :user_id, :city, :country, :uni, :course,
            :start, :finish,
            :accom, :social, :uniinfo, :travel,
            :zoom, :teams, :gmeet, :facetime,
            :proof, 'pending'
        )
    """), {
        "user_id": user_id,
        "city": city_of_study,
        "country": country_of_study,
        "uni": university_name,
        "course": course_name,
        "start": start,
        "finish": finish,
        "accom": accommodation,
        "social": social_life,
        "uniinfo": uni_info,
        "travel": travel_info,
        "zoom": zoom,
        "teams": microsoft_teams,
        "gmeet": google_meet,
        "facetime": apple_facetime,
        "proof": proof_path
    })

    await db.commit()
    return {"message": "Study consultancy profile submitted successfully"}


@consultancy_router.post("/internship", summary="Consultant: Submit internship consultancy")
async def submit_internship_info(
    company_name: str = Form(...),
    department_name: str = Form(...),
    internship_start: str = Form(...),
    internship_finish: str = Form(...),
    city_of_internship: str = Form(...),
    country_of_internship: str = Form(...),
    proof_of_internship: UploadFile = File(...),
    accommodation: bool = Form(False),
    social_life: bool = Form(False),
    company_info: bool = Form(False),
    travel_info: bool = Form(False),
    zoom: bool = Form(False),
    microsoft_teams: bool = Form(False),
    google_meet: bool = Form(False),
    apple_facetime: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    proof_path = save_proof_file(proof_of_internship, user_id, "internship")

    from datetime import datetime
    start = datetime.strptime(internship_start, "%Y-%m")
    finish = datetime.strptime(internship_finish, "%Y-%m")

    await db.execute(text("""
        INSERT INTO Internship (
            user_id, city_of_internship, country_of_internship, company_name, department_name,
            internship_start, internship_finish,
            accommodation, social_life, company_info, travel_info,
            zoom, microsoft_teams, google_meet, apple_facetime,
            proof_of_internship, status
        ) VALUES (
            :user_id, :city, :country, :company, :department,
            :start, :finish,
            :accom, :social, :companyinfo, :travel,
            :zoom, :teams, :gmeet, :facetime,
            :proof, 'pending'
        )
    """), {
        "user_id": user_id,
        "city": city_of_internship,
        "country": country_of_internship,
        "company": company_name,
        "department": department_name,
        "start": start,
        "finish": finish,
        "accom": accommodation,
        "social": social_life,
        "companyinfo": company_info,
        "travel": travel_info,
        "zoom": zoom,
        "teams": microsoft_teams,
        "gmeet": google_meet,
        "facetime": apple_facetime,
        "proof": proof_path
    })

    await db.commit()
    return {"message": "Internship consultancy profile submitted successfully"}





# Consultant: View Their Own Submitted Application
@consultancy_router.get("/study/me", summary="Consultant: Get current user's study consultancy")
async def get_my_study_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(text("SELECT * FROM Education WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No study consultancy found.")
    return dict(row._mapping)

# Consultant: Delete Their Own Application
@consultancy_router.delete("/study", summary="Consultant: Delete current user's study consultancy")
async def delete_my_study_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await db.execute(text("DELETE FROM Education WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    await db.commit()
    return {"message": "Study consultancy deleted."}

# Consultant: View Their Own Submitted Application
@consultancy_router.get("/internship/me", summary="Consultant: Get current user's internship consultancy")
async def get_my_internship_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(text("SELECT * FROM Internship WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No internship consultancy found.")
    return dict(row._mapping)

# Consultant: Delete Their Own Application
@consultancy_router.delete("/internship", summary="Consultant: Delete current user's internship consultancy")
async def delete_my_internship_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await db.execute(text("DELETE FROM Internship WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    await db.commit()
    return {"message": "Internship consultancy deleted."}


# Student: View Accepted Consultant Profiles
@consultancy_router.get("/study/approved", summary="Student: List all approved study consultants")
async def list_approved_study_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM Education WHERE status = 'accepted'"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

# Student: View Accepted Consultant Profiles
@consultancy_router.get("/internship/approved", summary="Student: List all approved internship consultants")
async def list_approved_internship_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM Internship WHERE status = 'accepted'"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

# Admin: View applications
@consultancy_router.get("/study", summary="Admin: View study applications by status")
async def get_study_applications(
    status: str = "pending",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"pending", "accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")

    result = await db.execute(text("SELECT * FROM Education WHERE status = :s"), {"s": status})
    return [dict(row._mapping) for row in result.fetchall()]



# Admin: View applications
@consultancy_router.get("/internship", summary="Admin: View internship applications by status")
async def get_internship_applications(
    status: str = "pending",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"pending", "accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")

    result = await db.execute(text("SELECT * FROM Internship WHERE status = :s"), {"s": status})
    return [dict(row._mapping) for row in result.fetchall()]



# Admin: Approve or reject
@consultancy_router.patch("/study/{user_id}/status", summary="Admin: Update study application status")
async def update_study_status(
    user_id: int,
    status: str,
    short_note: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")

    # 1. Get proof file path
    result = await db.execute(text("SELECT proof_of_education FROM Education WHERE user_id = :uid"), {"uid": user_id})
    row = result.fetchone()
    if row and row.proof_of_education:
        filepath = Path("." + row.proof_of_education)  # prepend dot to match relative path like ./static/...
        if filepath.exists():
            try:
                filepath.unlink()
            except Exception as e:
                print(f"Failed to delete file {filepath}: {e}")

    # 2. Update status and remove file path
    await db.execute(text("""
        UPDATE Education
        SET status = :s,
            short_note = :note,
            verified_by = :vid,
            verified_at = CURRENT_TIMESTAMP,
            proof_of_education = NULL
        WHERE user_id = :uid
    """), {
        "s": status,
        "note": short_note,
        "vid": current_user["user_id"],
        "uid": user_id
    })
    await db.commit()
    return {"message": f"Study application {status} and document deleted."}


# Admin: Approve or reject
@consultancy_router.patch("/internship/{user_id}/status", summary="Admin: Update internship application status")
async def update_internship_status(
    user_id: int,
    status: str,
    short_note: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")

    result = await db.execute(text("SELECT proof_of_internship FROM Internship WHERE user_id = :uid"), {"uid": user_id})
    row = result.fetchone()
    if row and row.proof_of_internship:
        filepath = Path("." + row.proof_of_internship)
        if filepath.exists():
            try:
                filepath.unlink()
            except Exception as e:
                print(f"Failed to delete file {filepath}: {e}")

    await db.execute(text("""
        UPDATE Internship
        SET status = :s,
            short_note = :note,
            verified_by = :vid,
            verified_at = CURRENT_TIMESTAMP,
            proof_of_internship = NULL
        WHERE user_id = :uid
    """), {
        "s": status,
        "note": short_note,
        "vid": current_user["user_id"],
        "uid": user_id
    })
    await db.commit()
    return {"message": f"Internship application {status} and document deleted."}

# Admin: Manually delete outdated consultancy profiles
@consultancy_router.delete("/admin/cleanup-expired", summary="Admin: Manually delete outdated consultancy profiles")
async def manual_cleanup_expired(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")

    try:
        from app.consultancy.controller import delete_expired_consultancies
        await delete_expired_consultancies(db)
        return {"message": "Expired consultancy profiles deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

