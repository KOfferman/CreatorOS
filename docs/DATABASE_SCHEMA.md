# Database Schema (MySQL)

## Overview
CreatorOS uses MySQL as the primary source of truth with SQLAlchemy models in `shared/database/database/models.py`.

UUID string primary keys (`String(36)`) are used across entities for portability and API friendliness.

## Core Tables

### `users`
- identity root for all user-scoped entities
- key fields: `email`, `full_name`, `is_active`
- unique index on `email`

### `creator_profiles`
- one-to-one extension of `users`
- key fields: `handle`, `niche`, `bio`, `target_platforms`, `creator_voice`, `audience_size`
- unique index on `handle`

### `trend_reports`
- discovered trend intelligence
- key fields: `title`, `summary`, `source`, `report_date`
- many-to-one to `users`

### `content_ideas`
- generated or curated post concepts
- key fields: `title`, `description`, `status`, `score`
- optional relation to `trend_reports`
- many-to-one to `users`

### `content_calendar_items`
- publish planning records
- key fields: `platform`, `scheduled_for`, `status`, `notes`
- optional relation to `content_ideas`
- many-to-one to `users`

### `agent_runs`
- execution ledger for all agent operations
- key fields: `agent_name`, `status`, `input_payload`, `output_payload`, `error_message`, timing fields
- many-to-one to `users`

### `audience_insights`
- structured audience analytics findings
- key fields: `insight_type`, `title`, `details`, `confidence_score`
- many-to-one to `users`

## Relationship Map
- `users` → one `creator_profile`
- `users` → many `trend_reports`
- `users` → many `content_ideas`
- `users` → many `content_calendar_items`
- `users` → many `agent_runs`
- `users` → many `audience_insights`
- `trend_reports` → many `content_ideas`
- `content_ideas` → many `content_calendar_items`

## Status Conventions
- `content_calendar_items.status`: `idea`, `draft`, `scheduled`, `published`
- `agent_runs.status`: `queued`, `running`, `completed`, `failed`

## Migration Strategy
- Alembic migrations in `shared/database/alembic`
- explicit forward migrations only in normal release flow
- rollback scripts prepared per release train for critical fixes

## Indexing Priorities
Current + recommended:
- `users.email` unique (existing)
- `creator_profiles.handle` unique (existing)
- `agent_runs.agent_name` index (existing)
- add composite indexes as data grows:
  - `agent_runs (user_id, created_at desc)`
  - `trend_reports (user_id, report_date desc)`
  - `content_calendar_items (user_id, scheduled_for)`

## Data Retention Guidance
- keep `agent_runs` for audit + cost attribution
- archive old `agent_runs.output_payload` to cold storage at scale
- define retention tiers by environment and compliance needs
