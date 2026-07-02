from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    creator_profile: Mapped["CreatorProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    trend_reports: Mapped[list["TrendReport"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    content_ideas: Mapped[list["ContentIdea"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    content_calendar_items: Mapped[list["ContentCalendarItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audience_insights: Mapped[list["AudienceInsight"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    social_accounts: Mapped[list["SocialAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SocialAccount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "social_accounts"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="social_accounts")


class CreatorProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "creator_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    handle: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    niche: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_platforms: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    creator_voice: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience_size: Mapped[int | None] = mapped_column(nullable=True)
    semantic_embedding: Mapped[list[float] | None] = mapped_column(
        JSON, nullable=True
    )  # Placeholder for future semantic vector storage integration.

    user: Mapped["User"] = relationship(back_populates="creator_profile")
    audience_insights: Mapped[list["AudienceInsight"]] = relationship(
        back_populates="creator_profile"
    )


class TrendReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "trend_reports"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship(back_populates="trend_reports")
    content_ideas: Mapped[list["ContentIdea"]] = relationship(back_populates="trend_report")


class ContentIdea(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_ideas"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trend_report_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("trend_reports.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_embedding: Mapped[list[float] | None] = mapped_column(
        JSON, nullable=True
    )  # Placeholder for future semantic vector storage integration.

    user: Mapped["User"] = relationship(back_populates="content_ideas")
    trend_report: Mapped["TrendReport | None"] = relationship(back_populates="content_ideas")
    calendar_items: Mapped[list["ContentCalendarItem"]] = relationship(back_populates="content_idea")


class ContentCalendarItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_calendar_items"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_idea_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("content_ideas.id", ondelete="SET NULL"), nullable=True
    )
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="idea")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="content_calendar_items")
    content_idea: Mapped["ContentIdea | None"] = relationship(back_populates="calendar_items")


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_runs"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    input_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="agent_runs")


class AudienceInsight(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audience_insights"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_profile_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("creator_profiles.id", ondelete="SET NULL"), nullable=True
    )
    insight_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_embedding: Mapped[list[float] | None] = mapped_column(
        JSON, nullable=True
    )  # Placeholder for future semantic vector storage integration.

    user: Mapped["User"] = relationship(back_populates="audience_insights")
    creator_profile: Mapped["CreatorProfile | None"] = relationship(back_populates="audience_insights")
