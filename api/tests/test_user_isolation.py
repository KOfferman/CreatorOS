from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.passwords import hash_password
from app.core.security import create_access_token


@pytest.fixture()
def two_user_client(client: TestClient, sqlite_session_factory, monkeypatch) -> TestClient:
    from database import ContentIdea, CreatorProfile, User

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
        user_a = User(
            id="user-a",
            email="a@creatoros.demo",
            full_name="User A",
            password_hash=hash_password("passwordaaa"),
            is_active=True,
        )
        user_b = User(
            id="user-b",
            email="b@creatoros.demo",
            full_name="User B",
            password_hash=hash_password("passwordbbb"),
            is_active=True,
        )
        session.add_all([user_a, user_b])
        session.add(
            CreatorProfile(
                id="profile-a",
                user_id=user_a.id,
                handle="user.a",
                niche="beauty",
                bio="A",
                target_platforms=["instagram"],
                creator_voice="warm",
                audience_size=1000,
            )
        )
        idea_b = ContentIdea(
            id="idea-b-1",
            user_id=user_b.id,
            title="B secret idea",
            description="private",
            status="draft",
        )
        session.add(idea_b)
        session.commit()

    token = create_access_token(subject="user-a", email="a@creatoros.demo")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def test_cannot_read_other_users_profile(two_user_client: TestClient) -> None:
    response = two_user_client.get("/api/v1/creators/me")
    assert response.status_code == 200
    assert response.json()["user_id"] == "user-a"


def test_cannot_update_other_users_content_idea(two_user_client: TestClient) -> None:
    response = two_user_client.patch(
        "/api/v1/content-ideas/idea-b-1/status",
        json={"status": "published"},
    )
    assert response.status_code == 404


def test_cannot_delete_other_users_content_idea(two_user_client: TestClient) -> None:
    response = two_user_client.delete("/api/v1/content-ideas/idea-b-1")
    assert response.status_code == 404


def test_cannot_list_other_users_data_via_query_param(two_user_client: TestClient) -> None:
    response = two_user_client.get("/api/v1/content-ideas")
    assert response.status_code == 200
    assert response.json()["ideas"] == []


def test_calendar_item_requires_ownership(sqlite_session_factory, two_user_client: TestClient) -> None:
    from database import ContentCalendarItem

    with sqlite_session_factory() as session:
        session.add(
            ContentCalendarItem(
                id="cal-b-1",
                user_id="user-b",
                content_idea_id=None,
                platform="instagram",
                scheduled_for=datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc),
                status="scheduled",
                notes="private",
            )
        )
        session.commit()

    response = two_user_client.delete("/api/v1/calendar/cal-b-1")
    assert response.status_code == 404
