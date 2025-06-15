from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, text
from datetime import datetime, timezone
from sqlalchemy import join
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.db import get_db
from app.auth.token_verification import get_current_user
from app.support.schemas import SupportTicketCreate, SupportTicketResponse
from app.support.models import SupportTicket, TicketStatus

support_router = APIRouter(prefix="/support", tags=["Support"])

# Create a support ticket (student or consultant)
@support_router.post("/", status_code=201)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        new_ticket = SupportTicket(
            user_id=current_user["user_id"],
            subject=ticket.subject,
            description=ticket.description,
            status="open",  # or use TicketStatus.open if you have an Enum defined
            created_at=datetime.utcnow().replace(tzinfo=timezone.utc),
            updated_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
        db.add(new_ticket)
        await db.commit()
        await db.refresh(new_ticket)  # get the ticket ID and state after commit
        return {
            "message": "Support ticket created successfully.",
            "ticket_id": new_ticket.id
        }
    except Exception as e:
         await db.rollback()  
         raise HTTPException(status_code=500, detail=f"Failed to create support ticket: {str(e)}")
    


# List all support tickets (admin only)

@support_router.get("/tickets")
async def list_support_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    query = """
        SELECT 
            st.id, st.subject, st.description, st.status, st.created_at,
            u.first_name AS user_first_name, u.last_name AS user_last_name
        FROM support_tickets st
        JOIN users u ON st.user_id = u.id
        ORDER BY st.created_at DESC
    """

    result = await db.execute(text(query))
    tickets = [
        dict(row._mapping) for row in result.fetchall()
    ]
    return tickets

# Get support tickets of the current user (student or consultant)
@support_router.get("/me", response_model=list[SupportTicketResponse])
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.user_id == current_user["user_id"])
    )
    tickets = result.scalars().all()
    return tickets


from app.support.schemas import SupportTicketDetailResponse
from app.support.models import SupportTicket, SupportTicketMessage

@support_router.get("/{ticket_id}", response_model=SupportTicketDetailResponse)
async def get_ticket_by_id(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user["role"] != "admin" and ticket.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    messages_result = await db.execute(
        select(SupportTicketMessage).where(SupportTicketMessage.ticket_id == ticket_id).order_by(SupportTicketMessage.sent_at.asc())
    )
    messages = messages_result.scalars().all()

    initial_message = {
        "id": 0,
        "ticket_id": ticket.id,
        "sender_id": ticket.user_id,
        "message": ticket.description,
        "created_at": ticket.created_at,
        "sender_role": "user",
        "sender_name": "You"  # or actual user name if preferred
    }

    formatted_messages = [
        {
            "id": m.id,
            "ticket_id": m.ticket_id,
            "sender_id": m.sender_id,
            "message": m.message,
            "created_at": m.sent_at,
            "sender_role": "admin" if m.sender_id != ticket.user_id else "user",
            "sender_name": "Admin" if m.sender_id != ticket.user_id else "You"
        }
        for m in messages
    ]

    return {
        "id": ticket.id,
        "user_id": ticket.user_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "resolved_by": ticket.resolved_by,
        "resolved_at": ticket.resolved_at,
        "replies": [initial_message] + formatted_messages
    }


from app.support.models import SupportTicketMessage
from app.support.schemas import TicketReplyCreate

@support_router.post("/{ticket_id}/reply")
async def post_ticket_reply(
    ticket_id: int,
    reply: TicketReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user["role"] != "admin" and current_user["user_id"] != ticket.user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    new_message = SupportTicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user["user_id"],
        message=reply.message
    )
    db.add(new_message)
    await db.commit()
    return {"message": "Reply sent successfully"}


@support_router.patch("/{ticket_id}/status")
async def update_ticket_status(ticket_id: int, status_update: dict, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update status")
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = status_update.get("status", ticket.status)
    ticket.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Status updated"}
