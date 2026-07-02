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


class YouTubeProvider(BaseSocialProvider):
    platform = "youtube"
    display_name = "YouTube"

    SCOPES = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/yt-analytics.readonly",
    ]

    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.google_client_id and settings.google_client_secret and settings.google_redirect_uri)

    def build_connect_url(self, *, state: str) -> str:
        settings = get_settings()
        if not self.is_configured():
            raise SocialProviderNotConfiguredError("YouTube OAuth is not configured.")

        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    async def exchange_code(self, *, code: str) -> OAuthTokens:
        settings = get_settings()
        payload = await self._post_form(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        return self._tokens_from_payload(payload)

    async def refresh_token(self, *, refresh_token: str) -> OAuthTokens:
        settings = get_settings()
        payload = await self._post_form(
            "https://oauth2.googleapis.com/token",
            {
                "refresh_token": refresh_token,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "grant_type": "refresh_token",
            },
        )
        tokens = self._tokens_from_payload(payload)
        if tokens.refresh_token is None:
            return OAuthTokens(
                access_token=tokens.access_token,
                refresh_token=refresh_token,
                expires_at=tokens.expires_at,
                scopes=tokens.scopes,
            )
        return tokens

    async def get_profile(self, *, access_token: str) -> SocialProfile:
        payload = await self._get_json(
            "https://www.googleapis.com/youtube/v3/channels",
            params={"part": "snippet,statistics", "mine": "true"},
            access_token=access_token,
        )
        items = payload.get("items") or []
        if not items:
            raise SocialProviderError("No YouTube channel found for this account.")

        channel = items[0]
        snippet = channel.get("snippet") or {}
        statistics = channel.get("statistics") or {}
        channel_id = channel.get("id")
        custom_url = snippet.get("customUrl")
        title = snippet.get("title")
        username = f"@{custom_url.lstrip('@')}" if custom_url else title

        return SocialProfile(
            platform_user_id=channel_id if isinstance(channel_id, str) else None,
            username=username if isinstance(username, str) else None,
            display_name=title if isinstance(title, str) else None,
            metadata={
                "subscriber_count": statistics.get("subscriberCount"),
                "view_count": statistics.get("viewCount"),
                "video_count": statistics.get("videoCount"),
                "thumbnail": ((snippet.get("thumbnails") or {}).get("default") or {}).get("url"),
            },
        )

    async def get_posts(self, *, access_token: str, platform_user_id: str | None = None) -> list[SocialPost]:
        params: dict[str, Any] = {
            "part": "snippet,statistics,contentDetails",
            "mine": "true",
            "maxResults": 10,
            "order": "date",
        }
        payload = await self._get_json(
            "https://www.googleapis.com/youtube/v3/search",
            params={**params, "type": "video"},
            access_token=access_token,
        )
        video_ids = [item.get("id", {}).get("videoId") for item in payload.get("items") or []]
        video_ids = [video_id for video_id in video_ids if isinstance(video_id, str)]
        if not video_ids:
            return []

        details = await self._get_json(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
            },
            access_token=access_token,
        )

        posts: list[SocialPost] = []
        for item in details.get("items") or []:
            snippet = item.get("snippet") or {}
            statistics = item.get("statistics") or {}
            video_id = item.get("id")
            posts.append(
                SocialPost(
                    id=str(video_id),
                    title=snippet.get("title"),
                    url=f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
                    published_at=snippet.get("publishedAt"),
                    metrics={
                        "views": statistics.get("viewCount"),
                        "likes": statistics.get("likeCount"),
                        "comments": statistics.get("commentCount"),
                    },
                    metadata={"description": snippet.get("description")},
                )
            )
        return posts

    async def get_analytics(
        self,
        *,
        access_token: str,
        platform_user_id: str | None = None,
    ) -> SocialAnalytics:
        if not platform_user_id:
            profile = await self.get_profile(access_token=access_token)
            platform_user_id = profile.platform_user_id
        if not platform_user_id:
            raise SocialProviderError("YouTube channel id is required for analytics.")

        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=28)
        try:
            payload = await self._get_json(
                "https://youtubeanalytics.googleapis.com/v2/reports",
                params={
                    "ids": f"channel=={platform_user_id}",
                    "startDate": start_date.isoformat(),
                    "endDate": end_date.isoformat(),
                    "metrics": "views,estimatedMinutesWatched,subscribersGained,averageViewDuration",
                },
                access_token=access_token,
            )
            rows = payload.get("rows") or []
            headers = [column.get("name") for column in payload.get("columnHeaders") or []]
            summary = dict(zip(headers, rows[0], strict=False)) if rows else {}
            return SocialAnalytics(
                summary=summary,
                period={"start": start_date.isoformat(), "end": end_date.isoformat()},
                metadata={"source": "youtube_analytics_api"},
            )
        except SocialProviderError:
            profile = await self.get_profile(access_token=access_token)
            posts = await self.get_posts(access_token=access_token, platform_user_id=platform_user_id)
            total_views = sum(int(post.metrics.get("views") or 0) for post in posts)
            return SocialAnalytics(
                summary={
                    "views": total_views,
                    "video_count": profile.metadata.get("video_count"),
                    "subscriber_count": profile.metadata.get("subscriber_count"),
                    "note": "YouTube Analytics API unavailable; returning channel summary fallback.",
                },
                period={"start": start_date.isoformat(), "end": end_date.isoformat()},
                metadata={"source": "youtube_data_api_fallback"},
            )

    @staticmethod
    def _tokens_from_payload(payload: dict[str, Any]) -> OAuthTokens:
        access_token = payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise SocialProviderError("Provider did not return an access token.")

        expires_in = payload.get("expires_in")
        expires_at = None
        if isinstance(expires_in, (int, float)):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

        refresh_token = payload.get("refresh_token")
        scope_value = payload.get("scope")
        scopes = scope_value.split(" ") if isinstance(scope_value, str) else YouTubeProvider.SCOPES
        return OAuthTokens(
            access_token=access_token,
            refresh_token=refresh_token if isinstance(refresh_token, str) else None,
            expires_at=expires_at,
            scopes=scopes,
        )

    @staticmethod
    async def _post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, data=data)
        if response.status_code >= 400:
            raise SocialProviderError(f"YouTube token request failed: {response.text}")
        return response.json()

    @staticmethod
    async def _get_json(url: str, *, params: dict[str, Any], access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code >= 400:
            raise SocialProviderError(f"YouTube API request failed: {response.text}")
        return response.json()
