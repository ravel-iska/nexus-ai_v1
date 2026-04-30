# ═══════════════════════════════════════════════════════════════
# AGENT ROUTES — API endpoints for agent interaction
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from packages.agents.orchestrator import NexusOrchestrator

logger = logging.getLogger("nexus.api.agent")
router = APIRouter()

# Lazy-init orchestrator
_orchestrator: NexusOrchestrator | None = None


def get_orchestrator() -> NexusOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        config = {
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "ollama_model": os.getenv("OLLAMA_MODEL", "nexus3:latest"),
            "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
            "openrouter_default_model": os.getenv("OPENROUTER_DEFAULT_MODEL", "anthropic/claude-sonnet-4"),
            "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            "database_url": os.getenv("DATABASE_URL"),
        }
        _orchestrator = NexusOrchestrator(config)
    return _orchestrator


class ChatRequest(BaseModel):
    user_id: str
    session_id: str = "default"
    message: str
    media_type: str | None = None
    media_url: str | None = None


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    emotion: str
    confidence: float
    task_type: str
    error: str | None = None
    metadata: dict = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message to the Nexus agent."""
    orchestrator = get_orchestrator()

    media = None
    if req.media_type:
        media = {"type": req.media_type, "url": req.media_url}

    result = await orchestrator.process(
        user_id=req.user_id,
        session_id=req.session_id,
        text=req.message,
        media=media,
    )

    return ChatResponse(**result)


@router.post("/chat/voice")
async def chat_voice(
    user_id: str = Form(...),
    session_id: str = Form("default"),
    audio: UploadFile = File(...),
):
    """Process a voice message (audio file)."""
    orchestrator = get_orchestrator()

    audio_bytes = await audio.read()

    result = await orchestrator.process(
        user_id=user_id,
        session_id=session_id,
        text="[VOICE_MESSAGE]",
        voice=audio_bytes,
    )

    return result


@router.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 50):
    """Get conversation history for a user."""
    orchestrator = get_orchestrator()
    history = await orchestrator.long_memory.get_user_history(user_id, limit)
    return {"user_id": user_id, "history": history}


@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get learned user profile."""
    orchestrator = get_orchestrator()
    profile = await orchestrator.long_memory.get_user_profile(user_id)
    if not profile:
        raise HTTPException(404, "User not found")
    return profile


@router.post("/clear-session")
async def clear_session(user_id: str, session_id: str = "default"):
    """Clear a specific session context."""
    orchestrator = get_orchestrator()
    await orchestrator.short_memory.clear_session(user_id, session_id)
    return {"status": "ok", "message": f"Session {session_id} cleared"}
