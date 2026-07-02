from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.schemas.content_idea import (
    ContentIdeaResponse,
    GenerateContentIdeaRequest,
    GeneratedContentIdeaResponse,
    ListContentIdeasResponse,
    SaveContentIdeaRequest,
    UpdateContentIdeaStatusRequest,
)
from app.services.content_idea_service import ContentIdeaService

router = APIRouter(prefix="/content-ideas")


class DeleteContentIdeaResponse(BaseModel):
    deleted: bool


def get_content_idea_service() -> ContentIdeaService:
    return ContentIdeaService()


@router.post("/generate", response_model=GeneratedContentIdeaResponse)
def generate_content_idea(
    payload: GenerateContentIdeaRequest,
    service: ContentIdeaService = Depends(get_content_idea_service),
) -> GeneratedContentIdeaResponse:
    return service.generate_content_idea(payload)


@router.get("", response_model=ListContentIdeasResponse)
def list_ideas(
    user_id: str = Query(..., min_length=1),
    limit: int = Query(default=50, ge=1, le=200),
    service: ContentIdeaService = Depends(get_content_idea_service),
) -> ListContentIdeasResponse:
    return service.list_ideas(user_id=user_id, limit=limit)


@router.post("", response_model=ContentIdeaResponse, status_code=status.HTTP_201_CREATED)
def save_idea(
    payload: SaveContentIdeaRequest,
    service: ContentIdeaService = Depends(get_content_idea_service),
) -> ContentIdeaResponse:
    return service.save_idea(payload)


@router.patch("/{idea_id}/status", response_model=ContentIdeaResponse)
def update_idea_status(
    idea_id: str,
    payload: UpdateContentIdeaStatusRequest,
    service: ContentIdeaService = Depends(get_content_idea_service),
) -> ContentIdeaResponse:
    try:
        return service.update_idea_status(idea_id=idea_id, status=payload.status)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{idea_id}", response_model=DeleteContentIdeaResponse)
def delete_idea(
    idea_id: str,
    service: ContentIdeaService = Depends(get_content_idea_service),
) -> DeleteContentIdeaResponse:
    try:
        result = service.delete_idea(idea_id=idea_id)
        return DeleteContentIdeaResponse(deleted=result.deleted)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
