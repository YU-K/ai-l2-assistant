from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TicketStatus


class TicketCreate(BaseModel):
    # status, created_at и id задаёт сервер — клиент не может их передать
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    source: str = Field(min_length=1, max_length=50)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    source: str
    status: TicketStatus
    created_at: datetime
