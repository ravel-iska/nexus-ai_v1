# ═══════════════════════════════════════════════════════════════
# RATE LIMIT MIDDLEWARE — Redis-backed per-IP/user rate limiting
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import time
import logging

import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("nexus.ratelimit")

# Rate limit config
MAX_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_RPM", "60"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed sliding window rate limiter."""

    def __init__(self, app):
        super().__init__(app)
        try:
            self.redis = redis.from_url(REDIS_URL, decode_responses=True)
            self.enabled = True
        except Exception as e:
            logger.warning(f"⚠️ Rate limiter disabled (Redis unavailable): {e}")
            self.enabled = False

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        # Skip rate limit for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Use user_id if authenticated, otherwise IP
        client_id = getattr(request.state, "user_id", None)
        if not client_id:
            client_id = request.client.host if request.client else "unknown"

        key = f"nexus:ratelimit:{client_id}"
        now = time.time()
        window = 60  # 1 minute window

        try:
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            results = pipe.execute()

            request_count = results[2]

            if request_count > MAX_REQUESTS_PER_MINUTE:
                logger.warning(f"🚫 Rate limit exceeded for {client_id}: {request_count}/{MAX_REQUESTS_PER_MINUTE}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "limit": MAX_REQUESTS_PER_MINUTE,
                        "retry_after": window,
                    },
                    headers={"Retry-After": str(window)},
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(MAX_REQUESTS_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(MAX_REQUESTS_PER_MINUTE - request_count)
            return response

        except Exception as e:
            logger.warning(f"⚠️ Rate limit check failed: {e}")
            return await call_next(request)
