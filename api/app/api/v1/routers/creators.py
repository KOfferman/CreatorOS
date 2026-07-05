from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import AuthenticatedUser, require_authenticated_user
from app.schemas.creator import (
    CreatorProfileCreateRequest,
    CreatorProfileResponse,
    SaveCreatorSettingsRequest,
    UpdateCreatorVoiceRequest,
    UpdateNicheRequest,
    UpdateTargetPlatformsRequest,
    UpdateUserRequest,
)
from app.services.creator_service import CreatorService

router = APIRouter(prefix="/creators")


def get_creator_service() -> CreatorService:
    return CreatorService()


@router.post("", response_model=CreatorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: CreatorProfileCreateRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.create_profile(user_id=user.user_id, payload=payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/me", response_model=CreatorProfileResponse)
def get_my_profile(
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.get_profile(user_id=user.user_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/me/niche", response_model=CreatorProfileResponse)
def update_my_niche(
    payload: UpdateNicheRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_niche(user_id=user.user_id, niche=payload.niche)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/me/target-platforms", response_model=CreatorProfileResponse)
def update_my_target_platforms(
    payload: UpdateTargetPlatformsRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_target_platforms(
            user_id=user.user_id, target_platforms=payload.target_platforms
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/me/creator-voice", response_model=CreatorProfileResponse)
def update_my_creator_voice(
    payload: UpdateCreatorVoiceRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_creator_voice(
            user_id=user.user_id, creator_voice=payload.creator_voice
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/me/user", response_model=CreatorProfileResponse)
def update_my_user(
    payload: UpdateUserRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.update_user(user_id=user.user_id, user=payload.user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/me/settings", response_model=CreatorProfileResponse)
def save_my_settings(
    payload: SaveCreatorSettingsRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: CreatorService = Depends(get_creator_service),
) -> CreatorProfileResponse:
    try:
        return service.save_settings(user_id=user.user_id, payload=payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
