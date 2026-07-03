from __future__ import annotations

import argparse
import calendar
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shared" / "database"))

import os

os.chdir(API_DIR)

from database import (
    AgentRun,
    AudienceInsight,
    ContentCalendarItem,
    ContentIdea,
    CreatorProfile,
    SocialAccount,
    TrendReport,
    User,
    get_session_factory,
)

UTC = timezone.utc

# Stable IDs — must match docs/seed_data.sql and web/.env.local
SEED_USER_ID = "10000000-0000-4000-8000-000000000001"
SEED_PROFILE_ID = "10000000-0000-4000-8000-000000000002"


@dataclass(frozen=True)
class SeedConfig:
    email: str = "daniela@creatoros.demo"
    full_name: str = "Daniela Rivera"
    handle: str = "daniela.creates"
    niche: str = "lifestyle, beauty, wellness"
    bio: str = (
        "NYC lifestyle + beauty creator. Reels, GRWM, honest product reviews, "
        "and creator routines for an 18–34 audience."
    )
    target_platforms: list[str] = None  # type: ignore[assignment]
    creator_voice: str = "aspirational, honest, warm, story-first"
    audience_size: int = 4_650_000

    def __post_init__(self) -> None:
        if self.target_platforms is None:
            object.__setattr__(self, "target_platforms", ["instagram", "tiktok", "youtube"])


def _now() -> datetime:
    return datetime.now(UTC)


def _month_day(*, day: int, hour: int = 10, minute: int = 0) -> datetime:
    now = _now()
    last_day = calendar.monthrange(now.year, now.month)[1]
    safe_day = min(max(day, 1), last_day)
    return datetime(now.year, now.month, safe_day, hour, minute, tzinfo=UTC)


def _print_counts(*, session, user_id: str) -> None:
    trends = session.query(TrendReport).filter(TrendReport.user_id == user_id).count()
    ideas = session.query(ContentIdea).filter(ContentIdea.user_id == user_id).count()
    cal = session.query(ContentCalendarItem).filter(ContentCalendarItem.user_id == user_id).count()
    insights = session.query(AudienceInsight).filter(AudienceInsight.user_id == user_id).count()
    runs = session.query(AgentRun).filter(AgentRun.user_id == user_id).count()
    social = session.query(SocialAccount).filter(SocialAccount.user_id == user_id).count()
    print(
        f"Seeded counts → trends={trends}, ideas={ideas}, calendar={cal}, "
        f"insights={insights}, agent_runs={runs}, social_accounts={social}"
    )


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

    session.query(SocialAccount).filter(SocialAccount.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(AudienceInsight).filter(AudienceInsight.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(AgentRun).filter(AgentRun.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(ContentCalendarItem).filter(ContentCalendarItem.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(ContentIdea).filter(ContentIdea.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(TrendReport).filter(TrendReport.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(CreatorProfile).filter(CreatorProfile.user_id.in_(user_ids)).delete(synchronize_session=False)
    session.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)


def _seed_trends(*, user_id: str) -> list[TrendReport]:
    """Matches _figma_design TRENDING_TOPICS + dashboard briefing topics."""
    today = date.today()
    topics = [
        (
            "Morning routines that changed my life",
            "TikTok",
            "12.4M views · +340% growth. Angles: 5am wake-up challenge, journaling for manifestation, cold shower transformation.",
        ),
        (
            "Pilates transformation: 30 days",
            "Instagram",
            "8.2M views · +210% growth. Angles: week-by-week progress, what no one tells you, beginner mistakes.",
        ),
        (
            "Day in the life: NYC creator",
            "YouTube",
            "5.9M views · +185% growth. Angles: $0 vs $1000 day, realistic schedule, behind the scenes.",
        ),
        (
            "Honest skincare review (no filter)",
            "Instagram",
            "4.7M views · +120% growth. Angles: dermatologist approved, drugstore dupes, breakout triggers.",
        ),
        (
            "Budget vs luxury makeup dupes",
            "TikTok",
            "3.8M views · +95% growth. Angles: blind test challenge, product by product, full glam on $30.",
        ),
        (
            "Marriage or happy single? The truth about it",
            "Instagram",
            "High emotional resonance with your audience. Based on recent comment themes and save patterns.",
        ),
        (
            "GRWM: soft glam in 15 minutes",
            "TikTok",
            "Get-ready-with-me formats are spiking with strong completion rates in beauty niches.",
        ),
        (
            "Room transformation on a budget",
            "YouTube",
            "Before/after home content is trending with high watch time among lifestyle audiences.",
        ),
        (
            "Wellness reset: nervous system care",
            "Instagram",
            "Glow-up reframed as regulation — strong saves and shares in wellness sub-niche.",
        ),
        (
            "Creator side hustle transparency",
            "TikTok",
            "Income breakdown and behind-the-brand content is driving comments and follows.",
        ),
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
                created_at=_now() - timedelta(minutes=i),
                updated_at=_now() - timedelta(minutes=i),
            )
        )
    return reports


def _seed_content_ideas(*, user_id: str, trend_reports: list[TrendReport]) -> list[ContentIdea]:
    """Published posts from figma POSTS_DATA + drafts/scheduled for generator & posts pages."""
    trend_ids = [tr.id for tr in trend_reports]

    ideas_data: list[tuple[str, str, str, float, str | None]] = [
        # Published posts (Posts page)
        ("My morning skincare routine 🌿", "Hook + caption for AM skincare GRWM.", "published", 890.0, trend_ids[0]),
        (
            "Getting ready — MET gala recreation",
            "Full glam transformation reel script with trending audio.",
            "published",
            2100.0,
            trend_ids[1],
        ),
        (
            "Honest review: Is this serum worth $89?",
            "No-filter skincare review with before/after framing.",
            "published",
            540.0,
            trend_ids[3],
        ),
        (
            "Day in my life: NYC creator edition",
            "Vlog outline: realistic creator schedule + BTS moments.",
            "published",
            96.0,
            trend_ids[2],
        ),
        # Dashboard AI idea + generator drafts
        (
            "Marriage or happy single? The truth about it",
            "Carousel + talking-head script based on audience questions.",
            "draft",
            96.0,
            trend_ids[5],
        ),
        (
            "Morning routine reel: 5 habits that changed everything",
            "Short-form script with hook, 3 tips, and CTA to save.",
            "scheduled",
            92.0,
            trend_ids[0],
        ),
        (
            "Pilates progress: week 4 check-in",
            "Transformation update with honest setbacks included.",
            "draft",
            88.0,
            trend_ids[1],
        ),
        (
            "Skincare GRWM — drugstore edition",
            "Full routine under $40 with product callouts.",
            "scheduled",
            86.0,
            trend_ids[3],
        ),
        (
            "NYC vlog: a realistic creator day",
            "Long-form outline with timestamps and B-roll list.",
            "draft",
            84.0,
            trend_ids[2],
        ),
        (
            "Collab @mia.creates — dual GRWM",
            "Co-branded content brief with shared hook ideas.",
            "scheduled",
            90.0,
            trend_ids[4],
        ),
        (
            "Q&A live session: your top 10 questions",
            "Live session run-of-show with audience prompts.",
            "scheduled",
            82.0,
            None,
        ),
        (
            "OOTW lookbook — spring neutrals",
            "5-outfit carousel with shoppable links.",
            "draft",
            80.0,
            None,
        ),
        (
            "Makeup tutorial: soft glam under 20 min",
            "Step-by-step script with product list.",
            "draft",
            78.0,
            trend_ids[4],
        ),
        (
            "Room transformation — rental friendly",
            "Before/after with budget breakdown.",
            "scheduled",
            85.0,
            trend_ids[7],
        ),
        (
            "Monthly faves: beauty + lifestyle picks",
            "Round-up format with affiliate-friendly structure.",
            "draft",
            83.0,
            None,
        ),
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
    """Matches figma CALENDAR_CONTENT + dashboard agenda items."""
    today = date.today()

    # Map idea titles to objects for linking
    by_title = {idea.title: idea for idea in ideas}

    figma_calendar = [
        (2, "Morning routine reel", "instagram", "scheduled", "Morning routine reel: 5 habits that changed everything"),
        (5, "Skincare GRWM", "tiktok", "published", "Skincare GRWM — drugstore edition"),
        (8, "NYC vlog", "youtube", "draft", "NYC vlog: a realistic creator day"),
        (12, "Collab @mia.creates", "instagram", "scheduled", "Collab @mia.creates — dual GRWM"),
        (15, "Q&A live session", "tiktok", "scheduled", "Q&A live session: your top 10 questions"),
        (19, "OOTW lookbook", "instagram", "draft", "OOTW lookbook — spring neutrals"),
        (22, "Makeup tutorial", "tiktok", "draft", "Makeup tutorial: soft glam under 20 min"),
        (26, "Room transformation", "youtube", "scheduled", "Room transformation — rental friendly"),
        (29, "Monthly faves", "instagram", "draft", "Monthly faves: beauty + lifestyle picks"),
    ]

    items: list[ContentCalendarItem] = []
    for day, label, platform, status, idea_title in figma_calendar:
        idea = by_title.get(idea_title)
        items.append(
            ContentCalendarItem(
                user_id=user_id,
                content_idea_id=idea.id if idea else None,
                platform=platform,
                scheduled_for=_month_day(day=day, hour=10 if status != "published" else 9),
                status=status,
                notes=label,
            )
        )

    # Dashboard agenda — today + tomorrow (shown first when sorted by date)
    agenda = [
        (
            datetime.combine(today, time(14, 0), tzinfo=UTC),
            "American photoshoot",
            "American Dream shoot · Today, 2:00 PM",
            "instagram",
        ),
        (
            datetime.combine(today + timedelta(days=1), time(10, 0), tzinfo=UTC),
            "Brand call: Glossier campaign",
            "Partnership negotiation · Tomorrow, 10:00 AM",
            "instagram",
        ),
    ]
    for scheduled_for, label, notes, platform in agenda:
        items.append(
            ContentCalendarItem(
                user_id=user_id,
                content_idea_id=None,
                platform=platform,
                scheduled_for=scheduled_for,
                status="scheduled",
                notes=notes,
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
                "best_time": "06:00",
                "top_windows": ["Tue 6–8am", "Thu 6pm", "Sat 9am"],
                "notes": "Saturday morning drives highest engagement for 18–24 audience.",
            },
            confidence_score=0.82,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="content_pillars",
            title="Top pillars by saves and shares",
            details={
                "pillars": [
                    {"name": "Personal story", "weight": 0.40},
                    {"name": "Education", "weight": 0.25},
                    {"name": "Aspiration", "weight": 0.25},
                    {"name": "Community", "weight": 0.10},
                ]
            },
            confidence_score=0.76,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="platform_stats",
            title="My networks",
            details={
                "platforms": [
                    {"platform": "instagram", "followers": 1_900_000, "weekly_gain": 19_000, "engagement_rate": 10.69},
                    {"platform": "tiktok", "followers": 2_300_000, "weekly_gain": 31_000, "engagement_rate": 14.69},
                    {"platform": "youtube", "followers": 450_000, "weekly_gain": 8_000, "engagement_rate": 6.2},
                ]
            },
            confidence_score=0.88,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="performance_alert",
            title="Latest post performance",
            details={
                "headline": "Your latest post is breaking records 🚀",
                "views": "737.8K",
                "platform": "instagram",
                "vs_average_pct": 116,
                "note": "721.9K–737.8K views · well above your 7-day average.",
            },
            confidence_score=0.91,
        ),
        AudienceInsight(
            user_id=user_id,
            creator_profile_id=creator_profile_id,
            insight_type="audience",
            title="Audience snapshot",
            details={
                "primary_regions": ["USA", "Mexico", "Spain", "Colombia"],
                "age_bands": {"18-24": 0.38, "25-34": 0.42, "35-44": 0.14, "45+": 0.06},
                "top_intents": ["beauty reviews", "GRWM", "creator lifestyle", "wellness routines"],
                "avg_engagement_rate": 6.3,
            },
            confidence_score=0.79,
        ),
    ]


def _seed_social_accounts(*, user_id: str) -> list[SocialAccount]:
    now = _now()
    return [
        SocialAccount(
            user_id=user_id,
            platform="instagram",
            platform_user_id="ig_daniela_creates",
            username="@daniela.creates",
            access_token_encrypted=None,
            metadata_json={
                "display_name": "Daniela Rivera",
                "follower_count": 1_900_000,
                "engagement_rate": 10.69,
            },
            connected_at=now - timedelta(days=30),
        ),
        SocialAccount(
            user_id=user_id,
            platform="tiktok",
            platform_user_id="tt_daniela_creates",
            username="@daniela.creates",
            access_token_encrypted=None,
            metadata_json={
                "display_name": "Daniela Rivera",
                "follower_count": 2_300_000,
                "engagement_rate": 14.69,
            },
            connected_at=now - timedelta(days=28),
        ),
        SocialAccount(
            user_id=user_id,
            platform="youtube",
            platform_user_id="yt_daniela_creates",
            username="@daniela.creates",
            access_token_encrypted=None,
            metadata_json={
                "display_name": "Daniela Rivera",
                "follower_count": 450_000,
                "engagement_rate": 6.2,
            },
            connected_at=now - timedelta(days=21),
        ),
    ]


def _seed_agent_runs(*, user_id: str, creator_score: int) -> list[AgentRun]:
    started = _now() - timedelta(seconds=5)
    finished = _now()
    coach_started = _now() - timedelta(hours=2)
    coach_finished = _now() - timedelta(hours=2) + timedelta(seconds=4)

    return [
        AgentRun(
            user_id=user_id,
            agent_name="refresh_creator_score",
            status="completed",
            input_payload={"user_id": user_id, "mode": "seed"},
            output_payload={
                "creator_score": creator_score,
                "score_delta_week": 12,
                "percentile": "Top 8%",
                "explanation": "Strong engagement velocity and consistent publishing cadence.",
                "usage": {"prompt_tokens": 420, "completion_tokens": 180, "total_tokens": 600},
                "cost": {"input_cost_usd": "0.0000", "output_cost_usd": "0.0000", "total_cost_usd": "0.0000"},
            },
            started_at=started,
            finished_at=finished,
        ),
        AgentRun(
            user_id=user_id,
            agent_name="TrendResearchAgent",
            status="completed",
            input_payload={
                "creator_niche": "lifestyle, beauty, wellness",
                "target_platforms": ["instagram", "tiktok", "youtube"],
            },
            output_payload={
                "topics_found": 10,
                "top_topic": "Morning routines that changed my life",
                "usage": {"prompt_tokens": 890, "completion_tokens": 420, "total_tokens": 1310},
            },
            started_at=started - timedelta(hours=6),
            finished_at=started - timedelta(hours=6) + timedelta(seconds=8),
        ),
        AgentRun(
            user_id=user_id,
            agent_name="GrowthCoachAgent",
            status="completed",
            input_payload={"question": "Weekly strategy check-in", "mode": "seed"},
            output_payload={
                "direct_coaching_response": (
                    "Hey Daniela! 👋 I've analyzed your content from the past 30 days. "
                    "Your engagement rate is 6.3% — that's 2× the industry average. "
                    "Ready to push it even higher?"
                ),
                "recommended_next_actions": [
                    "Post a Story poll today to re-engage warm audience",
                    "Drop a Reel tomorrow at 6am",
                    "Schedule TikTok duet content this week",
                ],
            },
            started_at=coach_started,
            finished_at=coach_finished,
        ),
    ]


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

        trend_reports = (
            session.query(TrendReport)
            .filter(TrendReport.user_id == user.id)
            .order_by(TrendReport.report_date.asc())
            .all()
        )

        ideas = _seed_content_ideas(user_id=user.id, trend_reports=trend_reports)
        session.add_all(ideas)
        session.commit()

        content_ideas = (
            session.query(ContentIdea)
            .filter(ContentIdea.user_id == user.id)
            .order_by(ContentIdea.created_at.asc())
            .all()
        )

        calendar_items = _seed_calendar_items(user_id=user.id, ideas=content_ideas)
        session.add_all(calendar_items)

        insights = _seed_audience_insights(user_id=user.id, creator_profile_id=profile.id)
        session.add_all(insights)

        social_accounts = _seed_social_accounts(user_id=user.id)
        session.add_all(social_accounts)

        runs = _seed_agent_runs(user_id=user.id, creator_score=creator_score)
        session.add_all(runs)

        session.commit()

        print("Seeded demo data successfully.")
        print(f"user_id={user.id} profile_id={profile.id} handle={profile.handle}")
        print("Sign in with daniela@creatoros.demo / demo1234")
        _print_counts(session=session, user_id=user.id)


def seed_daniela(*, reset: bool = True, creator_score: int = 371) -> None:
    seed_data(reset=reset, creator_score=creator_score)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Seed fictional CreatorOS demo data.")
    parser.add_argument("--no-reset", action="store_true", help="Do not delete existing seed data first.")
    parser.add_argument("--creator-score", type=int, default=371, help="Seed creator score value (default 371).")
    args = parser.parse_args(list(argv) if argv is not None else None)

    seed_data(reset=not args.no_reset, creator_score=int(args.creator_score))


if __name__ == "__main__":
    main()
