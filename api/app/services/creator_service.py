from database import CreatorProfile

from app.repositories.creator_repository import CreatorRepository
from app.schemas.creator import (
    CreatorProfileCreateRequest,
    CreatorProfileResponse,
)


class CreatorService:
    def __init__(self, repository: CreatorRepository | None = None) -> None:
        self.repository = repository or CreatorRepository()

    def create_profile(self, *, user_id: str, payload: CreatorProfileCreateRequest) -> CreatorProfileResponse:
        if not self.repository.user_exists(user_id=user_id):
            raise LookupError("User not found.")
        if self.repository.get_profile(user_id=user_id) is not None:
            raise ValueError("Creator profile already exists for this user.")
        profile = self.repository.create_profile(
            user_id=user_id,
            handle=payload.handle,
            niche=payload.niche,
            bio=payload.bio,
            target_platforms=payload.target_platforms,
            creator_voice=payload.creator_voice,
            audience_size=payload.audience_size,
        )
        return self._to_response(profile)

    def get_profile(self, *, user_id: str) -> CreatorProfileResponse:
        profile = self.repository.get_profile(user_id=user_id)
        if profile is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(profile)

    def update_niche(self, *, user_id: str, niche: str) -> CreatorProfileResponse:
        profile = self.repository.update_niche(user_id=user_id, niche=niche)
        if profile is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(profile)

    def update_target_platforms(self, *, user_id: str, target_platforms: list[str]) -> CreatorProfileResponse:
        profile = self.repository.update_target_platforms(
            user_id=user_id, target_platforms=target_platforms
        )
        if profile is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(profile)

    def update_creator_voice(self, *, user_id: str, creator_voice: str) -> CreatorProfileResponse:
        profile = self.repository.update_creator_voice(
            user_id=user_id, creator_voice=creator_voice
        )
        if profile is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(profile)

    @staticmethod
    def _to_response(profile: CreatorProfile) -> CreatorProfileResponse:
        return CreatorProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            handle=profile.handle,
            niche=profile.niche,
            bio=profile.bio,
            target_platforms=profile.target_platforms or [],
            creator_voice=profile.creator_voice,
            audience_size=profile.audience_size,
        )
