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

# Student or Consultant: Create a support ticket
@support_router.post("/", summary="Student or Consultant: Create a support ticket", status_code=201)
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
            status="open",
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
    


# Admin: List all support tickets
@support_router.get("/tickets", summary="Admin: List all support tickets")
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

# Student or Consultant: Get support tickets of the current user
@support_router.get("/me", summary="Student or Consultant: Get support tickets of the current user",response_model=list[SupportTicketResponse])
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

# Admin: Get support tickets of the current user
@support_router.get("/{ticket_id}", summary="Admin: Get support tickets of the current user")
async def get_ticket_by_id(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = """
        SELECT 
            st.*, 
            u.first_name AS user_first_name, 
            u.last_name AS user_last_name, 
            u.email AS user_email
        FROM support_tickets st
        JOIN users u ON st.user_id = u.id
        WHERE st.id = :ticket_id
    """
    result = await db.execute(text(query), {"ticket_id": ticket_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_dict = dict(row._mapping)

    # Permission check
    if current_user["role"] != "admin" and current_user["user_id"] != ticket_dict["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Fetch replies
    messages_result = await db.execute(
        select(SupportTicketMessage).where(SupportTicketMessage.ticket_id == ticket_id).order_by(SupportTicketMessage.sent_at.asc())
    )
    messages = messages_result.scalars().all()

    # Initial description as first message
    initial_message = {
        "id": 0,
        "ticket_id": ticket_dict["id"],
        "sender_id": ticket_dict["user_id"],
        "message": ticket_dict["description"],
        "created_at": ticket_dict["created_at"],
        "sender_role": "user",
        "sender_name": "You" if current_user["user_id"] == ticket_dict["user_id"] else f"{ticket_dict['user_first_name']} {ticket_dict['user_last_name']}"
    }

    formatted_messages = [
        {
            "id": m.id,
            "ticket_id": m.ticket_id,
            "sender_id": m.sender_id,
            "message": m.message,
            "created_at": m.sent_at,
            "sender_role": "admin" if m.sender_id != ticket_dict["user_id"] else "user",
            "sender_name": "Admin" if m.sender_id != ticket_dict["user_id"] else "You"
        }
        for m in messages
    ]

    return {
        "id": ticket_dict["id"],
        "user_id": ticket_dict["user_id"],
        "subject": ticket_dict["subject"],
        "description": ticket_dict["description"],
        "status": ticket_dict["status"],
        "created_at": ticket_dict["created_at"],
        "updated_at": ticket_dict["updated_at"],
        "resolved_by": ticket_dict["resolved_by"],
        "resolved_at": ticket_dict["resolved_at"],
        "user_full_name": f"{ticket_dict['user_first_name']} {ticket_dict['user_last_name']}".strip(),
        "user_email": ticket_dict["user_email"],
        "replies": [initial_message] + formatted_messages
    }



from app.support.models import SupportTicketMessage
from app.support.schemas import TicketReplyCreate

# All users: Reply ticket
@support_router.post("/{ticket_id}/reply", summary="All users: Reply ticket")
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

# Admin: Update support ticket status
@support_router.patch("/{ticket_id}/status", summary="Admin: Update support ticket status")
async def update_ticket_status(
    ticket_id: int,
    status_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update status")

    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    new_status = status_update.get("status", ticket.status)
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()

    if new_status in ("resolved", "closed"):
        ticket.resolved_by = current_user["user_id"]
        ticket.resolved_at = datetime.utcnow()

    await db.commit()
    return {"message": "Status updated"}
