from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.core.dependencies import AuthenticatedUser, require_authenticated_user
from app.schemas.social import (
    PlatformConnectResponse,
    PlatformConnectionsResponse,
    PlatformDisconnectResponse,
)
from app.services.social_service import SocialService
from app.social.base import SocialProviderError, SocialProviderNotConfiguredError
from app.social.oauth_service import verify_oauth_state

router = APIRouter(prefix="/integrations")
legacy_social_router = APIRouter(prefix="/social")


def get_social_service() -> SocialService:
    return SocialService()


@router.get("/platforms", response_model=PlatformConnectionsResponse)
def list_platforms(
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: SocialService = Depends(get_social_service),
) -> PlatformConnectionsResponse:
    return service.list_platforms(user_id=user.user_id)


@router.post("/platforms/{platform}/connect", response_model=PlatformConnectResponse)
def start_platform_connect(
    platform: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: SocialService = Depends(get_social_service),
) -> PlatformConnectResponse:
    try:
        return service.start_connect(user_id=user.user_id, platform=platform)
    except SocialProviderNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except SocialProviderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/platforms/{platform}", response_model=PlatformDisconnectResponse)
def disconnect_platform(
    platform: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: SocialService = Depends(get_social_service),
) -> PlatformDisconnectResponse:
    try:
        return service.disconnect(user_id=user.user_id, platform=platform)
    except SocialProviderError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


async def _handle_oauth_callback(
    *,
    platform: str,
    code: str | None,
    state: str | None,
    error: str | None,
    error_description: str | None,
    service: SocialService,
) -> RedirectResponse:
    if error:
        message = error_description or error
        return RedirectResponse(
            url=service.frontend_redirect(status="error", platform=platform, message=message),
            status_code=status.HTTP_302_FOUND,
        )

    if not code or not state:
        return RedirectResponse(
            url=service.frontend_redirect(
                status="error",
                platform=platform,
                message="Missing OAuth code or state.",
            ),
            status_code=status.HTTP_302_FOUND,
        )

    try:
        user_id, expected_platform = verify_oauth_state(state)
        if expected_platform != platform:
            raise SocialProviderError("OAuth state platform mismatch.")
        await service.complete_connect(user_id=user_id, platform=platform, code=code)
    except SocialProviderError as exc:
        return RedirectResponse(
            url=service.frontend_redirect(status="error", platform=platform, message=str(exc)),
            status_code=status.HTTP_302_FOUND,
        )

    return RedirectResponse(
        url=service.frontend_redirect(status="connected", platform=platform),
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/oauth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
    service: SocialService = Depends(get_social_service),
) -> RedirectResponse:
    return await _handle_oauth_callback(
        platform=platform,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
        service=service,
    )


@legacy_social_router.get("/instagram/callback", include_in_schema=False)
async def legacy_instagram_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
    service: SocialService = Depends(get_social_service),
) -> RedirectResponse:
    return await _handle_oauth_callback(
        platform="instagram",
        code=code,
        state=state,
        error=error,
        error_description=error_description,
        service=service,
    )
