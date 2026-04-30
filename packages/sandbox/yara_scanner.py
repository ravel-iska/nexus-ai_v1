# ═══════════════════════════════════════════════════════════════
# SANDBOX — YARA Scanner + Malware Analysis
# YARA-Forge, Malpedia, Yaraify, Imphash detection
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import logging
import hashlib
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.sandbox.yara")


@dataclass
class ScanResult:
    filename: str
    file_hash: dict           # md5, sha1, sha256
    file_size: int
    imphash: str | None
    yara_matches: list[dict]
    risk_level: str           # clean, suspicious, malicious
    risk_score: float         # 0-10
    recommendations: list[str] = field(default_factory=list)


class YARAScanner:
    """YARA-based malware scanner with multiple rule sources."""

    def __init__(self, rules_dir: str = "data/yara_rules"):
        self.rules_dir = Path(rules_dir)
        self._compiled_rules = None
        self._rule_sources = {
            "yara_forge": "https://yarahq.github.io/yara-forge-rules/",
            "malpedia": "https://malpedia.caad.fkie.fraunhofer.de/",
            "yaraify": "https://yaraify.abuse.ch/",
        }
        logger.info("🔬 YARA Scanner initialized")

    async def init(self):
        """Load and compile YARA rules."""
        try:
            import yara
        except ImportError:
            logger.error("❌ yara-python not installed. Run: pip install yara-python")
            return

        self.rules_dir.mkdir(parents=True, exist_ok=True)
        rule_files = list(self.rules_dir.glob("*.yar")) + list(self.rules_dir.glob("*.yara"))

        if not rule_files:
            logger.warning("⚠️ No YARA rules found. Download rules first.")
            return

        filepaths = {f"rule_{i}": str(f) for i, f in enumerate(rule_files)}
        self._compiled_rules = yara.compile(filepaths=filepaths)
        logger.info(f"✅ Compiled {len(rule_files)} YARA rule files")

    async def scan_file(self, file_path: str) -> ScanResult:
        """Scan a file with YARA rules + hash analysis."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_bytes = path.read_bytes()
        file_size = len(file_bytes)

        # Compute hashes
        file_hash = {
            "md5": hashlib.md5(file_bytes).hexdigest(),
            "sha1": hashlib.sha1(file_bytes).hexdigest(),
            "sha256": hashlib.sha256(file_bytes).hexdigest(),
        }

        # Compute imphash (PE files only)
        imphash = await self._compute_imphash(file_path)

        # YARA scan
        yara_matches = []
        if self._compiled_rules:
            import yara
            matches = self._compiled_rules.match(data=file_bytes)
            for match in matches:
                yara_matches.append({
                    "rule": match.rule,
                    "namespace": match.namespace,
                    "tags": list(match.tags),
                    "meta": dict(match.meta) if match.meta else {},
                    "strings": [
                        {"offset": s[0], "identifier": s[1], "data": s[2][:50].hex()}
                        for s in match.strings[:10]
                    ] if hasattr(match, 'strings') else [],
                })

        # Determine risk
        risk_score = min(10, len(yara_matches) * 3)
        if imphash and await self._check_known_imphash(imphash):
            risk_score = min(10, risk_score + 5)

        risk_level = "clean" if risk_score == 0 else "suspicious" if risk_score < 5 else "malicious"
        recommendations = self._get_recommendations(risk_level, yara_matches)

        return ScanResult(
            filename=path.name,
            file_hash=file_hash,
            file_size=file_size,
            imphash=imphash,
            yara_matches=yara_matches,
            risk_level=risk_level,
            risk_score=risk_score,
            recommendations=recommendations,
        )

    async def _compute_imphash(self, file_path: str) -> str | None:
        """Compute Import Hash for PE files (Ruppde method)."""
        try:
            import pefile
            pe = pefile.PE(file_path)
            return pe.get_imphash()
        except Exception:
            return None

    async def _check_known_imphash(self, imphash: str) -> bool:
        """Check if imphash matches known malware (placeholder for DB lookup)."""
        known_malicious = {
            "d5502a1d00787d68cf52f57963e9b3f9",  # Emotet
            "f34d5f2d4577ed6d9ceec516c1f5a744",  # TrickBot
        }
        return imphash.lower() in known_malicious

    def _get_recommendations(self, risk_level: str, matches: list) -> list[str]:
        recs = []
        if risk_level == "malicious":
            recs.append("🚨 File terdeteksi MALICIOUS — JANGAN dieksekusi!")
            recs.append("🗑️ Quarantine file segera")
            recs.append("📧 Kirim report ke admin")
            for m in matches[:3]:
                recs.append(f"  ⚠️ Rule: {m['rule']} ({m.get('namespace', '')})")
        elif risk_level == "suspicious":
            recs.append("⚠️ File mencurigakan — analisa lebih lanjut diperlukan")
            recs.append("🔬 Jalankan di sandbox VM untuk konfirmasi")
        else:
            recs.append("✅ File bersih — tidak ada YARA match")
        return recs


class HoneypotMonitor:
    """Honeypot untuk deteksi ransomware dan stealer."""

    def __init__(self, honeypot_dir: str = "data/honeypot"):
        self.honeypot_dir = Path(honeypot_dir)
        self._canary_files: dict[str, str] = {}  # filename -> hash
        logger.info("🍯 Honeypot Monitor initialized")

    async def setup_canaries(self):
        """Create canary/honeypot files that should never be modified."""
        self.honeypot_dir.mkdir(parents=True, exist_ok=True)

        canary_names = [
            "important_passwords.xlsx",
            "bitcoin_wallet_backup.dat",
            "company_financials_2025.pdf",
            "employee_database.csv",
            "admin_credentials.txt",
        ]

        for name in canary_names:
            path = self.honeypot_dir / name
            content = f"NEXUS_CANARY_{name}_{os.urandom(16).hex()}"
            path.write_text(content)
            self._canary_files[name] = hashlib.sha256(content.encode()).hexdigest()

        logger.info(f"🍯 {len(canary_names)} canary files deployed")

    async def check_canaries(self) -> list[dict]:
        """Check if any canary files were modified (ransomware/stealer indicator)."""
        alerts = []

        for name, expected_hash in self._canary_files.items():
            path = self.honeypot_dir / name
            if not path.exists():
                alerts.append({
                    "type": "canary_deleted",
                    "file": name,
                    "severity": "critical",
                    "message": f"🚨 Canary file DELETED: {name} — kemungkinan ransomware!",
                })
            else:
                current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if current_hash != expected_hash:
                    alerts.append({
                        "type": "canary_modified",
                        "file": name,
                        "severity": "critical",
                        "message": f"🚨 Canary file MODIFIED: {name} — kemungkinan ransomware/stealer!",
                    })

        if not alerts:
            logger.debug("✅ All canary files intact")
        else:
            logger.critical(f"🚨 {len(alerts)} canary alerts detected!")

        return alerts


class IOMonitor:
    """Monitor R/W I/O operations for suspicious patterns."""

    def __init__(self):
        self._watched_paths: list[str] = []
        self._io_log: list[dict] = []
        logger.info("📊 I/O Monitor initialized")

    async def monitor_io(self, pid: int, duration_seconds: int = 30) -> dict:
        """Monitor I/O operations of a process."""
        try:
            import psutil
            proc = psutil.Process(pid)

            initial = proc.io_counters()
            import asyncio
            await asyncio.sleep(duration_seconds)
            final = proc.io_counters()

            return {
                "pid": pid,
                "name": proc.name(),
                "duration_seconds": duration_seconds,
                "read_bytes": final.read_bytes - initial.read_bytes,
                "write_bytes": final.write_bytes - initial.write_bytes,
                "read_count": final.read_count - initial.read_count,
                "write_count": final.write_count - initial.write_count,
                "suspicious": (final.write_bytes - initial.write_bytes) > 100_000_000,
            }
        except Exception as e:
            return {"error": str(e)}
