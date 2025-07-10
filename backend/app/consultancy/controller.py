from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.consultancy.models import Education, Internship
from app.consultancy.schemas import EducationCreate, InternshipCreate


from app.consultancy.models import Education
from datetime import datetime
from fastapi import HTTPException

async def save_study_entry(db: AsyncSession, user_id: int, data: EducationCreate):
    try:
        from_dt = datetime.strptime(data.fromDate + "-01", "%Y-%m-%d")
        to_dt = datetime.strptime(data.toDate + "-01", "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if to_dt < datetime.now().replace(year=datetime.now().year - 5):
        raise HTTPException(status_code=400, detail="Graduation must be within the last 5 years")

    help_flags = {
        "accommodation": "Accommodation" in data.help,
        "social_life": "Social" in data.help,
        "uni_info": "University Info" in data.help,
        "travel_info": "City Tips" in data.help
    }

    call_flags = {
        "zoom": "Zoom" in data.call,
        "microsoft_teams": "Teams" in data.call,
        "google_meet": "Google Meet" in data.call,
        "apple_facetime": "FaceTime" in data.call
    }

    new_entry = Education(
        user_id=user_id,
        city_of_study=data.city,
        country_of_study=data.country,
        university_name=data.university,
        course_name=data.course,
        education_start=from_dt,
        education_finish=to_dt,
        proof_of_education=data.proof_url,
        status="pending",
        short_note=None,
        **help_flags,
        **call_flags
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    return {"message": "Study consultancy profile submitted successfully", "public_id": new_entry.public_id}


from app.consultancy.models import Internship
from datetime import datetime
from fastapi import HTTPException

async def save_internship_entry(db: AsyncSession, user_id: int, data: InternshipCreate):
    try:
        from_dt = datetime.strptime(data.fromDate + "-01", "%Y-%m-%d")
        to_dt = datetime.strptime(data.toDate + "-01", "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    if to_dt < datetime.now().replace(year=datetime.now().year - 5):
        raise HTTPException(status_code=400, detail="Internship must be within the last 5 years")

    help_flags = {
        "accommodation": "Accommodation" in data.help,
        "social_life": "Social" in data.help,
        "company_info": "Company Info" in data.help,
        "travel_info": "City Tips" in data.help
    }

    call_flags = {
        "zoom": "Zoom" in data.call,
        "microsoft_teams": "Teams" in data.call,
        "google_meet": "Google Meet" in data.call,
        "apple_facetime": "FaceTime" in data.call
    }

    new_entry = Internship(
        user_id=user_id,
        city_of_internship=data.city,
        country_of_internship=data.country,
        company_name=data.company,
        department_name=data.department,
        internship_start=from_dt,
        internship_finish=to_dt,
        proof_of_internship=data.proof_url,
        status="pending",
        short_note=None,
        **help_flags,
        **call_flags
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    return {"message": "Internship consultancy profile submitted successfully", "public_id": new_entry.public_id}


from sqlalchemy import delete, select
from app.db import get_db
from app.consultancy.models import Education, Internship
import os
from datetime import datetime, timedelta

async def delete_expired_consultancies(db: AsyncSession):
    five_years_ago = datetime.utcnow() - timedelta(days=5*365)

    # Fetch and delete outdated education profiles
    expired_educations = await db.execute(
        select(Education).where(Education.education_finish < five_years_ago)
    )
    for edu in expired_educations.scalars():
        if edu.proof_of_education:
            try:
                file_path = f"./backend{edu.proof_of_education}"
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"[Education] File delete error: {e}")
        await db.execute(delete(Education).where(Education.user_id == edu.user_id))

    # Fetch and delete outdated internship profiles
    expired_internships = await db.execute(
        select(Internship).where(Internship.internship_finish < five_years_ago)
    )
    for intern in expired_internships.scalars():
        if intern.proof_of_internship:
            try:
                file_path = f"./backend{intern.proof_of_internship}"
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"[Internship] File delete error: {e}")
        await db.execute(delete(Internship).where(Internship.user_id == intern.user_id))

    await db.commit()
