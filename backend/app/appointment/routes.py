from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from typing import List
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.appointment.models import ConsultantAvailability, Appointment, AppointmentStatus
from app.appointment.schemas import ConsultantAvailabilityOut as Slot, AppointmentCreate, AppointmentOut
from fastapi import Body
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/appointment",
    tags=["appointment"],
)

# Consultant fetches their own timetable
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

# Consultant updates their own timetable
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

    # Delete old slots
    await db.execute(
        delete(ConsultantAvailability)
        .where(ConsultantAvailability.consultant_id == uid)
    )
    # Insert new slots
    for s in slots:
        db.add(ConsultantAvailability(
            consultant_id=uid,
            days_of_week=s.days_of_week,
            start_time=s.start_time,
            end_time=s.end_time
        ))
    await db.commit()
    return slots

# Student fetches a consultant's timetable
@router.get(
    "/consultant/timetable/{consultant_id}",
    response_model=List[Slot],
    summary="Fetch a consultant's availability"
)
async def get_consultant_timetable(
    consultant_id: int,
    db: AsyncSession = Depends(get_db)
):
    rows = (await db.execute(
        select(ConsultantAvailability)
        .where(ConsultantAvailability.consultant_id == consultant_id)
    )).scalars().all()
    return [
        {"days_of_week": r.days_of_week, "start_time": r.start_time, "end_time": r.end_time}
        for r in rows
    ]

# Student books an appointment (with overlap check)
@router.post("/book", response_model=AppointmentOut)
async def book_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(403, "Only students can book appointments")

    # Check for overlapping appointment for this consultant, date, and time
    q = select(Appointment).where(
        Appointment.consultant_id == data.consultant_id,
        Appointment.date == data.date,
        Appointment.status.in_(["pending", "upcoming"]),
        and_(
            Appointment.start_time < data.end_time,
            Appointment.end_time > data.start_time
        )
    )
    result = await db.execute(q)
    if result.scalars().first():
        raise HTTPException(409, "This slot is already booked or pending approval.")

    appt = Appointment(
        consultant_id=data.consultant_id,
        student_id=current_user["user_id"],
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        reason=data.reason,
        info=data.info,
        platform=data.platform,
        status=AppointmentStatus.pending
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt

# Student fetches their own appointments
from sqlalchemy.orm import joinedload

@router.get("/my-appointments", response_model=List[AppointmentOut])
async def get_my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = select(Appointment).options(joinedload(Appointment.consultant)).where(Appointment.student_id == current_user["user_id"])
    result = await db.execute(q)
    appointments = result.scalars().all()
    now = datetime.now()
    updated = False
    for appt in appointments:
        end_time = appt.end_time or appt.start_time
        appt_end = datetime.combine(appt.date, datetime.strptime(end_time, "%H:%M").time())
        if appt.status == "upcoming" and appt_end < now:
            appt.status = "previous"
            updated = True
        if hasattr(appt, "consultant") and appt.consultant:
            appt.consultant_name = f"{appt.consultant.first_name} {appt.consultant.last_name}"
        else:
            appt.consultant_name = ""
    if updated:
        await db.commit()
    return appointments

@router.post("/reject/{appointment_id}", response_model=AppointmentOut)
async def reject_appointment(
    appointment_id: int,
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    appt = await db.get(Appointment, appointment_id)
    if not appt or appt.consultant_id != current_user["user_id"]:
        raise HTTPException(403, "Not allowed")
    appt.status = AppointmentStatus.rejected
    appt.rejection_reason = reason
    await db.commit()
    await db.refresh(appt)
    return appt

@router.get("/consultant/{consultant_id}/appointments", response_model=List[AppointmentOut])
async def get_public_consultant_appointments(
    consultant_id: int,
    db: AsyncSession = Depends(get_db)
):
    q = select(Appointment).where(
        Appointment.consultant_id == consultant_id,
        Appointment.status.in_(["pending", "upcoming"])
    )
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/consultant/appointments", response_model=List[AppointmentOut])
async def get_consultant_appointments(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = select(Appointment).options(joinedload(Appointment.student)).where(Appointment.consultant_id == current_user["user_id"])
    result = await db.execute(q)
    appointments = result.scalars().all()
    now = datetime.now()
    updated = False
    for appt in appointments:
        # Use end_time if available, otherwise start_time
        end_time = appt.end_time or appt.start_time
        appt_end = datetime.combine(appt.date, datetime.strptime(end_time, "%H:%M").time())
        if appt.status == "upcoming" and appt_end < now:
            appt.status = "previous"
            updated = True
        if hasattr(appt, "student") and appt.student:
            appt.student_name = f"{appt.student.first_name} {appt.student.last_name}"
        else:
            appt.student_name = ""
    if updated:
        await db.commit()
    return appointments

from fastapi import Body

@router.post("/approve/{appointment_id}", response_model=AppointmentOut)
async def approve_appointment(
    appointment_id: int,
    meeting_link: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Only consultants can approve
    appt = await db.get(Appointment, appointment_id)
    if not appt or appt.consultant_id != current_user["user_id"]:
        raise HTTPException(403, "Not allowed")
    appt.status = "upcoming"
    appt.meeting_link = meeting_link
    await db.commit()
    await db.refresh(appt)
    return appt

from datetime import datetime, timedelta
from sqlalchemy.future import select

@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    reason: str = Body(..., embed=True)
):
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalars().first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user["user_id"] not in [appt.student_id, appt.consultant_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    meeting_dt = datetime.combine(appt.date, datetime.strptime(appt.start_time, "%H:%M").time())
    if meeting_dt - datetime.now() <= timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Cannot cancel less than 24h before meeting")
    appt.status = "rejected"
    appt.rejection_reason = reason
    await db.commit()
    return {"detail": "Appointment cancelled"}