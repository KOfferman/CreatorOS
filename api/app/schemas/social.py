from __future__ import annotations

from pydantic import BaseModel, Field


class PlatformConnectionResponse(BaseModel):
    platform: str
    name: str
    connected: bool
    configured: bool
    account_handle: str | None = None
    account_name: str | None = None
    connected_at: str | None = None


class PlatformConnectionsResponse(BaseModel):
    platforms: list[PlatformConnectionResponse]


class PlatformConnectResponse(BaseModel):
    authorization_url: str
    platform: str


class PlatformDisconnectResponse(BaseModel):
    platform: str
    disconnected: bool = Field(default=True)
