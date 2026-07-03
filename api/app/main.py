from contextlib import asynccontextmanager

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.ollama_guard import check_ollama_reachable, uses_local_ollama, verify_ollama_for_startup
from app.errors.handlers import register_exception_handlers
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.request_id import RequestIDMiddleware
from app.schemas.health import HealthResponse

settings = get_settings()
configure_logging(settings.log_level)

if settings.environment.lower() in {"production", "staging"}:
    lowered_secret = settings.auth_secret.lower()
    if "changeme" in lowered_secret or "example" in lowered_secret:
        raise RuntimeError("AUTH_SECRET must be a real secret in non-development environments.")
    if settings.llm_provider.lower() == "openai" and not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await verify_ollama_for_startup(settings)
    yield


app = FastAPI(title="CreatorOS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.api_rate_limit_per_minute,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

register_exception_handlers(app)
app.include_router(api_v1_router, prefix="/api/v1")


def _health_status() -> str:
    if os.environ.get("VERCEL"):
        return "ok"
    if uses_local_ollama(settings) and not check_ollama_reachable(settings):
        return "degraded"
    return "ok"


@app.get("/health", response_model=HealthResponse, tags=["health"])
def root_healthcheck() -> HealthResponse:
    return HealthResponse(status=_health_status(), environment=settings.environment)


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def legacy_healthcheck() -> HealthResponse:
    return HealthResponse(status=_health_status(), environment=settings.environment)
