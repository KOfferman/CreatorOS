import pytest

from app.core.production_guard import validate_production_settings


def _production_settings(**overrides):
    from app.core.config import Settings

    base = {
        "environment": "production",
        "log_level": "INFO",
        "auth_secret": "x" * 40,
        "auth_url": "https://example.com",
        "auth_enabled": True,
        "demo_auth_enabled": False,
        "database_url": "mysql+pymysql://user:pass@host:3306/db",
        "redis_url": "rediss://default:token@upstash.example:6379",
        "celery_broker_url": "redis://localhost:6379/0",
        "celery_result_backend": "redis://localhost:6379/1",
        "admin_user_ids": ["admin-user-1"],
        "llm_provider": "mock",
    }
    base.update(overrides)
    return Settings(**base)


def test_production_requires_real_redis_url(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")
    settings = _production_settings(redis_url="redis://redis:6379/0")
    with pytest.raises(RuntimeError, match="REDIS_URL"):
        validate_production_settings(settings)


def test_production_accepts_upstash_redis_url(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_AUTH_ENABLED", "false")
    settings = _production_settings(redis_url="rediss://default:abc@fly-upstash.example:6379")
    validate_production_settings(settings)
