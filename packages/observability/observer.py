# ═══════════════════════════════════════════════════════════════
# OBSERVABILITY — Error Tracker + AI Debugger + Log Aggregator
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import os, logging, traceback, json
from datetime import datetime
from typing import Any

logger = logging.getLogger("nexus.observability")


class ErrorTracker:
    """Sentry-like error tracking with AI diagnosis."""

    def __init__(self, dsn: str = ""):
        self.dsn = dsn or os.getenv("SENTRY_DSN", "")
        self._init_sentry()
        logger.info("🔴 Error Tracker initialized")

    def _init_sentry(self):
        if not self.dsn:
            return
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            sentry_sdk.init(
                dsn=self.dsn,
                integrations=[FastApiIntegration()],
                traces_sample_rate=1.0, profiles_sample_rate=0.1,
                environment=os.getenv("APP_ENV", "development"),
                before_send=self._enrich_event,
            )
        except ImportError:
            logger.warning("⚠️ sentry_sdk not installed")

    def _enrich_event(self, event, hint):
        event.setdefault("tags", {})["service"] = "nexus-v3"
        return event

    async def capture_error(self, error: Exception, context: dict | None = None) -> dict:
        """Capture and process an error with AI diagnosis."""
        error_data = {
            "type": type(error).__name__, "message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {},
        }

        try:
            import sentry_sdk
            sentry_sdk.capture_exception(error)
        except Exception:
            pass

        diagnosis = await self._ai_diagnose(error_data)
        error_data["ai_diagnosis"] = diagnosis
        return error_data

    async def _ai_diagnose(self, error_data: dict) -> dict:
        """AI-powered error diagnosis."""
        error_type = error_data["type"]
        msg = error_data["message"]

        diagnosis_map = {
            "ConnectionError": {"cause": "Koneksi ke service gagal", "fix": ["Cek apakah service berjalan", "Cek network/firewall", "Retry dengan backoff"]},
            "TimeoutError": {"cause": "Request timeout", "fix": ["Tambah timeout", "Cek load server", "Implementasi retry"]},
            "PermissionError": {"cause": "Akses ditolak", "fix": ["Cek file permissions", "Cek user privileges", "Jalankan sebagai admin"]},
            "ImportError": {"cause": "Module tidak ditemukan", "fix": ["pip install <module>", "Cek virtual environment", "Cek requirements.txt"]},
        }

        diag = diagnosis_map.get(error_type, {"cause": "Error tidak dikenal", "fix": ["Periksa stack trace", "Google error message", "Cek documentation"]})
        diag["severity"] = "critical" if "crash" in msg.lower() or "fatal" in msg.lower() else "warning"
        return diag


class AIDebugger:
    """AI-assisted debugger for automatic error resolution."""

    async def suggest_fix(self, error_data: dict) -> list[str]:
        """Generate fix suggestions based on error pattern."""
        suggestions = []
        tb = error_data.get("traceback", "")
        msg = error_data.get("message", "")

        if "ModuleNotFoundError" in tb:
            module = msg.split("'")[1] if "'" in msg else "unknown"
            suggestions.append(f"pip install {module}")
        if "Connection refused" in msg:
            suggestions.append("Pastikan service target sudah running")
            suggestions.append("Cek port dan hostname di config")
        if "timeout" in msg.lower():
            suggestions.append("Tingkatkan timeout value")
            suggestions.append("Implementasi circuit breaker pattern")
        if "permission" in msg.lower():
            suggestions.append("chmod +x / chown file yang bermasalah")

        return suggestions or ["Analisa manual diperlukan — cek stack trace"]
