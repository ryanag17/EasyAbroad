from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from datetime import datetime

from app.db import get_db
from app.auth.token_verification import get_current_user
from app.support.schemas import SupportTicketCreate, SupportTicketResponse
from app.support.models import SupportTicket

support_router = APIRouter(prefix="/support", tags=["Support"])

# Create a support ticket (student or consultant)
@support_router.post("/", status_code=201)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        stmt = insert(SupportTicket).values(
            user_id=current_user["user_id"],
            subject=ticket.subject,
            description=ticket.description,
            status="open",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await db.execute(stmt)
        await db.commit()
        return {"message": "Support ticket created successfully."}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create support ticket")

# List all support tickets (admin only)
@support_router.get("/", response_model=list[SupportTicketResponse])
async def list_support_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    result = await db.execute(select(SupportTicket))
    tickets = result.scalars().all()
    return tickets
