from fastapi import APIRouter, Depends, HTTPException

from app.schemas.coach import CoachChatRequest, CoachChatResponse
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach")


def get_coach_service() -> CoachService:
    return CoachService()


@router.post("/chat", response_model=CoachChatResponse)
def coach_chat(
    payload: CoachChatRequest,
    service: CoachService = Depends(get_coach_service),
) -> CoachChatResponse:
    try:
        return service.chat(payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
