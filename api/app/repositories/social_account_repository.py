from __future__ import annotations

from datetime import datetime, timezone

from database import SocialAccount, get_session_factory

from app.social.token_service import decrypt_token, encrypt_token


class SocialAccountRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def list_for_user(self, *, user_id: str) -> list[SocialAccount]:
        with self.session_factory() as session:
            return (
                session.query(SocialAccount)
                .filter(SocialAccount.user_id == user_id)
                .order_by(SocialAccount.connected_at.desc())
                .all()
            )

    def get_for_user(self, *, user_id: str, platform: str) -> SocialAccount | None:
        with self.session_factory() as session:
            return (
                session.query(SocialAccount)
                .filter(SocialAccount.user_id == user_id, SocialAccount.platform == platform)
                .one_or_none()
            )

    def upsert_connection(
        self,
        *,
        user_id: str,
        platform: str,
        platform_user_id: str | None,
        username: str | None,
        access_token: str,
        refresh_token: str | None,
        expires_at: datetime | None,
        scopes: list[str] | None,
        metadata: dict | None,
    ) -> SocialAccount:
        with self.session_factory() as session:
            account = (
                session.query(SocialAccount)
                .filter(SocialAccount.user_id == user_id, SocialAccount.platform == platform)
                .one_or_none()
            )
            now = datetime.now(timezone.utc)
            if account is None:
                account = SocialAccount(
                    user_id=user_id,
                    platform=platform,
                    platform_user_id=platform_user_id,
                    username=username,
                    access_token_encrypted=encrypt_token(access_token),
                    refresh_token_encrypted=encrypt_token(refresh_token),
                    expires_at=expires_at,
                    scopes=scopes,
                    connected_at=now,
                    metadata_json=metadata,
                )
                session.add(account)
            else:
                account.platform_user_id = platform_user_id
                account.username = username
                account.access_token_encrypted = encrypt_token(access_token)
                account.refresh_token_encrypted = encrypt_token(refresh_token)
                account.expires_at = expires_at
                account.scopes = scopes
                account.connected_at = now
                account.metadata_json = metadata
                session.add(account)

            session.commit()
            session.refresh(account)
            return account

    def delete_for_user(self, *, user_id: str, platform: str) -> bool:
        with self.session_factory() as session:
            account = (
                session.query(SocialAccount)
                .filter(SocialAccount.user_id == user_id, SocialAccount.platform == platform)
                .one_or_none()
            )
            if account is None:
                return False
            session.delete(account)
            session.commit()
            return True

    @staticmethod
    def decrypted_access_token(account: SocialAccount) -> str | None:
        return decrypt_token(account.access_token_encrypted)
