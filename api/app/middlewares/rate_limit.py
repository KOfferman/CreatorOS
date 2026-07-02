from __future__ import annotations

import threading
import time
from collections import deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, requests_per_minute: int = 120) -> None:
        super().__init__(app)
        self.requests_per_minute = max(1, requests_per_minute)
        self.window_seconds = 60.0
        self._lock = threading.Lock()
        self._buckets: dict[str, deque[float]] = {}

    def _bucket_key(self, request: Request) -> str:
        client_ip = request.client.host if request.client else "unknown"
        return f"{client_ip}:{request.url.path}"

    def _check(self, key: str) -> tuple[bool, int]:
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

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in {"/health", "/healthz"}:
            return await call_next(request)

        key = self._bucket_key(request)
        allowed, remaining = self._check(key)
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
