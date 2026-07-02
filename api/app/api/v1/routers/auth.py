from fastapi import APIRouter
from database import User, get_session_factory

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import AuthTokenRequest, AuthTokenResponse

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=AuthTokenResponse)
def issue_access_token(payload: AuthTokenRequest) -> AuthTokenResponse:
    settings = get_settings()
    # Placeholder auth foundation: any strong-enough password is accepted for local/dev flows.
    # This endpoint still ties tokens to a persisted user record.
    session_factory = get_session_factory()
    with session_factory() as session:
        user = session.query(User).filter(User.email == payload.email).one_or_none()
        if user is None:
            user = User(email=payload.email, full_name=None, is_active=True)
            session.add(user)
            session.commit()
            session.refresh(user)

    token = create_access_token(subject=user.id, email=user.email)
    return AuthTokenResponse(
        access_token=token,
        expires_in_seconds=settings.auth_access_token_exp_minutes * 60,
        user_id=user.id,
    )
