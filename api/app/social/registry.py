from __future__ import annotations

from app.social.base import BaseSocialProvider, SocialProviderError
from app.social.instagram import InstagramProvider
from app.social.youtube import YouTubeProvider

_PROVIDERS: dict[str, BaseSocialProvider] = {
    InstagramProvider.platform: InstagramProvider(),
    YouTubeProvider.platform: YouTubeProvider(),
}


def get_social_provider(platform: str) -> BaseSocialProvider:
    provider = _PROVIDERS.get(platform)
    if provider is None:
        raise SocialProviderError(f"Unsupported platform: {platform}")
    return provider


def list_social_providers() -> list[BaseSocialProvider]:
    return list(_PROVIDERS.values())
