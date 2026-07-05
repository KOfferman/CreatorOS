from database import CreatorProfile

from app.core.user_handle import normalize_user_handle
from app.repositories.creator_repository import CreatorRepository
from app.schemas.creator import (
    CreatorProfileCreateRequest,
    CreatorProfileResponse,
    SaveCreatorSettingsRequest,
)
from app.schemas.creator_settings import CreatorSettings, normalize_settings


class CreatorService:
    def __init__(self, repository: CreatorRepository | None = None) -> None:
        self.repository = repository or CreatorRepository()

    def create_profile(self, *, user_id: str, payload: CreatorProfileCreateRequest) -> CreatorProfileResponse:
        if not self.repository.user_exists(user_id=user_id):
            raise LookupError("User not found.")
        if self.repository.get_profile(user_id=user_id) is not None:
            raise ValueError("Creator profile already exists for this user.")
        try:
            handle = normalize_user_handle(payload.user)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if self.repository.handle_is_taken(handle=handle):
            raise ValueError("That user name is already taken.")
        profile = self.repository.create_profile(
            user_id=user_id,
            handle=handle,
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

    def update_user(self, *, user_id: str, user: str) -> CreatorProfileResponse:
        profile = self.repository.get_profile(user_id=user_id)
        if profile is None:
            raise LookupError("Creator profile not found.")
        try:
            handle = normalize_user_handle(user)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if profile.handle == handle:
            return self._to_response(profile)
        if self.repository.handle_is_taken(handle=handle, exclude_user_id=user_id):
            raise ValueError("That user name is already taken.")
        updated = self.repository.update_handle(user_id=user_id, handle=handle)
        if updated is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(updated)

    def save_settings(
        self,
        *,
        user_id: str,
        payload: SaveCreatorSettingsRequest,
    ) -> CreatorProfileResponse:
        profile = self.repository.get_profile(user_id=user_id)
        if profile is None:
            if not payload.user:
                raise LookupError("Creator profile not found.")
            try:
                handle = normalize_user_handle(payload.user)
            except ValueError as exc:
                raise ValueError(str(exc)) from exc
            if self.repository.handle_is_taken(handle=handle):
                raise ValueError("That user name is already taken.")
            if not self.repository.user_exists(user_id=user_id):
                raise LookupError("User not found.")
            profile = self.repository.create_profile(
                user_id=user_id,
                handle=handle,
                niche=None,
                bio=None,
                target_platforms=[],
                creator_voice=None,
                audience_size=None,
            )
            current = CreatorSettings()
        else:
            current = normalize_settings(profile.settings_json)
        merged = current.model_dump()

        if payload.notification_prefs is not None:
            merged["notification_prefs"] = {
                **current.notification_prefs,
                **payload.notification_prefs,
            }
        if payload.ai_provider is not None:
            merged["ai_provider"] = payload.ai_provider.strip()
        if payload.stripe_payout_status is not None:
            merged["stripe_payout_status"] = payload.stripe_payout_status

        handle = profile.handle
        if payload.user is not None:
            try:
                normalized = normalize_user_handle(payload.user)
            except ValueError as exc:
                raise ValueError(str(exc)) from exc
            if normalized != profile.handle:
                if self.repository.handle_is_taken(handle=normalized, exclude_user_id=user_id):
                    raise ValueError("That user name is already taken.")
                handle = normalized

        updated = self.repository.update_settings_json(
            user_id=user_id,
            settings_json=merged,
            handle=handle if handle != profile.handle else None,
        )
        if updated is None:
            raise LookupError("Creator profile not found.")
        return self._to_response(updated)

    @staticmethod
    def _to_response(profile: CreatorProfile) -> CreatorProfileResponse:
        settings = normalize_settings(profile.settings_json)
        return CreatorProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            user=profile.handle,
            handle=profile.handle,
            niche=profile.niche,
            bio=profile.bio,
            target_platforms=profile.target_platforms or [],
            creator_voice=profile.creator_voice,
            audience_size=profile.audience_size,
            settings=settings,
        )
