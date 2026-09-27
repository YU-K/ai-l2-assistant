from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Ticket
from app.schemas import TicketCreate, TicketRead

router = APIRouter(prefix="/tickets", tags=["tickets"])

Session = Annotated[AsyncSession, Depends(get_session)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, session: Session) -> TicketRead:
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    await session.commit()
    # status и created_at заполняет БД — подтягиваем их после вставки
    await session.refresh(ticket)
    return TicketRead.model_validate(ticket)


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: int, session: Session) -> TicketRead:
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return TicketRead.model_validate(ticket)
