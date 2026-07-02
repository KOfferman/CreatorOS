from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "database"))

# Ensure seed uses the same database as the API (.env + .env.local in api/).
import os

os.chdir(API_DIR)

from database import (
    AgentRun,
    AudienceInsight,
    ContentCalendarItem,
    ContentIdea,
    CreatorProfile,
    TrendReport,
    User,
    get_session_factory,
)


UTC = timezone.utc

# Stable IDs — must match docs/seed_data.sql so re-seeding does not break browser sessions.
SEED_USER_ID = "10000000-0000-4000-8000-000000000001"
SEED_PROFILE_ID = "10000000-0000-4000-8000-000000000002"


@dataclass(frozen=True)
class SeedConfig:
    email: str = "daniela@creatoros.demo"
    full_name: str = "Daniela Vargas"
    handle: str = "daniela.creates"
    niche: str = "relationships, lifestyle, self-growth, Costa Rica travel"
    bio: str = (
        "Costa Rica-based creator exploring relationships, lifestyle rituals, and self-growth. "
        "Weekly travel stories + honest reflections + practical frameworks."
    )
    target_platforms: list[str] = None  # type: ignore[assignment]
    creator_voice: str = "warm, honest, reflective, practical, story-first"
    audience_size: int = 184_000

    def __post_init__(self) -> None:
        if self.target_platforms is None:
            object.__setattr__(self, "target_platforms", ["instagram", "tiktok", "youtube", "newsletter"])


def _now() -> datetime:
    return datetime.now(UTC)


def _print_counts(*, session, user_id: str) -> None:
    trends = session.query(TrendReport).filter(TrendReport.user_id == user_id).count()
    ideas = session.query(ContentIdea).filter(ContentIdea.user_id == user_id).count()
    cal = session.query(ContentCalendarItem).filter(ContentCalendarItem.user_id == user_id).count()
    insights = session.query(AudienceInsight).filter(AudienceInsight.user_id == user_id).count()
    runs = session.query(AgentRun).filter(AgentRun.user_id == user_id).count()
    print(f"Seeded counts → trends={trends}, ideas={ideas}, calendar_items={cal}, audience_insights={insights}, agent_runs={runs}")


def _delete_existing(*, session, email: str, handle: str) -> None:
    user = session.query(User).filter(User.email == email).one_or_none()
    profile = session.query(CreatorProfile).filter(CreatorProfile.handle == handle).one_or_none()

    user_ids: set[str] = set()
    if user:
        user_ids.add(user.id)
    if profile:
        user_ids.add(profile.user_id)

    if not user_ids:
        return

    # Delete children first (safe even if empty).
    session.query(AudienceInsight).filter(AudienceInsight.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(AgentRun).filter(AgentRun.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(ContentCalendarItem).filter(ContentCalendarItem.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(ContentIdea).filter(ContentIdea.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(TrendReport).filter(TrendReport.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(CreatorProfile).filter(CreatorProfile.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)


def _seed_trends(*, user_id: str) -> list[TrendReport]:
    today = date.today()
    topics = [
        ("The 2-minute repair after conflict", "Instagram", "Relationship micro-repairs are trending: short, actionable de-escalation habits."),
        ("Soft life routines (but realistic)", "TikTok", "Lifestyle content focusing on sustainable routines and mental calm is picking up."),
        ("Green flags people ignore", "YouTube", "Longer breakdowns of healthy relationship signals are getting strong retention."),
        ("Costa Rica: hidden beaches + ethics", "Instagram", "Travel content with ethics, local respect, and itinerary value is outperforming pure aesthetics."),
        ("Self-growth without hustle culture", "TikTok", "Anti-grind personal development narratives are driving shares and saves."),
        ("Attachment styles in real life", "Instagram", "Carousel-style explainers of attachment patterns are seeing high save rates."),
        ("Boundaries scripts that work", "TikTok", "Scripted boundary-setting lines are trending with practical delivery."),
        ("Daily reset rituals", "Instagram", "Evening reset and self-regulation routines are trending among lifestyle audiences."),
        ("Travel couple dynamics", "YouTube", "Relationship + travel storytelling is driving comments and watch time."),
        ("Glow-up = nervous system care", "TikTok", "Self-care reframed as regulation is getting strong engagement."),
    ]

    reports: list[TrendReport] = []
    for i, (title, source, summary) in enumerate(topics):
        reports.append(
            TrendReport(
                user_id=user_id,
                title=title,
                source=source,
                summary=summary,
                report_date=today - timedelta(days=(9 - i)),
            )
        )
    return reports


def _seed_content_ideas(*, user_id: str, trend_reports: list[TrendReport]) -> list[ContentIdea]:
    # Map first few ideas to trend reports for traceability.
    trend_ids = [tr.id for tr in trend_reports]

    ideas_data = [
        ("The 2-minute repair: what to say after you snap", "Hook + script for a short-form repair ritual.", "draft", 92, trend_ids[0]),
        ("Green flags people ignore (Costa Rica edition)", "Storytelling + relationship insight from travel moments.", "draft", 88, trend_ids[2]),
        ("Soft life routines that don't require quitting your job", "Practical routine with boundaries and self-growth framing.", "draft", 86, trend_ids[1]),
        ("Boundary scripts: 5 lines that changed my dating life", "Swipeable carousel + CTA to save.", "draft", 90, trend_ids[6]),
        ("Attachment styles: how it shows up on vacation", "Relatable travel scenarios + self-awareness prompt.", "draft", 84, trend_ids[5]),
        ("Costa Rica 3-day itinerary (slow travel)", "Value-first itinerary with respectful tips.", "draft", 80, trend_ids[3]),
        ("My nightly reset ritual (10 minutes)", "Simple self-regulation routine with step-by-step.", "draft", 82, trend_ids[7]),
        ("Glow-up is nervous system care: here's what I mean", "Reframe + actionable list.", "draft", 85, trend_ids[9]),
        ("Conflict ≠ danger: the reframe that helped me", "Self-growth + relationships micro-lesson.", "draft", 78, trend_ids[0]),
        ("How I choose partners: 3 non-negotiables", "Personal framework, warm tone, strong CTA.", "draft", 83, None),
        ("Travel couple check-in questions", "Printable questions for couples traveling together.", "draft", 79, trend_ids[8]),
        ("The difference between standards and walls", "Short-form educational with examples.", "draft", 81, None),
        ("What 'secure' actually looks like day-to-day", "List-style, high-save content.", "draft", 87, trend_ids[2]),
        ("My weekly reflection template", "Self-growth worksheet angle.", "draft", 76, None),
        ("Costa Rica: 5 respectful travel tips locals appreciate", "Ethical travel angle with cultural sensitivity.", "draft", 89, trend_ids[3]),
    ]

    ideas: list[ContentIdea] = []
    for title, description, status, score, trend_report_id in ideas_data:
        ideas.append(
            ContentIdea(
                user_id=user_id,
                title=title,
                description=description,
                status=status,
                score=float(score),
                trend_report_id=trend_report_id,
            )
        )
    return ideas


def _seed_calendar_items(*, user_id: str, ideas: list[ContentIdea]) -> list[ContentCalendarItem]:
    base = _now().replace(minute=0, second=0, microsecond=0)
    schedule = [
        (ideas[0], "instagram", base + timedelta(days=1, hours=9), "scheduled"),
        (ideas[3], "tiktok", base + timedelta(days=2, hours=18), "scheduled"),
        (ideas[5], "instagram", base + timedelta(days=3, hours=10), "scheduled"),
        (ideas[6], "instagram", base + timedelta(days=4, hours=8), "scheduled"),
        (ideas[10], "youtube", base + timedelta(days=5, hours=15), "draft"),
        (ideas[12], "instagram", base + timedelta(days=6, hours=11), "scheduled"),
        (ideas[14], "tiktok", base + timedelta(days=7, hours=19), "scheduled"),
    ]

    items: list[ContentCalendarItem] = []
    for idea, platform, scheduled_for, status in schedule:
        items.append(
            ContentCalendarItem(
                user_id=user_id,
                content_idea_id=idea.id,
                platform=platform,
                scheduled_for=scheduled_for,
                status=status,
                notes=idea.title,
            )
        )
    return items


def _seed_audience_insights(*, user_id: str, creator_profile_id: str) -> list[AudienceInsight]:
    return [
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="posting_time",
            title="Best posting windows (local time)",
            details={
                "top_windows": ["Tue 6–8am", "Thu 6pm", "Sun 9am"],
                "notes": "Relationship and self-growth content performs best in morning scroll and evening wind-down.",
            },
            confidence_score=0.78,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="content_pillars",
            title="Top pillars by saves and shares",
            details={
                "pillars": [
                    {"name": "Relationship micro-skills", "weight": 0.40},
                    {"name": "Soft-life routines", "weight": 0.25},
                    {"name": "Costa Rica slow travel", "weight": 0.20},
                    {"name": "Self-growth frameworks", "weight": 0.15},
                ]
            },
            confidence_score=0.74,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="format",
            title="Formats that convert to followers",
            details={
                "best_formats": [
                    "Short-form talking-head with on-screen bullet points",
                    "Carousel: 'scripts you can steal'",
                    "Travel story + reflection voiceover",
                ],
                "avoid": ["Overly polished travel montage without value context"],
            },
            confidence_score=0.69,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="audience",
            title="Audience snapshot",
            details={
                "primary_regions": ["Costa Rica", "USA", "Mexico", "Spain"],
                "age_bands": {"18-24": 0.30, "25-34": 0.44, "35-44": 0.18, "45+": 0.08},
                "top_intents": ["healthy relationships", "slow living", "travel planning", "self-regulation"],
            },
            confidence_score=0.72,
        ),
    ]


def _seed_creator_score_run(*, user_id: str, creator_score: int) -> AgentRun:
    started = _now() - timedelta(seconds=3)
    finished = _now()
    return AgentRun(
        user_id=user_id,
        agent_name="refresh_creator_score",
        status="completed",
        input_payload={"user_id": user_id, "mode": "seed"},
        output_payload={
            "creator_score": creator_score,
            "explanation": "Seeded creator score based on fictional activity signals.",
            "usage": {"prompt_tokens": 420, "completion_tokens": 180, "total_tokens": 600},
            "cost": {"input_cost_usd": "0.0000", "output_cost_usd": "0.0000", "total_cost_usd": "0.0000"},
        },
        started_at=started,
        finished_at=finished,
    )


def seed_data(*, reset: bool = True, creator_score: int = 371) -> None:
    cfg = SeedConfig()
    session_factory = get_session_factory()
    with session_factory() as session:
        if reset:
            _delete_existing(session=session, email=cfg.email, handle=cfg.handle)

        user = User(
            id=SEED_USER_ID,
            email=cfg.email,
            full_name=cfg.full_name,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        profile = CreatorProfile(
            id=SEED_PROFILE_ID,
            user_id=user.id,
            handle=cfg.handle,
            niche=cfg.niche,
            bio=cfg.bio,
            target_platforms=cfg.target_platforms,
            creator_voice=cfg.creator_voice,
            audience_size=cfg.audience_size,
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)

        trends = _seed_trends(user_id=user.id)
        session.add_all(trends)
        session.commit()

        # Refresh to ensure IDs exist for relationship use.
        session.flush()
        trend_reports = (
            session.query(TrendReport)
            .filter(TrendReport.user_id == user.id)
            .order_by(TrendReport.report_date.desc())
            .limit(10)
            .all()
        )[::-1]

        ideas = _seed_content_ideas(user_id=user.id, trend_reports=trend_reports)
        session.add_all(ideas)
        session.commit()
        session.flush()

        content_ideas = (
            session.query(ContentIdea)
            .filter(ContentIdea.user_id == user.id)
            .order_by(ContentIdea.created_at.asc())
            .limit(15)
            .all()
        )

        calendar_items = _seed_calendar_items(user_id=user.id, ideas=content_ideas)
        session.add_all(calendar_items)

        insights = _seed_audience_insights(user_id=user.id, creator_profile_id=profile.id)
        session.add_all(insights)

        run = _seed_creator_score_run(user_id=user.id, creator_score=creator_score)
        session.add(run)

        session.commit()

        print("Seeded demo data successfully.")
        print(f"user_id={user.id} profile_id={profile.id} handle={profile.handle}")
        print("Sign in with daniela@creatoros.demo / demo1234")
        _print_counts(session=session, user_id=user.id)


def seed_daniela(*, reset: bool = True, creator_score: int = 371) -> None:
    """Backward-compatible alias."""
    seed_data(reset=reset, creator_score=creator_score)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seed fictional CreatorOS demo data.")
    parser.add_argument("--no-reset", action="store_true", help="Do not delete existing seed data first.")
    parser.add_argument("--creator-score", type=int, default=371, help="Seed creator score value (default 371).")
    args = parser.parse_args(list(argv) if argv is not None else None)

    seed_data(reset=not args.no_reset, creator_score=int(args.creator_score))


if __name__ == "__main__":
    main()

