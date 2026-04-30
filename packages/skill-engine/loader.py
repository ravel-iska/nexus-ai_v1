# ═══════════════════════════════════════════════════════════════
# SKILL ENGINE — Hot-reload modular skill system
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import json
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("nexus.skill.loader")


class SkillLoader:
    """Hot-reload skill loader — loads skills without restarting the bot."""

    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.loaded_skills: dict[str, dict] = {}
        self._handlers: dict[str, Any] = {}

    def load_all(self) -> int:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return 0

        count = 0
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "skill.json").exists():
                try:
                    self.load_skill(skill_dir)
                    count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to load skill {skill_dir.name}: {e}")

        logger.info(f"✅ Loaded {count} skills from {self.skills_dir}")
        return count

    def load_skill(self, skill_path: Path):
        """Load a single skill from a directory."""
        manifest_path = skill_path / "skill.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        name = manifest["name"]
        version = manifest.get("version", "1.0.0")
        runtime = manifest.get("runtime", "python")
        commands = manifest.get("commands", [])

        # Load the handler module
        if runtime == "python":
            handler_path = skill_path / "handler.py"
            if handler_path.exists():
                spec = importlib.util.spec_from_file_location(f"skill_{name}", handler_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._handlers[name] = module
        elif runtime == "nodejs":
            # Node.js skills are handled via subprocess or IPC
            self._handlers[name] = {"type": "nodejs", "path": str(skill_path)}

        self.loaded_skills[name] = {
            "name": name,
            "version": version,
            "runtime": runtime,
            "commands": commands,
            "description": manifest.get("description", ""),
            "permissions": manifest.get("permissions", []),
            "path": str(skill_path),
            "status": "active",
        }

        # Register commands
        for cmd in commands:
            logger.debug(f"  📎 Registered command: {cmd} → {name}")

        logger.info(f"✅ Loaded skill: {name} v{version} ({runtime}) — {commands}")

    def hot_reload(self, skill_name: str) -> bool:
        """Hot-reload a specific skill without restart."""
        if skill_name not in self.loaded_skills:
            logger.warning(f"⚠️ Skill {skill_name} not found")
            return False

        skill_info = self.loaded_skills[skill_name]
        skill_path = Path(skill_info["path"])

        # Clear cached module
        if skill_name in self._handlers:
            del self._handlers[skill_name]

        try:
            self.load_skill(skill_path)
            logger.info(f"🔄 Hot-reloaded skill: {skill_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Hot-reload failed for {skill_name}: {e}")
            return False

    async def execute(self, command: str, args: dict) -> dict:
        """Execute a skill command."""
        # Find which skill handles this command
        for name, info in self.loaded_skills.items():
            if command in info["commands"]:
                handler = self._handlers.get(name)
                if handler is None:
                    return {"error": f"Skill {name} handler not loaded"}

                if isinstance(handler, dict) and handler.get("type") == "nodejs":
                    return await self._execute_nodejs(handler, command, args)

                # Python handler
                if hasattr(handler, "handle"):
                    return await handler.handle(command, args)
                elif hasattr(handler, "execute"):
                    return await handler.execute(command, args)

                return {"error": f"Skill {name} has no handle/execute function"}

        return {"error": f"No skill registered for command: {command}"}

    async def _execute_nodejs(self, handler: dict, command: str, args: dict) -> dict:
        """Execute a Node.js skill via subprocess."""
        import asyncio
        import subprocess

        path = handler["path"]
        proc = await asyncio.create_subprocess_exec(
            "node", f"{path}/handler.js", command, json.dumps(args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            return {"error": stderr.decode()}

        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            return {"output": stdout.decode()}

    def get_skill_list(self) -> list[dict]:
        """Get list of all loaded skills."""
        return list(self.loaded_skills.values())

    def unload_skill(self, skill_name: str) -> bool:
        """Unload a skill."""
        if skill_name in self.loaded_skills:
            del self.loaded_skills[skill_name]
            self._handlers.pop(skill_name, None)
            logger.info(f"🗑️ Unloaded skill: {skill_name}")
            return True
        return False
