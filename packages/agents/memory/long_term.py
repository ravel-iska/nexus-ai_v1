# ═══════════════════════════════════════════════════════════════
# LONG-TERM MEMORY — PostgreSQL persistent storage
# Stores all interactions for learning & improvement
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import json
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, DateTime, Float, JSON, select, func

logger = logging.getLogger("nexus.memory.long")


class Base(DeclarativeBase):
    pass


class Interaction(Base):
    """Immutable record of every user-agent interaction."""
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, index=True)
    input_text: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    agent_used: Mapped[str] = mapped_column(Text, default="nexus-local")
    task_type: Mapped[str] = mapped_column(Text, default="general")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserProfile(Base):
    """Learned user profile for personalization."""
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(Text, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(Text, default="id")
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    learned_topics: Mapped[dict] = mapped_column(JSON, default=dict)
    interaction_count: Mapped[int] = mapped_column(default=0)
    total_tokens_used: Mapped[int] = mapped_column(default=0)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Immutable audit trail for all system actions."""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(Text)
    actor: Mapped[str] = mapped_column(Text)
    target: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    severity: Mapped[str] = mapped_column(Text, default="info")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LongTermMemory:
    """PostgreSQL-backed persistent memory for learning and audit."""

    def __init__(self, database_url: str | None = None):
        url = database_url or "postgresql+asyncpg://nexus:changeme@localhost:5432/nexus_db"
        self.engine = create_async_engine(url, echo=False, pool_size=10)
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession)
        logger.info("🗄️ Long-term memory (PostgreSQL) initialized")

    async def init_tables(self):
        """Create all tables if they don't exist."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")

    async def save_interaction(
        self, user_id: str, input_text: str, response: str,
        agent_used: str = "", task_type: str = "general",
        confidence: float = 0.0, metadata: dict | None = None,
    ):
        """Save an interaction to persistent storage."""
        async with self.session_factory() as session:
            interaction = Interaction(
                user_id=user_id,
                input_text=input_text,
                response=response,
                agent_used=agent_used,
                task_type=task_type,
                confidence=confidence,
                metadata=metadata or {},
            )
            session.add(interaction)

            # Update user profile
            await self._update_user_profile(session, user_id, task_type, metadata)

            await session.commit()

    async def _update_user_profile(
        self, session: AsyncSession, user_id: str,
        task_type: str, metadata: dict | None,
    ):
        """Update or create user profile based on interaction."""
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile is None:
            profile = UserProfile(user_id=user_id)
            session.add(profile)

        profile.interaction_count += 1
        profile.last_seen = datetime.utcnow()

        tokens = (metadata or {}).get("tokens_used", 0)
        profile.total_tokens_used += tokens

        # Learn topic frequency
        topics = profile.learned_topics or {}
        topics[task_type] = topics.get(task_type, 0) + 1
        profile.learned_topics = topics

    async def get_user_history(
        self, user_id: str, limit: int = 50
    ) -> list[dict]:
        """Get recent interaction history for a user."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Interaction)
                .where(Interaction.user_id == user_id)
                .order_by(Interaction.created_at.desc())
                .limit(limit)
            )
            interactions = result.scalars().all()
            return [
                {
                    "input": i.input_text,
                    "response": i.response,
                    "agent": i.agent_used,
                    "task_type": i.task_type,
                    "created_at": i.created_at.isoformat(),
                }
                for i in reversed(interactions)
            ]

    async def get_user_profile(self, user_id: str) -> dict | None:
        """Get learned user profile."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            if not profile:
                return None
            return {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "language": profile.language,
                "preferences": profile.preferences,
                "learned_topics": profile.learned_topics,
                "interaction_count": profile.interaction_count,
                "total_tokens": profile.total_tokens_used,
            }

    async def log_audit(
        self, action: str, actor: str,
        target: str = "", details: dict | None = None,
        severity: str = "info",
    ):
        """Write an immutable audit log entry."""
        async with self.session_factory() as session:
            entry = AuditLog(
                action=action, actor=actor, target=target,
                details=details or {}, severity=severity,
            )
            session.add(entry)
            await session.commit()

    async def get_stats(self) -> dict:
        """Get system-wide statistics."""
        async with self.session_factory() as session:
            total_interactions = await session.scalar(select(func.count(Interaction.id)))
            total_users = await session.scalar(select(func.count(UserProfile.id)))
            return {
                "total_interactions": total_interactions or 0,
                "total_users": total_users or 0,
            }
