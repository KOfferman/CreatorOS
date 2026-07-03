from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[2]

# Ensure local packages are importable during tests.
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT / "api" / "worker"))
sys.path.insert(0, str(ROOT / "shared" / "agents"))
sys.path.insert(0, str(ROOT / "shared" / "ai_core"))
sys.path.insert(0, str(ROOT / "shared" / "database"))

# Required settings for app startup.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("AUTH_SECRET", "test-secret-value-that-is-long-enough-123")
os.environ.setdefault("AUTH_URL", "http://localhost:3000")
os.environ.setdefault("AUTH_ENABLED", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key-1234567890")
os.environ.setdefault("OPENAI_MODEL", "gpt-4o-mini")
os.environ.setdefault("API_RATE_LIMIT_PER_MINUTE", "5000")


@pytest.fixture()
def app():
    from app.main import app as fastapi_app

    fastapi_app.dependency_overrides.clear()
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token(subject="user-1", email="test@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sqlite_session_factory():
    from database import Base

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
