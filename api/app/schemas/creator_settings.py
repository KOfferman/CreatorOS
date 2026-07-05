from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

StripePayoutStatus = Literal["disconnected", "connected", "payouts_enabled"]

DEFAULT_NOTIFICATION_PREFS: dict[str, bool] = {
    "new_subscriber_alerts": True,
    "review_moderation_queue": True,
    "weekly_revenue_digest": True,
    "payout_confirmations": True,
}


class CreatorSettings(BaseModel):
    notification_prefs: dict[str, bool] = Field(default_factory=lambda: dict(DEFAULT_NOTIFICATION_PREFS))
    ai_provider: str = "claude"
    stripe_payout_status: StripePayoutStatus = "disconnected"


def normalize_settings(raw: dict | None) -> CreatorSettings:
    if not raw:
        return CreatorSettings()
    prefs = {**DEFAULT_NOTIFICATION_PREFS, **(raw.get("notification_prefs") or {})}
    stripe = raw.get("stripe_payout_status", "disconnected")
    if stripe not in {"disconnected", "connected", "payouts_enabled"}:
        stripe = "disconnected"
    return CreatorSettings(
        notification_prefs=prefs,
        ai_provider=str(raw.get("ai_provider") or "claude"),
        stripe_payout_status=stripe,
    )
