from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    environment: str


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1)


class TaskEnqueueResponse(BaseModel):
    task_id: str
    status: str = "queued"


class SummarizeResult(BaseModel):
    summary: str
