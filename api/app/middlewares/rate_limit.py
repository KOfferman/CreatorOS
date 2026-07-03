from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Protocol

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RateLimitBackend(Protocol):
    def check(self, key: str) -> tuple[bool, int]: ...


class InMemoryRateLimitBackend:
    def __init__(self, *, requests_per_minute: int, window_seconds: float = 60.0) -> None:
        self.requests_per_minute = max(1, requests_per_minute)
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = {}

    def check(self, key: str) -> tuple[bool, int]:
        now = time.time()
        with self._lock:
            bucket = self._buckets.setdefault(key, deque())
            while bucket and (now - bucket[0]) > self.window_seconds:
                bucket.popleft()
            allowed = len(bucket) < self.requests_per_minute
            if allowed:
                bucket.append(now)
            remaining = max(0, self.requests_per_minute - len(bucket))
            return allowed, remaining


class RedisRateLimitBackend:
    def __init__(self, *, redis_url: str, requests_per_minute: int, window_seconds: int = 60) -> None:
        import redis

        self.requests_per_minute = max(1, requests_per_minute)
        self.window_seconds = window_seconds
        self._client = redis.from_url(redis_url, decode_responses=True)

    def check(self, key: str) -> tuple[bool, int]:
        redis_key = f"ratelimit:{key}"
        count = int(self._client.incr(redis_key))
        if count == 1:
            self._client.expire(redis_key, self.window_seconds)
        allowed = count <= self.requests_per_minute
        remaining = max(0, self.requests_per_minute - count)
        return allowed, remaining


def is_placeholder_redis_url(redis_url: str) -> bool:
    lowered = redis_url.strip().lower()
    return lowered.startswith("redis://redis:") or lowered.startswith("redis://redis/")


def is_production_redis_url(redis_url: str) -> bool:
    url = redis_url.strip()
    if not url:
        return False
    if is_placeholder_redis_url(url):
        return False
    return url.startswith("redis://") or url.startswith("rediss://")


def build_rate_limit_backend(
    *,
    environment: str,
    redis_url: str,
    requests_per_minute: int,
) -> RateLimitBackend:
    env = environment.strip().lower()

    if env in {"production", "staging"}:
        if not is_production_redis_url(redis_url):
            raise RuntimeError(
                "REDIS_URL must point to a real Redis instance in production/staging "
                "(e.g. Upstash). Docker hostname 'redis' is not valid on Vercel."
            )
        try:
            backend = RedisRateLimitBackend(
                redis_url=redis_url,
                requests_per_minute=requests_per_minute,
            )
            backend.check("__startup_probe__")
            logger.info("rate_limit_backend=redis")
            return backend
        except Exception as exc:
            raise RuntimeError(f"REDIS_URL is required but connection failed: {exc}") from exc

    if redis_url and is_production_redis_url(redis_url):
        try:
            backend = RedisRateLimitBackend(
                redis_url=redis_url,
                requests_per_minute=requests_per_minute,
            )
            backend.check("__startup_probe__")
            logger.info("rate_limit_backend=redis")
            return backend
        except Exception as exc:
            logger.warning("redis_rate_limit_unavailable_falling_back_to_memory", exc_info=exc)

    logger.info("rate_limit_backend=memory")
    return InMemoryRateLimitBackend(requests_per_minute=requests_per_minute)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        backend: RateLimitBackend,
        requests_per_minute: int = 120,
    ) -> None:
        super().__init__(app)
        self.backend = backend
        self.requests_per_minute = max(1, requests_per_minute)

    def _bucket_key(self, request: Request) -> str:
        client_ip = request.client.host if request.client else "unknown"
        return f"{client_ip}:{request.url.path}"

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in {"/health", "/healthz"}:
            return await call_next(request)

        key = self._bucket_key(request)
        allowed, remaining = self.backend.check(key)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please retry later.",
                        "request_id": getattr(request.state, "request_id", None),
                    }
                },
                headers={"Retry-After": "60", "X-RateLimit-Remaining": "0"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        return response
