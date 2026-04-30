# ═══════════════════════════════════════════════════════════════
# SHORT-TERM MEMORY — Redis-backed session context
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger("nexus.memory.short")

DEFAULT_TTL = 3600  # 1 hour session expiry
MAX_CONTEXT_SIZE = 20  # Max messages to keep in context


class ShortTermMemory:
    """Redis-backed short-term memory for conversation context."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        logger.info("📦 Short-term memory (Redis) initialized")

    def _key(self, user_id: str, session_id: str) -> str:
        return f"nexus:context:{user_id}:{session_id}"

    async def get_context(self, user_id: str, session_id: str) -> list[dict]:
        """Retrieve conversation context for a session."""
        key = self._key(user_id, session_id)
        data = await self.redis.lrange(key, 0, -1)
        return [json.loads(item) for item in data]

    async def save_interaction(
        self, user_id: str, session_id: str,
        human_msg: str, ai_msg: str,
    ):
        """Save a human-AI interaction pair to context."""
        key = self._key(user_id, session_id)

        human_entry = json.dumps({"role": "user", "content": human_msg})
        ai_entry = json.dumps({"role": "assistant", "content": ai_msg})

        pipe = self.redis.pipeline()
        pipe.rpush(key, human_entry, ai_entry)
        pipe.ltrim(key, -MAX_CONTEXT_SIZE * 2, -1)  # Keep last N pairs
        pipe.expire(key, DEFAULT_TTL)
        await pipe.execute()

    async def clear_session(self, user_id: str, session_id: str):
        """Clear a specific session context."""
        await self.redis.delete(self._key(user_id, session_id))

    async def get_active_sessions(self, user_id: str) -> list[str]:
        """List active sessions for a user."""
        pattern = f"nexus:context:{user_id}:*"
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            session_id = key.split(":")[-1]
            keys.append(session_id)
        return keys

    async def set_user_preference(self, user_id: str, key: str, value: Any):
        """Store user preference in Redis."""
        pref_key = f"nexus:pref:{user_id}"
        await self.redis.hset(pref_key, key, json.dumps(value))

    async def get_user_preference(self, user_id: str, key: str) -> Any:
        """Retrieve user preference."""
        pref_key = f"nexus:pref:{user_id}"
        val = await self.redis.hget(pref_key, key)
        return json.loads(val) if val else None

    async def increment_token_usage(self, user_id: str, tokens: int) -> int:
        """Track daily token usage per user (budget control)."""
        import datetime
        today = datetime.date.today().isoformat()
        key = f"nexus:tokens:{user_id}:{today}"
        pipe = self.redis.pipeline()
        pipe.incrby(key, tokens)
        pipe.expire(key, 86400)  # TTL 24 hours
        results = await pipe.execute()
        return results[0]

    async def get_token_usage(self, user_id: str) -> int:
        """Get today's token usage."""
        import datetime
        today = datetime.date.today().isoformat()
        key = f"nexus:tokens:{user_id}:{today}"
        val = await self.redis.get(key)
        return int(val) if val else 0
