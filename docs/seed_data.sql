-- CreatorOS demo seed data (MySQL) — aligned with _figma_design mock data
-- Idempotent: removes prior seed rows by email/handle, then re-inserts.
--
-- Usage:
--   mysql -u creatoros -p creatoros < docs/seed_data.sql
--
-- Or from Docker Compose:
--   docker compose exec -T mysql mysql -u creatoros -pcreatoros creatoros < docs/seed_data.sql
--
-- Python (recommended — calendar uses current month automatically):
--   cd api && python scripts/seed_data.py
--
-- Web env (fixed user id):
--   NEXT_PUBLIC_CREATOR_USER_ID=10000000-0000-4000-8000-000000000001
--
-- Login: daniela@creatoros.demo / demo1234

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DELETE sa FROM social_accounts sa
INNER JOIN users u ON u.id = sa.user_id
WHERE u.email = 'daniela@creatoros.demo';

DELETE u
FROM users u
LEFT JOIN creator_profiles cp ON cp.user_id = u.id
WHERE u.email = 'daniela@creatoros.demo'
   OR cp.handle = 'daniela.creates';

SET @user_id    = '10000000-0000-4000-8000-000000000001';
SET @profile_id = '10000000-0000-4000-8000-000000000002';

INSERT INTO users (id, email, full_name, is_active, created_at, updated_at)
VALUES (@user_id, 'daniela@creatoros.demo', 'Daniela Rivera', 1, UTC_TIMESTAMP(), UTC_TIMESTAMP());

INSERT INTO creator_profiles (
  id, user_id, handle, niche, bio, target_platforms, creator_voice, audience_size,
  created_at, updated_at
)
VALUES (
  @profile_id, @user_id, 'daniela.creates',
  'lifestyle, beauty, wellness',
  'NYC lifestyle + beauty creator. Reels, GRWM, honest product reviews, and creator routines for an 18–34 audience.',
  JSON_ARRAY('instagram', 'tiktok', 'youtube'),
  'aspirational, honest, warm, story-first',
  4650000,
  UTC_TIMESTAMP(), UTC_TIMESTAMP()
);

-- Trend reports (figma TRENDING_TOPICS + dashboard topics)
INSERT INTO trend_reports (id, user_id, title, source, summary, report_date, created_at, updated_at)
VALUES
  ('20000000-0000-4000-8000-000000000001', @user_id, 'Morning routines that changed my life', 'TikTok', '12.4M views · +340% growth. Angles: 5am wake-up, journaling, cold shower.', DATE_SUB(CURDATE(), INTERVAL 9 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000002', @user_id, 'Pilates transformation: 30 days', 'Instagram', '8.2M views · +210% growth. Week-by-week progress content.', DATE_SUB(CURDATE(), INTERVAL 8 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000003', @user_id, 'Day in the life: NYC creator', 'YouTube', '5.9M views · +185% growth. Realistic schedule + BTS.', DATE_SUB(CURDATE(), INTERVAL 7 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000004', @user_id, 'Honest skincare review (no filter)', 'Instagram', '4.7M views · +120% growth. Drugstore dupes + derm-approved picks.', DATE_SUB(CURDATE(), INTERVAL 6 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000005', @user_id, 'Budget vs luxury makeup dupes', 'TikTok', '3.8M views · +95% growth. Blind test + full glam on $30.', DATE_SUB(CURDATE(), INTERVAL 5 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000006', @user_id, 'Marriage or happy single? The truth about it', 'Instagram', 'High emotional resonance · audience comment themes.', DATE_SUB(CURDATE(), INTERVAL 4 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000007', @user_id, 'GRWM: soft glam in 15 minutes', 'TikTok', 'GRWM formats spiking with strong completion rates.', DATE_SUB(CURDATE(), INTERVAL 3 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000008', @user_id, 'Room transformation on a budget', 'YouTube', 'Before/after home content trending in lifestyle.', DATE_SUB(CURDATE(), INTERVAL 2 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000009', @user_id, 'Wellness reset: nervous system care', 'Instagram', 'Glow-up reframed as regulation — strong saves.', DATE_SUB(CURDATE(), INTERVAL 1 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000010', @user_id, 'Creator side hustle transparency', 'TikTok', 'Income breakdown content driving comments.', CURDATE(), UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- Content ideas (figma POSTS_DATA + calendar-linked drafts)
INSERT INTO content_ideas (id, user_id, trend_report_id, title, description, status, score, created_at, updated_at)
VALUES
  ('30000000-0000-4000-8000-000000000001', @user_id, '20000000-0000-4000-8000-000000000001', 'My morning skincare routine 🌿', 'Hook + caption for AM skincare GRWM.', 'published', 890, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000002', @user_id, '20000000-0000-4000-8000-000000000002', 'Getting ready — MET gala recreation', 'Full glam transformation reel script.', 'published', 2100, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000003', @user_id, '20000000-0000-4000-8000-000000000004', 'Honest review: Is this serum worth $89?', 'No-filter skincare review.', 'published', 540, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000004', @user_id, '20000000-0000-4000-8000-000000000003', 'Day in my life: NYC creator edition', 'Vlog outline with BTS moments.', 'published', 96, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000005', @user_id, '20000000-0000-4000-8000-000000000006', 'Marriage or happy single? The truth about it', 'Carousel + talking-head script.', 'draft', 96, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000006', @user_id, '20000000-0000-4000-8000-000000000001', 'Morning routine reel: 5 habits that changed everything', 'Short-form script with hook + CTA.', 'scheduled', 92, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000007', @user_id, '20000000-0000-4000-8000-000000000002', 'Pilates progress: week 4 check-in', 'Transformation update with honest setbacks.', 'draft', 88, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000008', @user_id, '20000000-0000-4000-8000-000000000004', 'Skincare GRWM — drugstore edition', 'Full routine under $40.', 'scheduled', 86, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000009', @user_id, '20000000-0000-4000-8000-000000000003', 'NYC vlog: a realistic creator day', 'Long-form outline with timestamps.', 'draft', 84, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000010', @user_id, '20000000-0000-4000-8000-000000000005', 'Collab @mia.creates — dual GRWM', 'Co-branded content brief.', 'scheduled', 90, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000011', @user_id, NULL, 'Q&A live session: your top 10 questions', 'Live session run-of-show.', 'scheduled', 82, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000012', @user_id, NULL, 'OOTW lookbook — spring neutrals', '5-outfit carousel.', 'draft', 80, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000013', @user_id, '20000000-0000-4000-8000-000000000005', 'Makeup tutorial: soft glam under 20 min', 'Step-by-step script.', 'draft', 78, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000014', @user_id, '20000000-0000-4000-8000-000000000008', 'Room transformation — rental friendly', 'Before/after with budget breakdown.', 'scheduled', 85, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000015', @user_id, NULL, 'Monthly faves: beauty + lifestyle picks', 'Round-up format.', 'draft', 83, UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- Calendar (figma CALENDAR_CONTENT — days relative to current month + agenda)
INSERT INTO content_calendar_items (id, user_id, content_idea_id, platform, scheduled_for, status, notes, created_at, updated_at)
VALUES
  ('40000000-0000-4000-8000-000000000001', @user_id, '30000000-0000-4000-8000-000000000006', 'instagram', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-02 10:00:00')), 'scheduled', 'Morning routine reel', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000002', @user_id, '30000000-0000-4000-8000-000000000008', 'tiktok', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-05 09:00:00')), 'published', 'Skincare GRWM', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000003', @user_id, '30000000-0000-4000-8000-000000000009', 'youtube', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-08 10:00:00')), 'draft', 'NYC vlog', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000004', @user_id, '30000000-0000-4000-8000-000000000010', 'instagram', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-12 10:00:00')), 'scheduled', 'Collab @mia.creates', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000005', @user_id, '30000000-0000-4000-8000-000000000011', 'tiktok', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-15 10:00:00')), 'scheduled', 'Q&A live session', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000006', @user_id, '30000000-0000-4000-8000-000000000012', 'instagram', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-19 10:00:00')), 'draft', 'OOTW lookbook', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000007', @user_id, '30000000-0000-4000-8000-000000000013', 'tiktok', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-22 10:00:00')), 'draft', 'Makeup tutorial', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000008', @user_id, '30000000-0000-4000-8000-000000000014', 'youtube', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-26 10:00:00')), 'scheduled', 'Room transformation', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000009', @user_id, '30000000-0000-4000-8000-000000000015', 'instagram', TIMESTAMP(DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-29 10:00:00')), 'draft', 'Monthly faves', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000010', @user_id, NULL, 'instagram', DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 14 HOUR), 'scheduled', 'American photoshoot', UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('40000000-0000-4000-8000-000000000011', @user_id, NULL, 'instagram', DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 1 DAY) + INTERVAL 10 HOUR, 'scheduled', 'Brand call: Glossier campaign', UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- Audience insights (figma dashboard + insights screens)
INSERT INTO audience_insights (id, user_id, creator_profile_id, insight_type, title, details, confidence_score, created_at, updated_at)
VALUES
  ('50000000-0000-4000-8000-000000000001', @user_id, @profile_id, 'posting_time', 'Best posting windows (local time)',
   JSON_OBJECT('best_time', '06:00', 'top_windows', JSON_ARRAY('Tue 6–8am', 'Thu 6pm', 'Sat 9am')), 0.82, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('50000000-0000-4000-8000-000000000002', @user_id, @profile_id, 'content_pillars', 'Top pillars by saves and shares',
   JSON_OBJECT('pillars', JSON_ARRAY(
     JSON_OBJECT('name', 'Personal story', 'weight', 0.40),
     JSON_OBJECT('name', 'Education', 'weight', 0.25),
     JSON_OBJECT('name', 'Aspiration', 'weight', 0.25),
     JSON_OBJECT('name', 'Community', 'weight', 0.10)
   )), 0.76, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('50000000-0000-4000-8000-000000000003', @user_id, @profile_id, 'platform_stats', 'My networks',
   JSON_OBJECT('platforms', JSON_ARRAY(
     JSON_OBJECT('platform', 'instagram', 'followers', 1900000, 'weekly_gain', 19000, 'engagement_rate', 10.69),
     JSON_OBJECT('platform', 'tiktok', 'followers', 2300000, 'weekly_gain', 31000, 'engagement_rate', 14.69),
     JSON_OBJECT('platform', 'youtube', 'followers', 450000, 'weekly_gain', 8000, 'engagement_rate', 6.2)
   )), 0.88, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('50000000-0000-4000-8000-000000000004', @user_id, @profile_id, 'performance_alert', 'Latest post performance',
   JSON_OBJECT('headline', 'Your latest post is breaking records 🚀', 'views', '737.8K', 'platform', 'instagram', 'vs_average_pct', 116), 0.91, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('50000000-0000-4000-8000-000000000005', @user_id, @profile_id, 'audience', 'Audience snapshot',
   JSON_OBJECT('avg_engagement_rate', 6.3, 'primary_regions', JSON_ARRAY('USA', 'Mexico', 'Spain'), 'age_bands', JSON_OBJECT('18-24', 0.38, '25-34', 0.42)), 0.79, UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- Connected platforms (Settings screen)
INSERT INTO social_accounts (id, user_id, platform, platform_user_id, username, connected_at, metadata, created_at, updated_at)
VALUES
  ('70000000-0000-4000-8000-000000000001', @user_id, 'instagram', 'ig_daniela_creates', '@daniela.creates', UTC_TIMESTAMP(), JSON_OBJECT('display_name', 'Daniela Rivera', 'follower_count', 1900000), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('70000000-0000-4000-8000-000000000002', @user_id, 'tiktok', 'tt_daniela_creates', '@daniela.creates', UTC_TIMESTAMP(), JSON_OBJECT('display_name', 'Daniela Rivera', 'follower_count', 2300000), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('70000000-0000-4000-8000-000000000003', @user_id, 'youtube', 'yt_daniela_creates', '@daniela.creates', UTC_TIMESTAMP(), JSON_OBJECT('display_name', 'Daniela Rivera', 'follower_count', 450000), UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- Agent runs (creator score 371 + coach + trend research)
INSERT INTO agent_runs (id, user_id, agent_name, status, input_payload, output_payload, started_at, finished_at, created_at, updated_at)
VALUES
  ('60000000-0000-4000-8000-000000000001', @user_id, 'refresh_creator_score', 'completed',
   JSON_OBJECT('user_id', @user_id, 'mode', 'seed'),
   JSON_OBJECT('creator_score', 371, 'score_delta_week', 12, 'percentile', 'Top 8%'),
   UTC_TIMESTAMP() - INTERVAL 5 SECOND, UTC_TIMESTAMP(), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('60000000-0000-4000-8000-000000000002', @user_id, 'TrendResearchAgent', 'completed',
   JSON_OBJECT('creator_niche', 'lifestyle, beauty, wellness'),
   JSON_OBJECT('topics_found', 10, 'top_topic', 'Morning routines that changed my life'),
   UTC_TIMESTAMP() - INTERVAL 6 HOUR, UTC_TIMESTAMP() - INTERVAL 6 HOUR + INTERVAL 8 SECOND, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('60000000-0000-4000-8000-000000000003', @user_id, 'GrowthCoachAgent', 'completed',
   JSON_OBJECT('question', 'Weekly strategy check-in'),
   JSON_OBJECT('direct_coaching_response', 'Hey Daniela! 👋 Engagement rate is 6.3% — 2× industry average.'),
   UTC_TIMESTAMP() - INTERVAL 2 HOUR, UTC_TIMESTAMP() - INTERVAL 2 HOUR + INTERVAL 4 SECOND, UTC_TIMESTAMP(), UTC_TIMESTAMP());

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'seed_data applied' AS status, @user_id AS user_id;

SELECT 'trend_reports' AS entity, COUNT(*) AS row_count FROM trend_reports WHERE user_id = @user_id
UNION ALL SELECT 'content_ideas', COUNT(*) FROM content_ideas WHERE user_id = @user_id
UNION ALL SELECT 'content_calendar_items', COUNT(*) FROM content_calendar_items WHERE user_id = @user_id
UNION ALL SELECT 'audience_insights', COUNT(*) FROM audience_insights WHERE user_id = @user_id
UNION ALL SELECT 'social_accounts', COUNT(*) FROM social_accounts WHERE user_id = @user_id
UNION ALL SELECT 'agent_runs', COUNT(*) FROM agent_runs WHERE user_id = @user_id;
