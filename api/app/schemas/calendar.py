from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

CalendarStatus = Literal["idea", "draft", "scheduled", "published"]


class CreateCalendarItemRequest(BaseModel):
    content_idea_id: str | None = None
    platform: str | None = None
    scheduled_for: datetime
    status: CalendarStatus = "scheduled"
    notes: str | None = None


class CalendarItemResponse(BaseModel):
    id: str
    user_id: str
    content_idea_id: str | None = None
    platform: str | None = None
    scheduled_for: datetime | None = None
    status: CalendarStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ListCalendarItemsResponse(BaseModel):
    items: list[CalendarItemResponse] = Field(default_factory=list)


class UpdateCalendarItemStatusRequest(BaseModel):
    status: CalendarStatus


class MoveCalendarItemDateRequest(BaseModel):
    scheduled_for: datetime
