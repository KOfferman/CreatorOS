from __future__ import annotations

from urllib.parse import quote

from app.core.config import get_settings
from app.repositories.social_account_repository import SocialAccountRepository
from app.schemas.social import (
    PlatformConnectResponse,
    PlatformConnectionResponse,
    PlatformConnectionsResponse,
    PlatformDisconnectResponse,
)
from app.social.base import SocialProviderError, SocialProviderNotConfiguredError
from app.social.oauth_service import create_oauth_state
from app.social.registry import get_social_provider, list_social_providers


class SocialService:
    def __init__(self, repository: SocialAccountRepository | None = None) -> None:
        self.repository = repository or SocialAccountRepository()

    def list_platforms(self, *, user_id: str) -> PlatformConnectionsResponse:
        accounts = {account.platform: account for account in self.repository.list_for_user(user_id=user_id)}
        platforms: list[PlatformConnectionResponse] = []
        for provider in list_social_providers():
            account = accounts.get(provider.platform)
            metadata = account.metadata_json if account and account.metadata_json else {}
            platforms.append(
                PlatformConnectionResponse(
                    platform=provider.platform,
                    name=provider.display_name,
                    connected=account is not None,
                    configured=provider.is_configured(),
                    account_handle=account.username if account else None,
                    account_name=(metadata.get("display_name") if isinstance(metadata, dict) else None)
                    or (account.username if account else None),
                    connected_at=account.connected_at.isoformat() if account else None,
                )
            )
        return PlatformConnectionsResponse(platforms=platforms)

    def start_connect(self, *, user_id: str, platform: str) -> PlatformConnectResponse:
        provider = get_social_provider(platform)
        if not provider.is_configured():
            raise SocialProviderNotConfiguredError(f"{provider.display_name} OAuth is not configured.")
        state = create_oauth_state(user_id=user_id, platform=platform)
        return PlatformConnectResponse(
            authorization_url=provider.build_connect_url(state=state),
            platform=platform,
        )

    async def complete_connect(self, *, user_id: str, platform: str, code: str) -> None:
        provider = get_social_provider(platform)
        tokens = await provider.exchange_code(code=code)
        profile = await provider.get_profile(access_token=tokens.access_token)
        self.repository.upsert_connection(
            user_id=user_id,
            platform=platform,
            platform_user_id=profile.platform_user_id,
            username=profile.username,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_at=tokens.expires_at,
            scopes=tokens.scopes,
            metadata={"display_name": profile.display_name, **profile.metadata},
        )

    def disconnect(self, *, user_id: str, platform: str) -> PlatformDisconnectResponse:
        get_social_provider(platform)
        disconnected = self.repository.delete_for_user(user_id=user_id, platform=platform)
        if not disconnected:
            raise SocialProviderError(f"{platform} is not connected.")
        return PlatformDisconnectResponse(platform=platform)

    @staticmethod
    def frontend_redirect(*, status: str, platform: str, message: str | None = None) -> str:
        settings = get_settings()
        params = f"status={quote(status)}&platform={quote(platform)}"
        if message:
            params += f"&message={quote(message)}"
        return f"{settings.auth_url.rstrip('/')}/settings?{params}"
