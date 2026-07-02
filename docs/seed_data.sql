-- CreatorOS demo seed data (MySQL)
-- Idempotent: removes prior seed rows by email/handle, then re-inserts.
--
-- Usage:
--   mysql -u creatoros -p creatoros < docs/seed_data.sql
--
-- Or from Docker Compose:
--   docker compose -f api/docker-compose.yml exec -T mysql \
--     mysql -u creatoros -pcreatoros creatoros < docs/seed_data.sql
--
-- Optional web env (fixed user id):
--   NEXT_PUBLIC_CREATOR_USER_ID=10000000-0000-4000-8000-000000000001

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- Reset existing seed rows
-- ---------------------------------------------------------------------------
DELETE u
FROM users u
LEFT JOIN creator_profiles cp ON cp.user_id = u.id
WHERE u.email = 'daniela@creatoros.demo'
   OR cp.handle = 'daniela.creates';

-- ---------------------------------------------------------------------------
-- Fixed identifiers (stable across re-runs)
-- ---------------------------------------------------------------------------
SET @user_id    = '10000000-0000-4000-8000-000000000001';
SET @profile_id = '10000000-0000-4000-8000-000000000002';
SET @run_id     = '60000000-0000-4000-8000-000000000001';

-- ---------------------------------------------------------------------------
-- User + creator profile
-- ---------------------------------------------------------------------------
INSERT INTO users (id, email, full_name, is_active, created_at, updated_at)
VALUES (
  @user_id,
  'daniela@creatoros.demo',
  'Daniela Vargas',
  1,
  UTC_TIMESTAMP(),
  UTC_TIMESTAMP()
);

INSERT INTO creator_profiles (
  id, user_id, handle, niche, bio, target_platforms, creator_voice, audience_size,
  created_at, updated_at
)
VALUES (
  @profile_id,
  @user_id,
  'daniela.creates',
  'relationships, lifestyle, self-growth, Costa Rica travel',
  'Costa Rica-based creator exploring relationships, lifestyle rituals, and self-growth. Weekly travel stories + honest reflections + practical frameworks.',
  JSON_ARRAY('instagram', 'tiktok', 'youtube', 'newsletter'),
  'warm, honest, reflective, practical, story-first',
  184000,
  UTC_TIMESTAMP(),
  UTC_TIMESTAMP()
);

-- ---------------------------------------------------------------------------
-- Trend reports (10)
-- report_date: CURDATE() minus (9 - index) days
-- ---------------------------------------------------------------------------
INSERT INTO trend_reports (id, user_id, title, source, summary, report_date, created_at, updated_at)
VALUES
  ('20000000-0000-4000-8000-000000000001', @user_id, 'The 2-minute repair after conflict', 'Instagram', 'Relationship micro-repairs are trending: short, actionable de-escalation habits.', DATE_SUB(CURDATE(), INTERVAL 9 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000002', @user_id, 'Soft life routines (but realistic)', 'TikTok', 'Lifestyle content focusing on sustainable routines and mental calm is picking up.', DATE_SUB(CURDATE(), INTERVAL 8 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000003', @user_id, 'Green flags people ignore', 'YouTube', 'Longer breakdowns of healthy relationship signals are getting strong retention.', DATE_SUB(CURDATE(), INTERVAL 7 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000004', @user_id, 'Costa Rica: hidden beaches + ethics', 'Instagram', 'Travel content with ethics, local respect, and itinerary value is outperforming pure aesthetics.', DATE_SUB(CURDATE(), INTERVAL 6 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000005', @user_id, 'Self-growth without hustle culture', 'TikTok', 'Anti-grind personal development narratives are driving shares and saves.', DATE_SUB(CURDATE(), INTERVAL 5 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000006', @user_id, 'Attachment styles in real life', 'Instagram', 'Carousel-style explainers of attachment patterns are seeing high save rates.', DATE_SUB(CURDATE(), INTERVAL 4 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000007', @user_id, 'Boundaries scripts that work', 'TikTok', 'Scripted boundary-setting lines are trending with practical delivery.', DATE_SUB(CURDATE(), INTERVAL 3 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000008', @user_id, 'Daily reset rituals', 'Instagram', 'Evening reset and self-regulation routines are trending among lifestyle audiences.', DATE_SUB(CURDATE(), INTERVAL 2 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000009', @user_id, 'Travel couple dynamics', 'YouTube', 'Relationship + travel storytelling is driving comments and watch time.', DATE_SUB(CURDATE(), INTERVAL 1 DAY), UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('20000000-0000-4000-8000-000000000010', @user_id, 'Glow-up = nervous system care', 'TikTok', 'Self-care reframed as regulation is getting strong engagement.', CURDATE(), UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- ---------------------------------------------------------------------------
-- Content ideas (15)
-- ---------------------------------------------------------------------------
INSERT INTO content_ideas (
  id, user_id, trend_report_id, title, description, status, score, created_at, updated_at
)
VALUES
  ('30000000-0000-4000-8000-000000000001', @user_id, '20000000-0000-4000-8000-000000000001', 'The 2-minute repair: what to say after you snap', 'Hook + script for a short-form repair ritual.', 'draft', 92, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000002', @user_id, '20000000-0000-4000-8000-000000000003', 'Green flags people ignore (Costa Rica edition)', 'Storytelling + relationship insight from travel moments.', 'draft', 88, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000003', @user_id, '20000000-0000-4000-8000-000000000002', 'Soft life routines that don''t require quitting your job', 'Practical routine with boundaries and self-growth framing.', 'draft', 86, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000004', @user_id, '20000000-0000-4000-8000-000000000007', 'Boundary scripts: 5 lines that changed my dating life', 'Swipeable carousel + CTA to save.', 'draft', 90, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000005', @user_id, '20000000-0000-4000-8000-000000000006', 'Attachment styles: how it shows up on vacation', 'Relatable travel scenarios + self-awareness prompt.', 'draft', 84, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000006', @user_id, '20000000-0000-4000-8000-000000000004', 'Costa Rica 3-day itinerary (slow travel)', 'Value-first itinerary with respectful tips.', 'draft', 80, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000007', @user_id, '20000000-0000-4000-8000-000000000008', 'My nightly reset ritual (10 minutes)', 'Simple self-regulation routine with step-by-step.', 'draft', 82, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000008', @user_id, '20000000-0000-4000-8000-000000000010', 'Glow-up is nervous system care: here''s what I mean', 'Reframe + actionable list.', 'draft', 85, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000009', @user_id, '20000000-0000-4000-8000-000000000001', 'Conflict ≠ danger: the reframe that helped me', 'Self-growth + relationships micro-lesson.', 'draft', 78, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000010', @user_id, NULL, 'How I choose partners: 3 non-negotiables', 'Personal framework, warm tone, strong CTA.', 'draft', 83, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000011', @user_id, '20000000-0000-4000-8000-000000000009', 'Travel couple check-in questions', 'Printable questions for couples traveling together.', 'draft', 79, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000012', @user_id, NULL, 'The difference between standards and walls', 'Short-form educational with examples.', 'draft', 81, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000013', @user_id, '20000000-0000-4000-8000-000000000003', 'What ''secure'' actually looks like day-to-day', 'List-style, high-save content.', 'draft', 87, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000014', @user_id, NULL, 'My weekly reflection template', 'Self-growth worksheet angle.', 'draft', 76, UTC_TIMESTAMP(), UTC_TIMESTAMP()),
  ('30000000-0000-4000-8000-000000000015', @user_id, '20000000-0000-4000-8000-000000000004', 'Costa Rica: 5 respectful travel tips locals appreciate', 'Ethical travel angle with cultural sensitivity.', 'draft', 89, UTC_TIMESTAMP(), UTC_TIMESTAMP());

-- ---------------------------------------------------------------------------
-- Calendar items (7) — relative schedule from UTC now
-- ---------------------------------------------------------------------------
INSERT INTO content_calendar_items (
  id, user_id, content_idea_id, platform, scheduled_for, status, notes, created_at, updated_at
)
VALUES
  (
    '40000000-0000-4000-8000-000000000001', @user_id,
    '30000000-0000-4000-8000-000000000001', 'instagram',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 1 DAY) + INTERVAL 9 HOUR,
    'scheduled', 'The 2-minute repair: what to say after you snap',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000002', @user_id,
    '30000000-0000-4000-8000-000000000004', 'tiktok',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 2 DAY) + INTERVAL 18 HOUR,
    'scheduled', 'Boundary scripts: 5 lines that changed my dating life',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000003', @user_id,
    '30000000-0000-4000-8000-000000000006', 'instagram',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 3 DAY) + INTERVAL 10 HOUR,
    'scheduled', 'Costa Rica 3-day itinerary (slow travel)',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000004', @user_id,
    '30000000-0000-4000-8000-000000000007', 'instagram',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 4 DAY) + INTERVAL 8 HOUR,
    'scheduled', 'My nightly reset ritual (10 minutes)',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000005', @user_id,
    '30000000-0000-4000-8000-000000000011', 'youtube',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 5 DAY) + INTERVAL 15 HOUR,
    'draft', 'Travel couple check-in questions',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000006', @user_id,
    '30000000-0000-4000-8000-000000000013', 'instagram',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 6 DAY) + INTERVAL 11 HOUR,
    'scheduled', 'What ''secure'' actually looks like day-to-day',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '40000000-0000-4000-8000-000000000007', @user_id,
    '30000000-0000-4000-8000-000000000015', 'tiktok',
    DATE_ADD(DATE(UTC_TIMESTAMP()), INTERVAL 7 DAY) + INTERVAL 19 HOUR,
    'scheduled', 'Costa Rica: 5 respectful travel tips locals appreciate',
    UTC_TIMESTAMP(), UTC_TIMESTAMP()
  );

-- ---------------------------------------------------------------------------
-- Audience insights (4)
-- ---------------------------------------------------------------------------
INSERT INTO audience_insights (
  id, user_id, creator_profile_id, insight_type, title, details, confidence_score,
  created_at, updated_at
)
VALUES
  (
    '50000000-0000-4000-8000-000000000001', @user_id, @profile_id,
    'posting_time', 'Best posting windows (local time)',
    JSON_OBJECT(
      'top_windows', JSON_ARRAY('Tue 6–8am', 'Thu 6pm', 'Sun 9am'),
      'notes', 'Relationship and self-growth content performs best in morning scroll and evening wind-down.'
    ),
    0.78, UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '50000000-0000-4000-8000-000000000002', @user_id, @profile_id,
    'content_pillars', 'Top pillars by saves and shares',
    JSON_OBJECT(
      'pillars', JSON_ARRAY(
        JSON_OBJECT('name', 'Relationship micro-skills', 'weight', 0.40),
        JSON_OBJECT('name', 'Soft-life routines', 'weight', 0.25),
        JSON_OBJECT('name', 'Costa Rica slow travel', 'weight', 0.20),
        JSON_OBJECT('name', 'Self-growth frameworks', 'weight', 0.15)
      )
    ),
    0.74, UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '50000000-0000-4000-8000-000000000003', @user_id, @profile_id,
    'format', 'Formats that convert to followers',
    JSON_OBJECT(
      'best_formats', JSON_ARRAY(
        'Short-form talking-head with on-screen bullet points',
        'Carousel: ''scripts you can steal''',
        'Travel story + reflection voiceover'
      ),
      'avoid', JSON_ARRAY('Overly polished travel montage without value context')
    ),
    0.69, UTC_TIMESTAMP(), UTC_TIMESTAMP()
  ),
  (
    '50000000-0000-4000-8000-000000000004', @user_id, @profile_id,
    'audience', 'Audience snapshot',
    JSON_OBJECT(
      'primary_regions', JSON_ARRAY('Costa Rica', 'USA', 'Mexico', 'Spain'),
      'age_bands', JSON_OBJECT('18-24', 0.30, '25-34', 0.44, '35-44', 0.18, '45+', 0.08),
      'top_intents', JSON_ARRAY('healthy relationships', 'slow living', 'travel planning', 'self-regulation')
    ),
    0.72, UTC_TIMESTAMP(), UTC_TIMESTAMP()
  );

-- ---------------------------------------------------------------------------
-- Creator score agent run
-- ---------------------------------------------------------------------------
INSERT INTO agent_runs (
  id, user_id, agent_name, status, input_payload, output_payload,
  started_at, finished_at, created_at, updated_at
)
VALUES (
  @run_id,
  @user_id,
  'refresh_creator_score',
  'completed',
  JSON_OBJECT('user_id', @user_id, 'mode', 'seed'),
  JSON_OBJECT(
    'creator_score', 371,
    'explanation', 'Seeded creator score based on fictional activity signals.',
    'usage', JSON_OBJECT('prompt_tokens', 420, 'completion_tokens', 180, 'total_tokens', 600),
    'cost', JSON_OBJECT(
      'input_cost_usd', '0.0000',
      'output_cost_usd', '0.0000',
      'total_cost_usd', '0.0000'
    )
  ),
  UTC_TIMESTAMP() - INTERVAL 3 SECOND,
  UTC_TIMESTAMP(),
  UTC_TIMESTAMP(),
  UTC_TIMESTAMP()
);

SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------------------
-- Summary
-- ---------------------------------------------------------------------------
SELECT 'seed_data applied' AS status, @user_id AS user_id, @profile_id AS profile_id;

SELECT 'trend_reports' AS entity, COUNT(*) AS row_count FROM trend_reports WHERE user_id = @user_id
UNION ALL
SELECT 'content_ideas', COUNT(*) FROM content_ideas WHERE user_id = @user_id
UNION ALL
SELECT 'content_calendar_items', COUNT(*) FROM content_calendar_items WHERE user_id = @user_id
UNION ALL
SELECT 'audience_insights', COUNT(*) FROM audience_insights WHERE user_id = @user_id
UNION ALL
SELECT 'agent_runs', COUNT(*) FROM agent_runs WHERE user_id = @user_id;
