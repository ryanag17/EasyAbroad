# app/consultancy/controller.py
from datetime import datetime
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.consultancy.models import Education, Internship
from app.consultancy.schemas import StudyConsultancyRequest, InternshipConsultancyRequest


async def save_study_entry(db: AsyncSession, user_id: int, data: StudyConsultancyRequest):
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

    stmt = insert(Education).values(
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

    await db.execute(stmt)
    await db.commit()

    return {"message": "Study consultancy profile submitted successfully"}

async def save_internship_entry(db: AsyncSession, user_id: int, data: InternshipConsultancyRequest):
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

    stmt = insert(Internship).values(
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

    await db.execute(stmt)
    await db.commit()

    return {"message": "Internship consultancy profile submitted successfully"}
