from pydantic import AliasChoices, BaseModel, Field

from app.schemas.creator_settings import CreatorSettings


class CreatorProfileCreateRequest(BaseModel):
    user: str = Field(min_length=1, validation_alias=AliasChoices("user", "handle"))
    niche: str | None = None
    bio: str | None = None
    target_platforms: list[str] = Field(default_factory=list)
    creator_voice: str | None = None
    audience_size: int | None = Field(default=None, ge=0)


class CreatorProfileResponse(BaseModel):
    id: str
    user_id: str
    user: str
    handle: str
    niche: str | None = None
    bio: str | None = None
    target_platforms: list[str] = Field(default_factory=list)
    creator_voice: str | None = None
    audience_size: int | None = None
    settings: CreatorSettings = Field(default_factory=CreatorSettings)


class UpdateUserRequest(BaseModel):
    user: str = Field(min_length=1)


class SaveCreatorSettingsRequest(BaseModel):
    user: str | None = None
    notification_prefs: dict[str, bool] | None = None
    ai_provider: str | None = None
    stripe_payout_status: str | None = None


class UpdateNicheRequest(BaseModel):
    niche: str = Field(min_length=1)


class UpdateTargetPlatformsRequest(BaseModel):
    target_platforms: list[str] = Field(min_length=1)


class UpdateCreatorVoiceRequest(BaseModel):
    creator_voice: str = Field(min_length=1)
