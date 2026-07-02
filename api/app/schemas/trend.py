from datetime import date

from pydantic import BaseModel, Field, field_validator

_DISALLOWED_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "<script",
    "javascript:",
)


class TrendReportResponse(BaseModel):
    id: str
    user_id: str
    title: str
    summary: str | None = None
    source: str | None = None
    report_date: date | None = None


class LatestTrendsResponse(BaseModel):
    trends: list[TrendReportResponse] = Field(default_factory=list)


class RunTrendResearchRequest(BaseModel):
    creator_niche: str = Field(min_length=1, max_length=300)
    target_platforms: list[str] = Field(min_length=1, max_length=10)
    audience_description: str = Field(min_length=1, max_length=1200)

    @field_validator("creator_niche", "audience_description")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        cleaned = value.strip()
        lowered = cleaned.lower()
        for pattern in _DISALLOWED_PATTERNS:
            if pattern in lowered:
                raise ValueError("Input contains disallowed prompt-injection content.")
        return cleaned

    @field_validator("target_platforms")
    @classmethod
    def validate_target_platforms(cls, value: list[str]) -> list[str]:
        allowed = {"instagram", "tiktok", "youtube", "linkedin", "blog", "newsletter"}
        normalized: list[str] = []
        for platform in value:
            cleaned = platform.strip().lower()
            if not cleaned:
                continue
            if cleaned not in allowed:
                raise ValueError(f"Unsupported platform '{platform}'.")
            normalized.append(cleaned)
        if not normalized:
            raise ValueError("At least one target platform is required.")
        return normalized
