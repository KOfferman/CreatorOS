from pydantic import BaseModel, Field, field_validator

_DISALLOWED_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "<script",
    "javascript:",
)


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        lowered = cleaned.lower()
        for pattern in _DISALLOWED_PATTERNS:
            if pattern in lowered:
                raise ValueError("Text contains disallowed prompt-injection content.")
        return cleaned


class TaskEnqueueResponse(BaseModel):
    task_id: str
    status: str = "queued"
