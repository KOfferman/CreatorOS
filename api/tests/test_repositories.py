from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.calendar_repository import CalendarRepository
from app.repositories.creator_repository import CreatorRepository
from database import User


def test_creator_repository_create_and_update(sqlite_session_factory):
    with sqlite_session_factory() as session:
        user = User(email="repo-test@example.com", full_name="Repo Test", is_active=True)
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    repository = CreatorRepository(session_factory=sqlite_session_factory)
    created = repository.create_profile(
        user_id=user_id,
        handle="repo.creator",
        niche="fitness",
        bio="repo bio",
        target_platforms=["instagram", "tiktok"],
        creator_voice="direct",
        audience_size=500,
    )
    assert created.user_id == user_id
    assert created.handle == "repo.creator"

    updated = repository.update_niche(user_id=user_id, niche="wellness")
    assert updated is not None
    assert updated.niche == "wellness"


def test_calendar_repository_create_and_move_item(sqlite_session_factory):
    with sqlite_session_factory() as session:
        user = User(email="calendar-repo@example.com", full_name="Calendar Repo", is_active=True)
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    repository = CalendarRepository(session_factory=sqlite_session_factory)
    created = repository.create_item(
        user_id=user_id,
        content_idea_id=None,
        platform="instagram",
        scheduled_for=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        status="scheduled",
        notes="calendar repo test",
    )
    assert created.status == "scheduled"
    assert created.platform == "instagram"

    moved = repository.move_item_date(
        item_id=created.id,
        user_id=user_id,
        scheduled_for=datetime(2026, 7, 2, 9, 30, tzinfo=timezone.utc),
    )
    assert moved is not None
    assert moved.scheduled_for is not None
    assert moved.scheduled_for.day == 2
