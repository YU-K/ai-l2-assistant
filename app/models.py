from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TicketStatus(StrEnum):
    NEW = "new"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50))
    # В БД обычный VARCHAR, а не PG ENUM — новые статусы не потребуют ALTER TYPE
    status: Mapped[str] = mapped_column(String(20), server_default=TicketStatus.NEW.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
