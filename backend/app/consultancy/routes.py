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

    file_path = user_dir / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/uploads/proof_documents/{category}/user_{user_id}/{file.filename}"

@consultancy_router.post("/upload-proof/study", summary="Upload proof of study")
async def upload_study_proof(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    relative_path = save_proof_file(file, user_id, "study")
    return {"message": "Study proof uploaded successfully", "path": relative_path}

@consultancy_router.post("/upload-proof/internship", summary="Upload proof of internship")
async def upload_internship_proof(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    relative_path = save_proof_file(file, user_id, "internship")
    return {"message": "Internship proof uploaded successfully", "path": relative_path}

from fastapi import Form, File, UploadFile

@consultancy_router.post("/study", summary="Submit education consultancy")
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


@consultancy_router.post("/internship", summary="Submit internship consultancy")
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
@consultancy_router.get("/study/me", summary="Get current user's study consultancy")
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
@consultancy_router.delete("/study", summary="Delete current user's study consultancy")
async def delete_my_study_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await db.execute(text("DELETE FROM Education WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    await db.commit()
    return {"message": "Study consultancy deleted."}

# Consultant: View Their Own Submitted Application
@consultancy_router.get("/internship/me", summary="Get current user's internship consultancy")
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
@consultancy_router.delete("/internship", summary="Delete current user's internship consultancy")
async def delete_my_internship_consultancy(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    await db.execute(text("DELETE FROM Internship WHERE user_id = :uid"), {"uid": current_user["user_id"]})
    await db.commit()
    return {"message": "Internship consultancy deleted."}


# Student: View Accepted Consultant Profiles
@consultancy_router.get("/study/approved", summary="List all approved study consultants")
async def list_approved_study_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM Education WHERE status = 'accepted'"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

# Student: View Accepted Consultant Profiles
@consultancy_router.get("/internship/approved", summary="List all approved internship consultants")
async def list_approved_internship_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM Internship WHERE status = 'accepted'"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

# Admin: View all pending applications
@consultancy_router.get("/study/pending", summary="Admin: View pending study applications")
async def get_pending_study(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    result = await db.execute(text("SELECT * FROM Education WHERE status = 'pending'"))
    return [dict(row._mapping) for row in result.fetchall()]

# Admin: View all pending applications
@consultancy_router.get("/internship/pending", summary="Admin: View pending internship applications")
async def get_pending_internship(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    result = await db.execute(text("SELECT * FROM Internship WHERE status = 'pending'"))
    return [dict(row._mapping) for row in result.fetchall()]

# Admin: Approve or reject
@consultancy_router.patch("/study/{user_id}/status", summary="Admin: Update study application status")
async def update_study_status(
    user_id: int,
    status: str,  # should be 'approved' or 'rejected'
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")
    await db.execute(text("UPDATE Education SET status = :s WHERE user_id = :uid"), {"s": status, "uid": user_id})
    await db.commit()
    return {"message": f"Application {status}."}

# Admin: Approve or reject
@consultancy_router.patch("/internship/{user_id}/status", summary="Admin: Update internship application status")
async def update_internship_status(
    user_id: int,
    status: str,  # should be 'approved' or 'rejected'
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized.")
    if status not in {"accepted", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status.")
    await db.execute(text("UPDATE Internship SET status = :s WHERE user_id = :uid"), {"s": status, "uid": user_id})
    await db.commit()
    return {"message": f"Application {status}."}