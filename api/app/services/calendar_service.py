from dataclasses import dataclass

from database import ContentCalendarItem

from app.repositories.calendar_repository import CalendarRepository
from app.schemas.calendar import (
    CalendarItemResponse,
    CreateCalendarItemRequest,
    ListCalendarItemsResponse,
)


@dataclass(frozen=True, slots=True)
class DeleteCalendarItemResult:
    deleted: bool


class CalendarService:
    def __init__(self, repository: CalendarRepository | None = None) -> None:
        self.repository = repository or CalendarRepository()

    def create_item(self, *, user_id: str, payload: CreateCalendarItemRequest) -> CalendarItemResponse:
        item = self.repository.create_item(
            user_id=user_id,
            content_idea_id=payload.content_idea_id,
            platform=payload.platform,
            scheduled_for=payload.scheduled_for,
            status=payload.status,
            notes=payload.notes,
        )
        return self._to_response(item)

    def list_items(self, *, user_id: str, limit: int = 100) -> ListCalendarItemsResponse:
        items = self.repository.list_items(user_id=user_id, limit=limit)
        return ListCalendarItemsResponse(items=[self._to_response(item) for item in items])

    def update_status(self, *, item_id: str, user_id: str, status: str) -> CalendarItemResponse:
        item = self.repository.update_status(item_id=item_id, user_id=user_id, status=status)
        if item is None:
            raise LookupError("Calendar item not found.")
        return self._to_response(item)

    def move_item_date(self, *, item_id: str, user_id: str, scheduled_for) -> CalendarItemResponse:
        item = self.repository.move_item_date(
            item_id=item_id, user_id=user_id, scheduled_for=scheduled_for
        )
        if item is None:
            raise LookupError("Calendar item not found.")
        return self._to_response(item)

    def delete_item(self, *, item_id: str, user_id: str) -> DeleteCalendarItemResult:
        deleted = self.repository.delete_item(item_id=item_id, user_id=user_id)
        if not deleted:
            raise LookupError("Calendar item not found.")
        return DeleteCalendarItemResult(deleted=True)

    @staticmethod
    def _to_response(item: ContentCalendarItem) -> CalendarItemResponse:
        return CalendarItemResponse(
            id=item.id,
            user_id=item.user_id,
            content_idea_id=item.content_idea_id,
            platform=item.platform,
            scheduled_for=item.scheduled_for,
            status=item.status,  # validated by response schema Literal
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
