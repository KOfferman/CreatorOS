from pydantic import BaseModel, Field


class DailyBriefingResponse(BaseModel):
    greeting: str
    top_opportunity: str
    performance_insight: str
    recommended_posts: list[str] = Field(default_factory=list)
    best_posting_time: str
    creator_score: int = Field(ge=0, le=100)
