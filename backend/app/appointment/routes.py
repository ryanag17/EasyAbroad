from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, func
from typing import List
from app.db import get_db
from app.auth.token_verification import get_current_user
from app.consultancy.models import Education, Internship
from app.appointment.models import ConsultantAvailability, Appointment, AppointmentStatus, ConsultantReview
from app.appointment.schemas import ConsultantAvailabilityOut as Slot, AppointmentCreate, AppointmentOut, ReviewCreate, ReviewOut
from fastapi import Body
from sqlalchemy.orm import Session, selectinload
from app.auth.models import User
from app.notification.models import Notification
import uuid

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
@router.get("/consultant/timetable/{consultant_public_id}", response_model=List[Slot], summary="Fetch a consultant's availability")
async def get_consultant_timetable(
    consultant_public_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Resolve consultant_id from Education
    result = await db.execute(
        select(User.id)
        .join(Education, Education.user_id == User.id)
        .where(Education.public_id == consultant_public_id)
    )
    row = result.first()

    # If not found, try Internship
    if row is None:
        result = await db.execute(
            select(User.id)
            .join(Internship, Internship.user_id == User.id)
            .where(Internship.public_id == consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]

    rows = (await db.execute(
        select(ConsultantAvailability)
        .where(ConsultantAvailability.consultant_id == consultant_id)
    )).scalars().all()

    return [
        {"days_of_week": r.days_of_week, "start_time": r.start_time, "end_time": r.end_time}
        for r in rows
    ]



# Student books an appointment (with overlap check) (with notification)
@router.post("/book", response_model=AppointmentOut, summary="Student: book appointment (with notification)")
async def book_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "student":
        raise HTTPException(403, "Only students can book appointments")

    # Lookup consultant_id using public_id
    # First try Education
    result = await db.execute(
        select(User.id)
        .join(User.education)
        .where(Education.public_id == data.consultant_public_id)
    )
    row = result.first()

    if row is None:
        # Try Internship
        result = await db.execute(
            select(User.id)
            .join(User.internship)
            .where(Internship.public_id == data.consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]


    # Check for overlapping appointment
    q = select(Appointment).where(
        Appointment.consultant_id == consultant_id,
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

    # Create appointment
    appt = Appointment(
        public_id=str(uuid.uuid4()),
        consultant_id=consultant_id,
        consultant_public_id=data.consultant_public_id,
        student_id=current_user["user_id"],
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        reason=data.reason,
        info=data.info,
        platform=data.platform,
        status=AppointmentStatus.pending,
        type=data.type
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)

    # Create notification
    student = await db.get(User, current_user["user_id"])
    student_name = f"{student.first_name} {student.last_name}" if student else "the student"

    notif_content = (
        f"You have received a new appointment request from {student_name} "
        f"for {data.date}, {data.start_time}-{data.end_time}."
    )
    new_notif = Notification(
        user_id=consultant_id,
        content=notif_content,
        type="info",
        redirect_url="/consultant/appointments.html"
    )
    db.add(new_notif)
    await db.commit()
    await db.refresh(new_notif)

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

# Consultant: reject appointment request (with notification)
@router.post("/reject/{public_id}", response_model=AppointmentOut, summary="Consultant: reject appointment request (with notification)")
async def reject_appointment(
    public_id: str,
    reason: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Find by public_id
    result = await db.execute(select(Appointment).where(Appointment.public_id == public_id))
    appt = result.scalar_one_or_none()
    if not appt or appt.consultant_id != current_user["user_id"]:
        raise HTTPException(403, "Not allowed")
    
    appt.status = AppointmentStatus.rejected
    appt.rejection_reason = reason

    # Get consultant's name
    consultant = await db.get(User, appt.consultant_id)
    consultant_name = f"{consultant.first_name} {consultant.last_name}" if consultant else "the consultant"

    # Create notification for student
    notif_content = f"Your appointment request for {consultant_name} has been rejected."
    new_notif = Notification(
        user_id=appt.student_id,
        content=notif_content,
        type="info",
        redirect_url="/student/appointments.html"
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(appt)
    await db.refresh(new_notif)
    return appt


@router.get("/consultant/{consultant_public_id}/appointments", response_model=List[AppointmentOut])
async def get_public_consultant_appointments(
    consultant_public_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Resolve consultant_id using Education first
    result = await db.execute(
        select(User.id)
        .join(Education, Education.user_id == User.id)
        .where(Education.public_id == consultant_public_id)
    )
    row = result.first()

    # If not found, try Internship
    if row is None:
        result = await db.execute(
            select(User.id)
            .join(Internship, Internship.user_id == User.id)
            .where(Internship.public_id == consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]

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

# Consultant: approve the appointment request (with notification)
@router.post("/approve/{public_id}", response_model=AppointmentOut, summary="Consultant: approve appointment")
async def approve_appointment(
    public_id: str,
    meeting_link: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(select(Appointment).where(Appointment.public_id == public_id))
    appt = result.scalar_one_or_none()
    if not appt or appt.consultant_id != current_user["user_id"]:
        raise HTTPException(403, "Not allowed")

    if not meeting_link.startswith("http://") and not meeting_link.startswith("https://"):
        meeting_link = "https://" + meeting_link    
    appt.status = "upcoming"
    appt.meeting_link = meeting_link

    consultant = await db.get(User, appt.consultant_id)
    consultant_name = f"{consultant.first_name} {consultant.last_name}" if consultant else "the consultant"

    notif_content = f"Your appointment request for {consultant_name} has been approved."
    new_notif = Notification(
        user_id=appt.student_id,
        content=notif_content,
        type="info",
        redirect_url="/student/appointments.html"
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(appt)
    await db.refresh(new_notif)
    return appt


from datetime import datetime, timedelta
from sqlalchemy.future import select

# Cancel appointment (with notification)
@router.post("/{public_id}/cancel", summary="Cancel appointment (with notification)")
async def cancel_appointment(
    public_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    reason: str = Body(..., embed=True)
):
    # Use public_id to find the appointment
    result = await db.execute(select(Appointment).where(Appointment.public_id == public_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if current_user["user_id"] not in [appt.student_id, appt.consultant_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    meeting_dt = datetime.combine(appt.date, datetime.strptime(appt.start_time, "%H:%M").time())
    if meeting_dt - datetime.now() <= timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Cannot cancel less than 24h before meeting")

    appt.status = AppointmentStatus.rejected
    appt.cancellation_reason = reason

    # Determine recipient
    if current_user["user_id"] == appt.student_id:
        recipient_id = appt.consultant_id
        who = "student"
    else:
        recipient_id = appt.student_id
        who = "consultant"

    notif_content = f"Your appointment has been canceled by the {who}."
    new_notif = Notification(
        user_id=recipient_id,
        content=notif_content,
        type="info",
        redirect_url="/student/appointments.html" if who == "consultant" else "/consultant/appointments"
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(new_notif)
    return {"detail": "Appointment cancelled"}


# Allows only students to submit reviews after appointment is done and doesn't allow multiple reviews (with notification)
@router.post("/review", response_model=ReviewOut, summary="Student: Submit Review (with notification)")
async def submit_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(select(Appointment).where(Appointment.public_id == data.public_id))
    booking = result.scalar_one_or_none()

    if not booking or booking.student_id != current_user["user_id"]:
        raise HTTPException(403, "Unauthorized to review this appointment.")

    # Check for existing review
    result = await db.execute(
        select(ConsultantReview).where(ConsultantReview.booking_id == booking.id)
    )
    existing_review = result.scalar()
    if existing_review:
        raise HTTPException(400, "Review already submitted for this appointment.")

    review = ConsultantReview(
        public_id=str(uuid.uuid4()),
        booking_id=booking.id,
        student_id=current_user["user_id"],
        consultant_id=booking.consultant_id,
        rating=data.rating,
        review_text=data.review_text
    )
    db.add(review)

    # Notification
    student = await db.get(User, current_user["user_id"])
    student_name = f"{student.first_name} {student.last_name}" if student else "A student"

    notif_content = f"You have received a new review from {student_name}."
    new_notif = Notification(
        user_id=booking.consultant_id,
        content=notif_content,
        type="info",
        redirect_url="/consultant/reviews.html"
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(review)
    await db.refresh(new_notif)

    return review


# Calculates average rating and number of reviews per consultant.
@router.get("/consultant/public/{consultant_public_id}/consultant-average-rating", summary="Student: Calculate and show average rating and number of reviews of consultant.")
async def get_consultant_average_rating(
    consultant_public_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Resolve consultant_id from public_id
    result = await db.execute(
        select(User.id)
        .join(Education, Education.user_id == User.id)
        .where(Education.public_id == consultant_public_id)
    )
    row = result.first()

    if row is None:
        result = await db.execute(
            select(User.id)
            .join(Internship, Internship.user_id == User.id)
            .where(Internship.public_id == consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]
    result = await db.execute(
        select(func.avg(ConsultantReview.rating), func.count(ConsultantReview.id))
        .where(ConsultantReview.consultant_id == consultant_id)
    )
    avg, count = result.first()
    return {
        "average_rating": round(avg or 0, 2),
        "total_reviews": count
    }



# On the student view, shows the ratings/reviews for the consultant being viewed.
@router.get("/consultant/public/{consultant_public_id}/reviews", response_model=List[ReviewOut], summary="Student: Get reviews by consultant public ID")
async def get_consultant_reviews_by_public_id(
    consultant_public_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Try Education first
    result = await db.execute(
        select(User.id)
        .join(Education, Education.user_id == User.id)
        .where(Education.public_id == consultant_public_id)
    )
    row = result.first()

    if row is None:
        # Try Internship
        result = await db.execute(
            select(User.id)
            .join(Internship, Internship.user_id == User.id)
            .where(Internship.public_id == consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]

    result = await db.execute(
        select(ConsultantReview)
        .options(selectinload(ConsultantReview.student))
        .where(ConsultantReview.consultant_id == consultant_id)
    )
    reviews = result.scalars().all()

    output = []
    for r in reviews:
        student_name = None
        if r.student:
            student_name = f"{r.student.first_name} {r.student.last_name}"
        output.append(
            ReviewOut(
                id=r.id,
                public_id=r.public_id,
                booking_id=r.booking_id,
                student_id=r.student_id,
                consultant_id=r.consultant_id,
                rating=r.rating,
                review_text=r.review_text,
                submitted_at=r.submitted_at,
                student_name=student_name,
            )
        )
    return output


# Basic consultant info is gathered from the student's appointment.
@router.get("/booking/{public_id}/consultant", summary="Student: Fetch basic consultant info from appointment.")
async def get_consultant_info_from_booking(
    public_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(select(Appointment).where(Appointment.public_id == public_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.student_id != current_user["user_id"]:
        raise HTTPException(403, "Unauthorized")
    
    consultant = await db.get(User, booking.consultant_id)
    if not consultant:
        raise HTTPException(404, "Consultant not found")
    
    return {
        "consultant_id": consultant.id,
        "first_name": consultant.first_name,
        "last_name": consultant.last_name
    }

# Shows student the review and rating they had already given to consultant after appointment.
@router.get("/review/{public_id}", summary="Student: Show already written review.")
async def get_review_by_booking(
    public_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(ConsultantReview)
        .join(Appointment, ConsultantReview.booking_id == Appointment.id)
        .where(
            (Appointment.public_id == public_id) &
            (ConsultantReview.student_id == current_user["user_id"])
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return {
        "id": review.id,
        "rating": review.rating,
        "review_text": review.review_text,
        "submitted_at": review.submitted_at.isoformat()
    }


# Shows average rating of consultant.
@router.get("/consultant/public/{consultant_public_id}/average-rating", summary="Consultant/Student: Average rating of consultant.")
async def get_average_rating(
    consultant_public_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Try Education first
    result = await db.execute(
        select(User.id)
        .join(Education, Education.user_id == User.id)
        .where(Education.public_id == consultant_public_id)
    )
    row = result.first()

    if row is None:
        # Try Internship
        result = await db.execute(
            select(User.id)
            .join(Internship, Internship.user_id == User.id)
            .where(Internship.public_id == consultant_public_id)
        )
        row = result.first()

    if row is None:
        raise HTTPException(404, "Consultant not found")

    consultant_id = row[0]

    # Calculate average and total reviews
    result = await db.execute(
        select(func.avg(ConsultantReview.rating), func.count(ConsultantReview.id))
        .where(ConsultantReview.consultant_id == consultant_id)
    )
    avg, count = result.first()
    return {
        "average_rating": round(avg, 2) if avg is not None else None,
        "total_reviews": count
    }



# Allows consultants to view reviews written about them.
@router.get("/consultant/reviews/me", response_model=List[ReviewOut], summary="Consultant: view my reviews.")
async def get_my_consultant_reviews(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "consultant":
        raise HTTPException(403, "Not a consultant")

    result = await db.execute(
        select(ConsultantReview)
        .options(selectinload(ConsultantReview.student))
        .where(ConsultantReview.consultant_id == current_user["user_id"])
    )
    reviews = result.scalars().all()

    output = []
    for r in reviews:
        student_name = None
        if r.student:
            student_name = f"{r.student.first_name} {r.student.last_name}"
        output.append(
            ReviewOut(
                id=r.id,
                public_id=r.public_id,                
                booking_id=r.booking_id,
                student_id=r.student_id,
                consultant_id=r.consultant_id,
                rating=r.rating,
                review_text=r.review_text,
                submitted_at=r.submitted_at,
                student_name=student_name,
            )
        )
    return output


@router.get("/by-public-id/{public_id}")
async def get_appointment_by_public_id(public_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Appointment).where(Appointment.public_id == public_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(404, "Appointment not found")
    return {"id": appt.id}