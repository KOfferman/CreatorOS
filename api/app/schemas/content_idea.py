from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_DISALLOWED_PROMPT_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "<script",
    "javascript:",
)


def _guard_text_input(value: str, field_name: str) -> str:
    normalized = value.strip()
    if len(normalized) > 2000:
        raise ValueError(f"{field_name} is too long.")
    lowered = normalized.lower()
    for pattern in _DISALLOWED_PROMPT_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"{field_name} contains disallowed content.")
    return normalized


class GenerateContentIdeaRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    platform: str = Field(min_length=1, max_length=120)
    creator_voice: str = Field(min_length=1, max_length=600)
    goal: str = Field(min_length=1, max_length=600)
    audience: str = Field(min_length=1, max_length=600)

    @field_validator("topic", "platform", "creator_voice", "goal", "audience")
    @classmethod
    def validate_inputs(cls, value: str, info):
        return _guard_text_input(value, info.field_name)


class GeneratedContentIdeaResponse(BaseModel):
    title: str
    description: str
    suggested_score: float = Field(ge=0.0, le=100.0)
    status: str = "draft"


class SaveContentIdeaRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=6000)
    trend_report_id: str | None = None
    score: float | None = Field(default=None, ge=0.0, le=100.0)
    status: str = "draft"

    @field_validator("title", "status")
    @classmethod
    def validate_required_strings(cls, value: str, info):
        return _guard_text_input(value, info.field_name)

    @field_validator("description")
    @classmethod
    def validate_optional_description(cls, value: str | None):
        if value is None:
            return None
        return _guard_text_input(value, "description")


class ContentIdeaResponse(BaseModel):
    id: str
    user_id: str
    trend_report_id: str | None = None
    title: str
    description: str | None = None
    status: str
    score: float | None = None
    created_at: datetime
    updated_at: datetime


class ListContentIdeasResponse(BaseModel):
    ideas: list[ContentIdeaResponse] = Field(default_factory=list)


class UpdateContentIdeaStatusRequest(BaseModel):
    status: str = Field(min_length=1)
