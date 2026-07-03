from pydantic import BaseModel, Field


class CreatorProfileCreateRequest(BaseModel):
    handle: str = Field(min_length=1)
    niche: str | None = None
    bio: str | None = None
    target_platforms: list[str] = Field(default_factory=list)
    creator_voice: str | None = None
    audience_size: int | None = Field(default=None, ge=0)


class CreatorProfileResponse(BaseModel):
    id: str
    user_id: str
    handle: str
    niche: str | None = None
    bio: str | None = None
    target_platforms: list[str] = Field(default_factory=list)
    creator_voice: str | None = None
    audience_size: int | None = None


class UpdateNicheRequest(BaseModel):
    niche: str = Field(min_length=1)


class UpdateTargetPlatformsRequest(BaseModel):
    target_platforms: list[str] = Field(min_length=1)


class UpdateCreatorVoiceRequest(BaseModel):
    creator_voice: str = Field(min_length=1)
