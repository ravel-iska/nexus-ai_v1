# ═══════════════════════════════════════════════════════════════
# SKILL VALIDATOR — Validate skill manifests before loading
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("nexus.skill.validator")

REQUIRED_FIELDS = ["name", "version", "commands", "runtime"]
ALLOWED_RUNTIMES = ["python", "nodejs"]
ALLOWED_PERMISSIONS = [
    "browser", "database", "filesystem", "network",
    "media", "blockchain", "osint", "system",
]
MAX_SKILL_SIZE_MB = 50


class SkillValidator:
    """Validate skill manifest and structure before installation."""

    def validate(self, skill_path: Path) -> dict[str, Any]:
        """Full validation of a skill directory. Returns {valid, errors, warnings}."""
        errors = []
        warnings = []

        # 1. Check manifest exists
        manifest_path = skill_path / "skill.json"
        if not manifest_path.exists():
            return {"valid": False, "errors": ["skill.json not found"], "warnings": []}

        # 2. Parse manifest
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            return {"valid": False, "errors": [f"Invalid JSON: {e}"], "warnings": []}

        # 3. Required fields
        for field in REQUIRED_FIELDS:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        # 4. Runtime check
        runtime = manifest.get("runtime", "")
        if runtime not in ALLOWED_RUNTIMES:
            errors.append(f"Invalid runtime: {runtime}. Allowed: {ALLOWED_RUNTIMES}")

        # 5. Handler file exists
        if runtime == "python":
            if not (skill_path / "handler.py").exists():
                errors.append("handler.py not found")
        elif runtime == "nodejs":
            if not (skill_path / "handler.js").exists():
                errors.append("handler.js not found")

        # 6. Permission scope check
        permissions = manifest.get("permissions", [])
        for perm in permissions:
            if perm not in ALLOWED_PERMISSIONS:
                warnings.append(f"Unknown permission: {perm}")

        # 7. Dangerous permissions
        dangerous = {"system", "filesystem", "network"}
        used_dangerous = set(permissions) & dangerous
        if used_dangerous:
            warnings.append(f"⚠️ Dangerous permissions: {used_dangerous}. Requires sandbox.")

        # 8. Size check
        total_size = sum(f.stat().st_size for f in skill_path.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        if size_mb > MAX_SKILL_SIZE_MB:
            errors.append(f"Skill too large: {size_mb:.1f}MB (max {MAX_SKILL_SIZE_MB}MB)")

        # 9. Commands format
        commands = manifest.get("commands", [])
        if not isinstance(commands, list) or not all(isinstance(c, str) for c in commands):
            errors.append("'commands' must be a list of strings")

        valid = len(errors) == 0
        result = {"valid": valid, "errors": errors, "warnings": warnings}

        if valid:
            logger.info(f"✅ Skill validation passed: {manifest.get('name')}")
        else:
            logger.warning(f"❌ Skill validation failed: {errors}")

        return result


# packages/skill-engine/__init__.py content
