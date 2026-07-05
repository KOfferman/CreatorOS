import pytest

from app.repositories.creator_repository import CreatorRepository
from app.schemas.creator import CreatorProfileCreateRequest, SaveCreatorSettingsRequest
from app.services.creator_service import CreatorService


def test_save_settings_persists_notification_prefs(sqlite_session_factory) -> None:
    repo = CreatorRepository(session_factory=sqlite_session_factory)
    service = CreatorService(repository=repo)

    from database import User

    with sqlite_session_factory() as session:
        session.add(User(email="settings@example.com", full_name="Settings", is_active=True))
        session.commit()
        user_id = session.query(User).filter(User.email == "settings@example.com").one().id

    service.create_profile(
        user_id=user_id,
        payload=CreatorProfileCreateRequest(user="settings.user"),
    )

    updated = service.save_settings(
        user_id=user_id,
        payload=SaveCreatorSettingsRequest(
            notification_prefs={"weekly_revenue_digest": False},
            ai_provider="gpt4o",
            stripe_payout_status="connected",
        ),
    )

    assert updated.settings.ai_provider == "gpt4o"
    assert updated.settings.stripe_payout_status == "connected"
    assert updated.settings.notification_prefs["weekly_revenue_digest"] is False
    assert updated.settings.notification_prefs["new_subscriber_alerts"] is True

    reloaded = service.get_profile(user_id=user_id)
    assert reloaded.settings.ai_provider == "gpt4o"


def test_save_settings_creates_profile_when_missing(sqlite_session_factory) -> None:
    repo = CreatorRepository(session_factory=sqlite_session_factory)
    service = CreatorService(repository=repo)

    from database import User

    with sqlite_session_factory() as session:
        session.add(User(email="new@example.com", full_name="New", is_active=True))
        session.commit()
        user_id = session.query(User).filter(User.email == "new@example.com").one().id

    created = service.save_settings(
        user_id=user_id,
        payload=SaveCreatorSettingsRequest(
            user="brand.new",
            ai_provider="claude",
        ),
    )

    assert created.user == "brand.new"
    assert created.settings.ai_provider == "claude"
