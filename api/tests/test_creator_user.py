import pytest

from app.core.user_handle import normalize_user_handle
from app.repositories.creator_repository import CreatorRepository
from app.schemas.creator import CreatorProfileCreateRequest
from app.services.creator_service import CreatorService


def _payload(user: str) -> CreatorProfileCreateRequest:
    return CreatorProfileCreateRequest(user=user)


def test_normalize_user_handle_strips_at_and_lowercases() -> None:
    assert normalize_user_handle("@Daniela.Creates") == "daniela.creates"


def test_normalize_user_handle_rejects_invalid() -> None:
    with pytest.raises(ValueError, match="3–30 characters"):
        normalize_user_handle("ab")


def test_update_user_rejects_taken_name(sqlite_session_factory) -> None:
    repo = CreatorRepository(session_factory=sqlite_session_factory)
    service = CreatorService(repository=repo)

    from database import User

    with sqlite_session_factory() as session:
        session.add(User(email="a@example.com", full_name="A", is_active=True))
        session.add(User(email="b@example.com", full_name="B", is_active=True))
        session.commit()
        user_a = session.query(User).filter(User.email == "a@example.com").one()
        user_b = session.query(User).filter(User.email == "b@example.com").one()
        user_a_id = user_a.id
        user_b_id = user_b.id

    service.create_profile(user_id=user_a_id, payload=_payload("alpha.user"))
    service.create_profile(user_id=user_b_id, payload=_payload("beta.user"))

    with pytest.raises(ValueError, match="already taken"):
        service.update_user(user_id=user_b_id, user="alpha.user")


def test_update_user_allows_same_name(sqlite_session_factory) -> None:
    repo = CreatorRepository(session_factory=sqlite_session_factory)
    service = CreatorService(repository=repo)

    from database import User

    with sqlite_session_factory() as session:
        session.add(User(email="solo@example.com", full_name="Solo", is_active=True))
        session.commit()
        user_id = session.query(User).filter(User.email == "solo@example.com").one().id

    service.create_profile(user_id=user_id, payload=_payload("solo.user"))
    updated = service.update_user(user_id=user_id, user="@solo.user")
    assert updated.user == "solo.user"
