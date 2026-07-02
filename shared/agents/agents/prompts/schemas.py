from pydantic import BaseModel, Field


class SummarizePromptInput(BaseModel):
    text: str = Field(min_length=1)
    audience: str = Field(default="general")


class SummarizePromptOutput(BaseModel):
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
