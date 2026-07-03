from pydantic import BaseModel, Field, field_validator

_DISALLOWED_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "<script",
    "javascript:",
)


class CoachChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        lowered = cleaned.lower()
        for pattern in _DISALLOWED_PATTERNS:
            if pattern in lowered:
                raise ValueError("Question contains disallowed prompt-injection content.")
        return cleaned


class CoachChatResponse(BaseModel):
    direct_coaching_response: str
    recommended_next_actions: list[str] = Field(default_factory=list)
    content_ideas: list[str] = Field(default_factory=list)
    risk_warning: str | None = None
    agent_run_id: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
