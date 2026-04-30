# ═══════════════════════════════════════════════════════════════
# JWT AUTH MIDDLEWARE — Secure all API endpoints
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("nexus.auth")

SECRET_KEY = os.getenv("APP_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# Paths that don't require authentication
PUBLIC_PATHS = {"/health", "/api/docs", "/api/redoc", "/openapi.json"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT-based authentication middleware."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for public paths
        if path in PUBLIC_PATHS or path.startswith("/api/docs"):
            return await call_next(request)

        # Skip in development mode
        if os.getenv("APP_ENV") == "development":
            return await call_next(request)

        # Extract token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header"},
            )

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("sub", "")
            request.state.role = payload.get("role", "user")
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"error": "Token expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})

        return await call_next(request)


def create_token(user_id: str, role: str = "user") -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Verify and decode a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
