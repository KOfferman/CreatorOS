from __future__ import annotations

from dataclasses import dataclass

from ai_core import AIProviderError, build_provider
from database import ContentIdea
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.repositories.content_idea_repository import ContentIdeaRepository
from app.repositories.trend_repository import TrendRepository
from app.schemas.content_idea import (
    ContentIdeaResponse,
    GenerateContentIdeaRequest,
    GeneratedContentIdeaResponse,
    ListContentIdeasResponse,
    SaveContentIdeaRequest,
)


class _GeneratedIdeaPayload(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    suggested_score: float = Field(ge=0.0, le=100.0)


@dataclass(frozen=True, slots=True)
class DeleteContentIdeaResult:
    deleted: bool


class ContentIdeaService:
    def __init__(
        self,
        repository: ContentIdeaRepository | None = None,
        trend_repository: TrendRepository | None = None,
    ) -> None:
        self.repository = repository or ContentIdeaRepository()
        self.trend_repository = trend_repository or TrendRepository()
        self.settings = get_settings()

    def generate_content_idea(self, payload: GenerateContentIdeaRequest) -> GeneratedContentIdeaResponse:
        if self.settings.llm_provider.strip().lower() == "mock":
            return self._mock_generated_idea(payload)

        try:
            provider = build_provider(
                provider_name=self.settings.llm_provider,
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model,
            )
            result = provider.generate_json(
                prompt=(
                    "Generate one high-quality creator content idea.\n"
                    f"Topic: {payload.topic}\n"
                    f"Platform: {payload.platform}\n"
                    f"Creator voice: {payload.creator_voice}\n"
                    f"Goal: {payload.goal}\n"
                    f"Audience: {payload.audience}\n"
                    "Return JSON with keys: title, description, suggested_score."
                ),
                system_prompt="You are CreatorOS Content Ideation AI. Return JSON only.",
                temperature=0.5,
            )
            idea = _GeneratedIdeaPayload.model_validate(result.data)
            return GeneratedContentIdeaResponse(
                title=idea.title,
                description=idea.description,
                suggested_score=idea.suggested_score,
                status="draft",
            )
        except AIProviderError:
            if self._allows_mock_fallback():
                return self._mock_generated_idea(payload)
            raise

    def _allows_mock_fallback(self) -> bool:
        return self.settings.environment.strip().lower() in {"development", "test"}

    def list_ideas(self, *, user_id: str, limit: int = 50) -> ListContentIdeasResponse:
        ideas = self.repository.list_by_user(user_id=user_id, limit=limit)
        return ListContentIdeasResponse(ideas=[self._to_response(idea) for idea in ideas])

    def save_idea(self, *, user_id: str, payload: SaveContentIdeaRequest) -> ContentIdeaResponse:
        if payload.trend_report_id:
            trend = self.trend_repository.get_by_id(
                trend_report_id=payload.trend_report_id,
                user_id=user_id,
            )
            if trend is None:
                raise LookupError("Trend report not found.")
        idea = self.repository.create(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            trend_report_id=payload.trend_report_id,
            score=payload.score,
        )
        return self._to_response(idea)

    def update_idea_status(self, *, idea_id: str, user_id: str, status: str) -> ContentIdeaResponse:
        idea = self.repository.update_status(idea_id=idea_id, user_id=user_id, status=status)
        if idea is None:
            raise LookupError("Content idea not found.")
        return self._to_response(idea)

    def delete_idea(self, *, idea_id: str, user_id: str) -> DeleteContentIdeaResult:
        deleted = self.repository.delete(idea_id=idea_id, user_id=user_id)
        if not deleted:
            raise LookupError("Content idea not found.")
        return DeleteContentIdeaResult(deleted=True)

    def _mock_generated_idea(self, payload: GenerateContentIdeaRequest) -> GeneratedContentIdeaResponse:
        title = f"{payload.topic}: 3 practical shifts for {payload.platform}"
        description = (
            f"Create a {payload.creator_voice} style post for {payload.audience} that helps achieve "
            f"'{payload.goal}'. Lead with a bold hook, include one actionable framework, and close "
            "with a comment-driving CTA."
        )
        return GeneratedContentIdeaResponse(
            title=title,
            description=description,
            suggested_score=78.0,
            status="draft",
        )

    @staticmethod
    def _to_response(idea: ContentIdea) -> ContentIdeaResponse:
        return ContentIdeaResponse(
            id=idea.id,
            user_id=idea.user_id,
            trend_report_id=idea.trend_report_id,
            title=idea.title,
            description=idea.description,
            status=idea.status,
            score=idea.score,
            created_at=idea.created_at,
            updated_at=idea.updated_at,
        )
