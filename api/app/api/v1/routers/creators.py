from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.creator import (
    CreatorProfileCreateRequest,
    CreatorProfileResponse,
    UpdateCreatorVoiceRequest,
    UpdateNicheRequest,
    UpdateTargetPlatformsRequest,
)
from app.services.creator_service import CreatorService

router = APIRouter(prefix="/creators")


def get_creator_service() -> CreatorService:
    return CreatorService()


@router.post("", response_model=CreatorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: CreatorProfileCreateRequest,
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.create_profile(payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=CreatorProfileResponse)
def get_profile(
    user_id: str,
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.get_profile(user_id=user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}/niche", response_model=CreatorProfileResponse)
def update_niche(
    user_id: str,
    payload: UpdateNicheRequest,
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_niche(user_id=user_id, niche=payload.niche)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}/target-platforms", response_model=CreatorProfileResponse)
def update_target_platforms(
    user_id: str,
    payload: UpdateTargetPlatformsRequest,
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_target_platforms(
            user_id=user_id, target_platforms=payload.target_platforms
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}/creator-voice", response_model=CreatorProfileResponse)
def update_creator_voice(
    user_id: str,
    payload: UpdateCreatorVoiceRequest,
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_creator_voice(user_id=user_id, creator_voice=payload.creator_voice)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
