from __future__ import annotations

from unittest.mock import patch

import pytest
from ai_core import AIProviderError

from app.schemas.content_idea import GenerateContentIdeaRequest
from app.services.content_idea_service import ContentIdeaService


def _payload() -> GenerateContentIdeaRequest:
    return GenerateContentIdeaRequest(
        topic="Morning routine",
        platform="instagram",
        creator_voice="warm",
        goal="engagement",
        audience="creators",
    )


@patch("app.services.content_idea_service.build_provider")
def test_content_idea_falls_back_to_mock_in_development(mock_build, monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    from app.core.config import get_settings

    get_settings.cache_clear()

    mock_build.return_value.generate_json.side_effect = AIProviderError("provider down")

    service = ContentIdeaService()
    result = service.generate_content_idea(_payload())
    assert "Morning routine" in result.title


@patch("app.services.content_idea_service.build_provider")
def test_content_idea_surfaces_llm_failure_in_production(mock_build, monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    from app.core.config import get_settings

    get_settings.cache_clear()

    mock_build.return_value.generate_json.side_effect = AIProviderError("provider down")

    service = ContentIdeaService()
    with pytest.raises(AIProviderError):
        service.generate_content_idea(_payload())
