from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.passwords import hash_password


@pytest.fixture()
def authed_client(client: TestClient, sqlite_session_factory, monkeypatch) -> TestClient:
    from database import CreatorProfile, User

    def _factory():
        return sqlite_session_factory

    for module in (
        "app.auth.service",
        "app.repositories.creator_repository",
        "app.repositories.trend_repository",
        "app.repositories.content_idea_repository",
        "app.repositories.calendar_repository",
        "app.repositories.coach_repository",
    ):
        monkeypatch.setattr(f"{module}.get_session_factory", _factory)
    monkeypatch.setattr("database.get_session_factory", _factory)
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    get_settings.cache_clear()

    with sqlite_session_factory() as session:
        user = User(
            id="flow-user-1",
            email="flow@creatoros.demo",
            full_name="Flow Tester",
            password_hash=hash_password("flowpass123"),
            is_active=True,
        )
        session.add(user)
        session.add(
            CreatorProfile(
                id="flow-profile-1",
                user_id=user.id,
                handle="flow.creates",
                niche="beauty",
                bio="Test creator",
                target_platforms=["instagram"],
                creator_voice="warm",
                audience_size=10000,
            )
        )
        session.commit()

    login = client.post(
        "/api/v1/auth/token",
        json={"email": "flow@creatoros.demo", "password": "flowpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@patch("app.services.coach_service.GrowthCoachAgent")
def test_creator_flow_profile_trends_content_calendar_coach(
    mock_coach_agent,
    authed_client: TestClient,
) -> None:
    from ai_core import TokenUsage

    class _CoachExecution:
        class _Meta:
            agent_run_id = "run-coach-1"
            provider_name = "mock"
            model_name = "mock-coach"
            usage = TokenUsage()

        class _Output:
            direct_coaching_response = "Ship one Reel today."
            recommended_next_actions = ["Post at 9am"]
            content_ideas = ["GRWM routine"]
            risk_warning = None

        output = _Output()
        meta = _Meta()

    mock_coach_agent.return_value.run.return_value = _CoachExecution()

    profile = authed_client.get("/api/v1/creators/me")
    assert profile.status_code == 200
    assert profile.json()["handle"] == "flow.creates"

    trends = authed_client.get("/api/v1/trends/latest")
    assert trends.status_code == 200

    generated = authed_client.post(
        "/api/v1/content-ideas/generate",
        json={
            "topic": "Morning skincare routine",
            "platform": "instagram",
            "creator_voice": "warm and honest",
            "goal": "grow saves",
            "audience": "beauty enthusiasts",
        },
    )
    assert generated.status_code == 200

    calendar = authed_client.get("/api/v1/calendar")
    assert calendar.status_code == 200

    coach = authed_client.post(
        "/api/v1/coach/chat",
        json={"question": "What should I post today?"},
    )
    assert coach.status_code == 200
    assert "Reel" in coach.json()["direct_coaching_response"]
