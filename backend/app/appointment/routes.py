from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.db import get_db
from app.auth.token_verification import get_current_user
from app.appointment.models import ConsultantAvailability
from app.appointment.schemas import ConsultantAvailabilityOut as Slot

router = APIRouter(
    prefix="/appointment",
    tags=["appointment"],
)

@router.get(
    "/consultant/timetable",
    response_model=List[Slot],
    summary="Fetch my current availability"
)
async def get_timetable(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "consultant":
        raise HTTPException(403, "Not a consultant")
    rows = (await db.execute(
        select(ConsultantAvailability)
        .where(ConsultantAvailability.consultant_id == current_user["user_id"])
    )).scalars().all()
    return [
        {"days_of_week": r.days_of_week, "start_time": r.start_time, "end_time": r.end_time}
        for r in rows
    ]


@router.put(
    "/consultant/timetable",
    response_model=List[Slot],
    summary="Overwrite my availability"
)
async def update_timetable(
    slots: List[Slot],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "consultant":
        raise HTTPException(403, "Not a consultant")
    uid = current_user["user_id"]

    # deleting the old one
    await db.execute(
        delete(ConsultantAvailability)
        .where(ConsultantAvailability.consultant_id == uid)
    )
    # inserting new
    for s in slots:
        db.add(ConsultantAvailability(
            consultant_id=uid,
            days_of_week=s.days_of_week,
            start_time=s.start_time,
            end_time=s.end_time
        ))
    await db.commit()

    # returning what we saved
    return slots
