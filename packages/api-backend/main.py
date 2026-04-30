# ═══════════════════════════════════════════════════════════════
# WA AGENT NEXUS v3.0 — FASTAPI BACKEND
# Central API server connecting all packages
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .routers import agent_routes, skill_routes
from .middleware.auth import JWTAuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware

logger = logging.getLogger("nexus.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("🚀 Nexus API Backend starting...")

    # Initialize database tables
    from packages.agents.memory.long_term import LongTermMemory
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://nexus:changeme@localhost:5432/nexus_db")
    memory = LongTermMemory(db_url)
    await memory.init_tables()
    app.state.long_memory = memory

    logger.info("✅ Nexus API Backend ready")
    yield

    # Shutdown
    logger.info("🛑 Nexus API Backend shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="WA Agent Nexus API",
        description="Enterprise AI Agent Ecosystem — Backend API",
        version="3.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )

    # ─── Security Middleware ───
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(","),
    )

    # Custom middleware
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(JWTAuthMiddleware)

    # ─── Routers ───
    app.include_router(agent_routes.router, prefix="/api/v1/agent", tags=["Agent"])
    app.include_router(skill_routes.router, prefix="/api/v1/skills", tags=["Skills"])

    # ─── Health Check ───
    @app.get("/health", tags=["System"])
    async def health():
        return {
            "status": "healthy",
            "version": "3.0.0",
            "service": "nexus-api-backend",
        }

    @app.get("/api/v1/stats", tags=["System"])
    async def system_stats():
        memory = app.state.long_memory
        stats = await memory.get_stats()
        return {"status": "ok", "data": stats}

    return app


# Entry point
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
