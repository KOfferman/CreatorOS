from __future__ import annotations

from database import CreatorProfile, User, get_session_factory


class CreatorRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def user_exists(self, *, user_id: str) -> bool:
        with self.session_factory() as session:
            return session.get(User, user_id) is not None

    def get_profile(self, *, user_id: str) -> CreatorProfile | None:
        with self.session_factory() as session:
            return (
                session.query(CreatorProfile)
                .filter(CreatorProfile.user_id == user_id)
                .order_by(CreatorProfile.created_at.desc())
                .first()
            )

    def create_profile(
        self,
        *,
        user_id: str,
        handle: str,
        niche: str | None,
        bio: str | None,
        target_platforms: list[str],
        creator_voice: str | None,
        audience_size: int | None,
    ) -> CreatorProfile:
        with self.session_factory() as session:
            profile = CreatorProfile(
                user_id=user_id,
                handle=handle,
                niche=niche,
                bio=bio,
                target_platforms=target_platforms,
                creator_voice=creator_voice,
                audience_size=audience_size,
            )
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile

    def update_niche(self, *, user_id: str, niche: str) -> CreatorProfile | None:
        with self.session_factory() as session:
            profile = (
                session.query(CreatorProfile)
                .filter(CreatorProfile.user_id == user_id)
                .order_by(CreatorProfile.created_at.desc())
                .first()
            )
            if profile is None:
                return None
            profile.niche = niche
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile

    def update_target_platforms(self, *, user_id: str, target_platforms: list[str]) -> CreatorProfile | None:
        with self.session_factory() as session:
            profile = (
                session.query(CreatorProfile)
                .filter(CreatorProfile.user_id == user_id)
                .order_by(CreatorProfile.created_at.desc())
                .first()
            )
            if profile is None:
                return None
            profile.target_platforms = target_platforms
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile

    def update_creator_voice(self, *, user_id: str, creator_voice: str) -> CreatorProfile | None:
        with self.session_factory() as session:
            profile = (
                session.query(CreatorProfile)
                .filter(CreatorProfile.user_id == user_id)
                .order_by(CreatorProfile.created_at.desc())
                .first()
            )
            if profile is None:
                return None
            profile.creator_voice = creator_voice
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile
