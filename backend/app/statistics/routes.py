from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db import get_db
from app.auth.models import User
from app.consultancy.models import Education, Internship
from app.auth.token_verification import get_current_user
from app.support.models import SupportTicket

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
    # Total study consultancy profiles
    stmt_study_total = select(func.count(Education.user_id))
    study_total = await db.scalar(stmt_study_total)

    # Study by status
    stmt_study_status = select(Education.status, func.count(Education.user_id)).group_by(Education.status)
    res_study_status = await db.execute(stmt_study_status)
    study_status_counts = {status: count for status, count in res_study_status.all()}

    # Total internship consultancy profiles
    stmt_internship_total = select(func.count(Internship.user_id))
    internship_total = await db.scalar(stmt_internship_total)

    # Internship by status
    stmt_internship_status = select(Internship.status, func.count(Internship.user_id)).group_by(Internship.status)
    res_internship_status = await db.execute(stmt_internship_status)
    internship_status_counts = {status: count for status, count in res_internship_status.all()}

    return {
        "study_consultancies": {
            "total": study_total,
            "status_breakdown": study_status_counts
        },
        "internship_consultancies": {
            "total": internship_total,
            "status_breakdown": internship_status_counts
        },
        "overall_total": study_total + internship_total
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

    # Tickets by user role
    stmt_roles = select(User.role, func.count(SupportTicket.id)).join(User, SupportTicket.user_id == User.id).group_by(User.role)
    res_roles = await db.execute(stmt_roles)
    role_counts = {role: count for role, count in res_roles.all()}

    return {
        "total_tickets": total_tickets,
        "status_counts": status_counts,
        "submitter_role_counts": role_counts
    }