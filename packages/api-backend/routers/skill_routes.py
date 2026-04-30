# ═══════════════════════════════════════════════════════════════
# SKILL ROUTES — API endpoints for skill management
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("nexus.api.skills")
router = APIRouter()


class SkillInstallRequest(BaseModel):
    source: str  # "local", "github", "url", "marketplace"
    path: str    # file path, repo URL, HTTP URL, or skill name
    force: bool = False


class SkillInfo(BaseModel):
    name: str
    version: str
    description: str
    commands: list[str]
    runtime: str
    status: str


@router.get("/list")
async def list_skills():
    """List all installed skills."""
    # TODO: Connect to SkillEngine
    return {"skills": [], "total": 0}


@router.post("/install")
async def install_skill(req: SkillInstallRequest):
    """Install a new skill from various sources."""
    logger.info(f"📦 Installing skill from {req.source}: {req.path}")
    # TODO: Connect to SkillEngine.install()
    return {"status": "ok", "message": f"Skill installation from {req.source} queued"}


@router.delete("/{skill_name}")
async def uninstall_skill(skill_name: str):
    """Uninstall a skill."""
    logger.info(f"🗑️ Uninstalling skill: {skill_name}")
    return {"status": "ok", "message": f"Skill {skill_name} uninstalled"}


@router.post("/{skill_name}/reload")
async def reload_skill(skill_name: str):
    """Hot-reload a specific skill."""
    logger.info(f"🔄 Reloading skill: {skill_name}")
    return {"status": "ok", "message": f"Skill {skill_name} reloaded"}
