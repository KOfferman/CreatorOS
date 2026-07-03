from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.social.base import (
    BaseSocialProvider,
    OAuthTokens,
    SocialAnalytics,
    SocialPost,
    SocialProfile,
    SocialProviderError,
    SocialProviderNotConfiguredError,
)


class InstagramProvider(BaseSocialProvider):
    platform = "instagram"
    display_name = "Instagram"

    AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
    TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    GRAPH_URL = "https://graph.instagram.com"

    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(
            settings.meta_app_id
            and settings.meta_app_secret
            and settings.instagram_config_id
            and settings.meta_redirect_uri
        )

    def build_connect_url(self, *, state: str) -> str:
        settings = get_settings()
        if not self.is_configured():
            raise SocialProviderNotConfiguredError("Instagram OAuth is not configured.")

        params = {
            "client_id": settings.meta_app_id,
            "redirect_uri": settings.meta_redirect_uri,
            "response_type": "code",
            "config_id": settings.instagram_config_id,
            "state": state,
        }
        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, *, code: str) -> OAuthTokens:
        settings = get_settings()
        payload = await self._post_form(
            self.TOKEN_URL,
            {
                "client_id": settings.meta_app_id,
                "client_secret": settings.meta_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": settings.meta_redirect_uri,
                "code": code,
            },
        )
        return self._tokens_from_payload(payload)

    async def refresh_token(self, *, refresh_token: str) -> OAuthTokens:
        settings = get_settings()
        payload = await self._get_json(
            f"{self.GRAPH_URL}/refresh_access_token",
            params={
                "grant_type": "ig_refresh_token",
                "access_token": refresh_token,
            },
        )
        return self._tokens_from_payload(payload, fallback_refresh_token=refresh_token)

    async def get_profile(self, *, access_token: str) -> SocialProfile:
        payload = await self._get_json(
            f"{self.GRAPH_URL}/me",
            params={"fields": "id,username,name,account_type,media_count", "access_token": access_token},
        )
        username = payload.get("username")
        display_name = payload.get("name") or username
        return SocialProfile(
            platform_user_id=str(payload["id"]) if payload.get("id") is not None else None,
            username=f"@{username}" if isinstance(username, str) and not username.startswith("@") else username,
            display_name=display_name if isinstance(display_name, str) else None,
            metadata={
                "account_type": payload.get("account_type"),
                "media_count": payload.get("media_count"),
            },
        )

    async def get_posts(self, *, access_token: str, platform_user_id: str | None = None) -> list[SocialPost]:
        payload = await self._get_json(
            f"{self.GRAPH_URL}/me/media",
            params={
                "fields": "id,caption,permalink,timestamp,like_count,comments_count",
                "access_token": access_token,
            },
        )
        posts: list[SocialPost] = []
        for item in payload.get("data") or []:
            posts.append(
                SocialPost(
                    id=str(item.get("id")),
                    title=item.get("caption"),
                    url=item.get("permalink"),
                    published_at=item.get("timestamp"),
                    metrics={
                        "likes": item.get("like_count"),
                        "comments": item.get("comments_count"),
                    },
                )
            )
        return posts

    async def get_analytics(
        self,
        *,
        access_token: str,
        platform_user_id: str | None = None,
    ) -> SocialAnalytics:
        profile = await self.get_profile(access_token=access_token)
        posts = await self.get_posts(access_token=access_token, platform_user_id=platform_user_id)
        total_likes = sum(int(post.metrics.get("likes") or 0) for post in posts)
        total_comments = sum(int(post.metrics.get("comments") or 0) for post in posts)
        return SocialAnalytics(
            summary={
                "media_count": profile.metadata.get("media_count"),
                "recent_post_count": len(posts),
                "recent_likes": total_likes,
                "recent_comments": total_comments,
            },
            metadata={"source": "instagram_graph_api"},
        )

    @staticmethod
    def _tokens_from_payload(payload: dict[str, Any], *, fallback_refresh_token: str | None = None) -> OAuthTokens:
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise SocialProviderError("Instagram did not return an access token.")

        expires_in = payload.get("expires_in")
        expires_at = None
        if isinstance(expires_in, (int, float)):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

        refresh_token = payload.get("refresh_token")
        if not isinstance(refresh_token, str):
            refresh_token = fallback_refresh_token

        return OAuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scopes=[],
        )

    @staticmethod
    async def _post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, data=data)
        if response.status_code >= 400:
            raise SocialProviderError(f"Instagram token request failed: {response.text}")
        return response.json()

    @staticmethod
    async def _get_json(url: str, *, params: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params)
        if response.status_code >= 400:
            raise SocialProviderError(f"Instagram API request failed: {response.text}")
        return response.json()
