from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class SocialProviderError(Exception):
    pass


class SocialProviderNotConfiguredError(SocialProviderError):
    pass


@dataclass(frozen=True, slots=True)
class OAuthTokens:
    access_token: str
    refresh_token: str | None
    expires_at: datetime | None
    scopes: list[str]


@dataclass(frozen=True, slots=True)
class SocialProfile:
    platform_user_id: str | None
    username: str | None
    display_name: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SocialPost:
    id: str
    title: str | None
    url: str | None
    published_at: str | None
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SocialAnalytics:
    summary: dict[str, Any]
    period: dict[str, str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseSocialProvider(ABC):
    platform: str
    display_name: str

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def build_connect_url(self, *, state: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def exchange_code(self, *, code: str) -> OAuthTokens:
        raise NotImplementedError

    @abstractmethod
    async def refresh_token(self, *, refresh_token: str) -> OAuthTokens:
        raise NotImplementedError

    @abstractmethod
    async def get_profile(self, *, access_token: str) -> SocialProfile:
        raise NotImplementedError

    @abstractmethod
    async def get_posts(self, *, access_token: str, platform_user_id: str | None = None) -> list[SocialPost]:
        raise NotImplementedError

    @abstractmethod
    async def get_analytics(
        self,
        *,
        access_token: str,
        platform_user_id: str | None = None,
    ) -> SocialAnalytics:
        raise NotImplementedError

    async def publish_post(self, *, access_token: str, content: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"{self.display_name} publish is not implemented yet.")

    async def schedule_post(
        self,
        *,
        access_token: str,
        content: dict[str, Any],
        scheduled_for: datetime,
    ) -> dict[str, Any]:
        raise NotImplementedError(f"{self.display_name} scheduling is not implemented yet.")
