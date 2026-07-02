-- CreatorOS schema for Hostinger phpMyAdmin
-- Database: u830541354_CreatorOs
--
-- Steps:
-- 1. hPanel → Databases → phpMyAdmin → select u830541354_CreatorOs
-- 2. SQL tab → paste this entire file → Go
-- 3. Then run docs/seed_data.sql the same way

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
);

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY ix_users_email (email)
);

CREATE TABLE IF NOT EXISTS creator_profiles (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    handle VARCHAR(120) NOT NULL,
    niche VARCHAR(120) NULL,
    bio TEXT NULL,
    target_platforms JSON NULL,
    creator_voice TEXT NULL,
    audience_size INT NULL,
    semantic_embedding JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_creator_profiles_user_id (user_id),
    UNIQUE KEY ix_creator_profiles_handle (handle),
    CONSTRAINT fk_creator_profiles_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trend_reports (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NULL,
    source VARCHAR(255) NULL,
    report_date DATE NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_trend_reports_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content_ideas (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    trend_report_id VARCHAR(36) NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    status VARCHAR(50) NOT NULL,
    score FLOAT NULL,
    semantic_embedding JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_content_ideas_trend_report_id FOREIGN KEY (trend_report_id) REFERENCES trend_reports (id) ON DELETE SET NULL,
    CONSTRAINT fk_content_ideas_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content_calendar_items (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    content_idea_id VARCHAR(36) NULL,
    platform VARCHAR(50) NULL,
    scheduled_for DATETIME NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'idea',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_calendar_content_idea_id FOREIGN KEY (content_idea_id) REFERENCES content_ideas (id) ON DELETE SET NULL,
    CONSTRAINT fk_calendar_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    agent_name VARCHAR(120) NOT NULL,
    status VARCHAR(50) NOT NULL,
    input_payload JSON NULL,
    output_payload JSON NULL,
    error_message TEXT NULL,
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_agent_runs_agent_name (agent_name),
    CONSTRAINT fk_agent_runs_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audience_insights (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    creator_profile_id VARCHAR(36) NULL,
    insight_type VARCHAR(80) NOT NULL,
    title VARCHAR(255) NOT NULL,
    details JSON NULL,
    confidence_score FLOAT NULL,
    semantic_embedding JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_audience_insights_creator_profile_id FOREIGN KEY (creator_profile_id) REFERENCES creator_profiles (id) ON DELETE SET NULL,
    CONSTRAINT fk_audience_insights_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS platform_connections (
    id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    external_account_id VARCHAR(255) NULL,
    account_handle VARCHAR(255) NULL,
    account_name VARCHAR(255) NULL,
    access_token TEXT NULL,
    refresh_token TEXT NULL,
    token_expires_at DATETIME NULL,
    scopes JSON NULL,
    metadata JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_platform_connections_user_platform (user_id, platform),
    KEY ix_platform_connections_user_id (user_id),
    CONSTRAINT fk_platform_connections_user_id FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

INSERT IGNORE INTO alembic_version (version_num) VALUES ('0002_add_platform_connections');
