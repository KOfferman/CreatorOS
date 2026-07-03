from fastapi import APIRouter, Depends, HTTPException, status

from ai_core import AIProviderError

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AIProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Coach LLM unavailable ({service.settings.llm_provider}): {exc}",
        ) from exc
