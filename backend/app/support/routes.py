from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime, timezone
import uuid

from app.db import get_db
from app.auth.models import User
from app.auth.token_verification import get_current_user
from app.support.schemas import SupportTicketCreate, SupportTicketResponse, TicketReplyCreate
from app.support.models import SupportTicket, SupportTicketMessage
from app.notification.models import Notification

support_router = APIRouter(prefix="/support", tags=["Support"])

# Student or Consultant: Create a support ticket (with notification)
@support_router.post("/", summary="Student or Consultant: Create a support ticket (with notification)", status_code=201)
async def create_support_ticket(
    ticket: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        new_ticket = SupportTicket(
            public_id=str(uuid.uuid4()),
            user_id=current_user["user_id"],
            subject=ticket.subject,
            description=ticket.description,
            status="open",
            created_at=datetime.utcnow().replace(tzinfo=timezone.utc),
            updated_at=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
        db.add(new_ticket)

        notif_content = f"A new support ticket '{ticket.subject}' has been created."
        admin_users = await db.execute(select(User).where(User.role == "admin"))
        for admin_user in admin_users.scalars().all():
            new_notif = Notification(
                user_id=admin_user.id,
                content=notif_content,
                type="info",
                redirect_url="/admin/support-tickets.html"
            )
            db.add(new_notif)

        await db.commit()
        await db.refresh(new_ticket)

        return {
            "message": "Support ticket created successfully.",
            "ticket_id": new_ticket.public_id  # ← send public_id to frontend
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
            st.id, st.public_id, st.subject, st.description, st.status, st.created_at,
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
@support_router.get("/me", summary="Student or Consultant: Get support tickets of the current user", response_model=list[SupportTicketResponse])
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.user_id == current_user["user_id"])
    )
    tickets = result.scalars().all()
    return tickets


# Admin: Get single support ticket by public_id
@support_router.get("/{ticket_id}", summary="Admin: Get support tickets of the current user")
async def get_ticket_by_id(
    ticket_id: str,  # now using public_id
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
        WHERE st.public_id = :ticket_id
    """
    result = await db.execute(text(query), {"ticket_id": ticket_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket_dict = dict(row._mapping)

    if current_user["role"] != "admin" and current_user["user_id"] != ticket_dict["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    messages_result = await db.execute(
        select(SupportTicketMessage).where(SupportTicketMessage.ticket_id == ticket_dict["id"]).order_by(SupportTicketMessage.sent_at.asc())
    )
    messages = messages_result.scalars().all()

    initial_message = {
        "id": 0,
        "ticket_id": ticket_dict["public_id"],
        "sender_id": ticket_dict["user_id"],
        "message": ticket_dict["description"],
        "created_at": ticket_dict["created_at"],
        "sender_role": "user",
        "sender_name": "You" if current_user["user_id"] == ticket_dict["user_id"] else f"{ticket_dict['user_first_name']} {ticket_dict['user_last_name']}"
    }

    formatted_messages = [
        {
            "id": m.id,
            "ticket_id": ticket_dict["public_id"],
            "sender_id": m.sender_id,
            "message": m.message,
            "created_at": m.sent_at,
            "sender_role": "admin" if m.sender_id != ticket_dict["user_id"] else "user",
            "sender_name": "Admin" if m.sender_id != ticket_dict["user_id"] else "You"
        }
        for m in messages
    ]

    return {
        "id": ticket_dict["public_id"],
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


# All users: Reply to ticket
@support_router.post("/{ticket_id}/reply", summary="All users: Reply ticket (with notification)")
async def post_ticket_reply(
    ticket_id: str,
    reply: TicketReplyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SupportTicket).where(SupportTicket.public_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user["role"] != "admin" and current_user["user_id"] != ticket.user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    new_message = SupportTicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user["user_id"],
        message=reply.message
    )
    db.add(new_message)

    if current_user["role"] == "admin":
        notif_content = f"You have received a new reply from admin on your support ticket '{ticket.subject}'."
        user = await db.get(User, ticket.user_id)
        user_folder = "student" if user.role == "student" else "consultant"
        new_notif = Notification(
            user_id=ticket.user_id,
            content=notif_content,
            type="info",
            redirect_url=f"/{user_folder}/ticket-detail.html?id={ticket.public_id}"
        )
        db.add(new_notif)
    else:
        notif_content = f"A new reply was posted on ticket '{ticket.subject}' by the user."
        admin_users = await db.execute(select(User).where(User.role == "admin"))
        for admin_user in admin_users.scalars().all():
            new_notif = Notification(
                user_id=admin_user.id,
                content=notif_content,
                type="info",
                redirect_url=f"/admin/ticket-detail.html?id={ticket.public_id}"
            )
            db.add(new_notif)

    await db.commit()
    await db.refresh(new_message)

    return {"message": "Reply sent successfully"}


# Admin: Update ticket status
@support_router.patch("/{ticket_id}/status", summary="Admin: Update support ticket status (with notification)")
async def update_ticket_status(
    ticket_id: str,
    status_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update status")

    result = await db.execute(select(SupportTicket).where(SupportTicket.public_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    user = await db.get(User, ticket.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Ticket owner not found.")

    new_status = status_update.get("status", ticket.status)
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()

    if new_status in ("resolved", "closed"):
        ticket.resolved_by = current_user["user_id"]
        ticket.resolved_at = datetime.utcnow()

    notif_content = f"The status of your support ticket '{ticket.subject}' has been updated to '{new_status}'."
    user_folder = "student" if user.role == "student" else "consultant"
    new_notif = Notification(
        user_id=ticket.user_id,
        content=notif_content,
        type="info",
        redirect_url=f"/{user_folder}/ticket-detail.html?id={ticket.public_id}"
    )
    db.add(new_notif)

    await db.commit()
    await db.refresh(new_notif)

    return {"message": "Status updated"}
