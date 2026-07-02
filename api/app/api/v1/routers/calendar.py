from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.schemas.calendar import (
    CalendarItemResponse,
    CreateCalendarItemRequest,
    ListCalendarItemsResponse,
    MoveCalendarItemDateRequest,
    UpdateCalendarItemStatusRequest,
)
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar")


class DeleteCalendarItemResponse(BaseModel):
    deleted: bool


def get_calendar_service() -> CalendarService:
    return CalendarService()


@router.post("", response_model=CalendarItemResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_content_item(
    payload: CreateCalendarItemRequest,
    service: CalendarService = Depends(get_calendar_service),
) -> CalendarItemResponse:
    return service.create_item(payload)


@router.get("", response_model=ListCalendarItemsResponse)
def list_calendar_items(
    user_id: str = Query(..., min_length=1),
    limit: int = Query(default=100, ge=1, le=500),
    service: CalendarService = Depends(get_calendar_service),
) -> ListCalendarItemsResponse:
    return service.list_items(user_id=user_id, limit=limit)


@router.patch("/{item_id}/status", response_model=CalendarItemResponse)
def update_item_status(
    item_id: str,
    payload: UpdateCalendarItemStatusRequest,
    service: CalendarService = Depends(get_calendar_service),
) -> CalendarItemResponse:
    try:
        return service.update_status(item_id=item_id, status=payload.status)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{item_id}/move-date", response_model=CalendarItemResponse)
def move_item_date(
    item_id: str,
    payload: MoveCalendarItemDateRequest,
    service: CalendarService = Depends(get_calendar_service),
) -> CalendarItemResponse:
    try:
        return service.move_item_date(item_id=item_id, scheduled_for=payload.scheduled_for)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{item_id}", response_model=DeleteCalendarItemResponse)
def delete_item(
    item_id: str,
    service: CalendarService = Depends(get_calendar_service),
) -> DeleteCalendarItemResponse:
    try:
        result = service.delete_item(item_id=item_id)
        return DeleteCalendarItemResponse(deleted=result.deleted)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
