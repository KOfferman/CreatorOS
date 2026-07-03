from contextlib import asynccontextmanager

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.ollama_guard import check_ollama_reachable, uses_local_ollama, verify_ollama_for_startup
from app.core.production_guard import validate_production_settings
from app.errors.handlers import register_exception_handlers
from app.middlewares.rate_limit import RateLimitMiddleware, build_rate_limit_backend
from app.middlewares.request_id import RequestIDMiddleware
from app.schemas.health import HealthResponse

settings = get_settings()
configure_logging(settings.log_level)
validate_production_settings(settings)

_rate_limit_backend = build_rate_limit_backend(
    environment=settings.environment,
    redis_url=settings.redis_url,
    requests_per_minute=settings.api_rate_limit_per_minute,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await verify_ollama_for_startup(settings)
    yield


app = FastAPI(title="CreatorOS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    backend=_rate_limit_backend,
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
    current = get_settings()
    return HealthResponse(status=_health_status(), environment=current.environment)


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def legacy_healthcheck() -> HealthResponse:
    current = get_settings()
    return HealthResponse(status=_health_status(), environment=current.environment)
