from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db import get_db
from app.auth.models import User
from app.consultancy.models import Education, Internship
from app.auth.token_verification import get_current_user
from app.support.models import SupportTicket
from app.appointment.models import Appointment

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)

def require_admin(user=Depends(get_current_user)):
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access only"
        )
    return user

@router.get("/users", summary="Admin: Get user statistics (by role and status)")
async def get_user_statistics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    # Count by role
    stmt_roles = select(
        User.role,
        func.count(User.id)
    ).group_by(User.role)
    result_roles = await db.execute(stmt_roles)
    roles_count = {role: count for role, count in result_roles.all()}

    # Count by status
    stmt_status = select(
        User.is_active,
        func.count(User.id)
    ).group_by(User.is_active)
    result_status = await db.execute(stmt_status)
    status_count = {status: count for status, count in result_status.all()}

    # Count by role & status combination
    stmt_combo = select(
        User.role,
        User.is_active,
        func.count(User.id)
    ).group_by(User.role, User.is_active)
    result_combo = await db.execute(stmt_combo)
    role_status_details = {}
    for role, status, count in result_combo.all():
        if role not in role_status_details:
            role_status_details[role] = {}
        role_status_details[role][status] = count

    return {
        "roles_count": roles_count,
        "status_count": status_count,
        "role_status_details": role_status_details
    }


@router.get("/consultancies", summary="Admin: Get consultancy profile statistics")
async def get_consultancy_statistics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    # Study consultancies by status
    stmt_study_status = select(Education.status, func.count(Education.user_id)).group_by(Education.status)
    res_study_status = await db.execute(stmt_study_status)
    study_status_counts = {status: count for status, count in res_study_status.all()}

    # Internship consultancies by status
    stmt_internship_status = select(Internship.status, func.count(Internship.user_id)).group_by(Internship.status)
    res_internship_status = await db.execute(stmt_internship_status)
    internship_status_counts = {status: count for status, count in res_internship_status.all()}

    # Total accepted profiles
    total_accepted = study_status_counts.get("accepted", 0) + internship_status_counts.get("accepted", 0)

    return {
        "study_consultancies": {
            "total": sum(study_status_counts.values()),
            "accepted": study_status_counts.get("accepted", 0),
            "status_breakdown": study_status_counts
        },
        "internship_consultancies": {
            "total": sum(internship_status_counts.values()),
            "accepted": internship_status_counts.get("accepted", 0),
            "status_breakdown": internship_status_counts
        },
        "overall_total": sum(study_status_counts.values()) + sum(internship_status_counts.values()),
        "overall_status_counts": {
            "accepted": total_accepted,
            "pending": study_status_counts.get("pending", 0) + internship_status_counts.get("pending", 0),
            "rejected": study_status_counts.get("rejected", 0) + internship_status_counts.get("rejected", 0),
        },
        "overall_accepted_total": total_accepted
    }


@router.get("/support-tickets", summary="Admin: Get support ticket statistics")
async def get_support_ticket_statistics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    # Total tickets
    stmt_total = select(func.count(SupportTicket.id))
    total_tickets = await db.scalar(stmt_total)

    # Tickets by status
    stmt_status = select(SupportTicket.status, func.count(SupportTicket.id)).group_by(SupportTicket.status)
    res_status = await db.execute(stmt_status)
    status_counts = {status: count for status, count in res_status.all()}

    # Tickets by submitter role
    stmt_roles = select(User.role, func.count(SupportTicket.id)).join(User, SupportTicket.user_id == User.id).group_by(User.role)
    res_roles = await db.execute(stmt_roles)
    submitter_role_counts = {role: count for role, count in res_roles.all()}

    return {
        "total_tickets": total_tickets,
        "status_counts": status_counts,
        "submitter_role_counts": submitter_role_counts
    }


@router.get("/appointments/summary", summary="Get global appointment statistics")
async def get_appointment_summary(db: AsyncSession = Depends(get_db)):
    # Total count
    total = await db.execute(select(func.count(Appointment.id)))
    total_count = total.scalar()

    # By status
    status_result = await db.execute(
        select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)
    )
    status_counts = dict(status_result.all())

    # By type
    type_result = await db.execute(
        select(Appointment.type, func.count(Appointment.id)).group_by(Appointment.type)
    )
    type_counts = dict(type_result.all())

    return {
        "total_appointments": total_count,
        "status_counts": status_counts,
        "type_counts": type_counts,
    }
