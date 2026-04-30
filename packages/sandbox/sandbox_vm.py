# ═══════════════════════════════════════════════════════════════
# SANDBOX VM — Docker/QEMU-based malware sandbox
# Network & VM bypass, PS/CMD extractor, screen capture
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import os
import json
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.sandbox.vm")


@dataclass
class SandboxReport:
    sample_name: str
    execution_time: float
    processes: list[dict]
    network_activity: list[dict]
    file_activity: list[dict]
    registry_activity: list[dict]
    screenshots: list[str]
    extracted_artifacts: list[dict]  # PS scripts, CMD args, dropped files
    risk_score: float
    verdict: str  # clean, suspicious, malicious


class SandboxVM:
    """Docker-based sandbox for safe malware execution and analysis."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.sandbox_image = self.config.get("image", "nexus/sandbox:latest")
        self.timeout = self.config.get("timeout", 120)
        self.network_enabled = self.config.get("network", False)
        logger.info(f"🔬 Sandbox VM initialized (image: {self.sandbox_image})")

    async def analyze(self, file_path: str) -> SandboxReport:
        """Run a file in the sandbox and collect analysis report."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Sample not found: {file_path}")

        logger.info(f"🔬 Starting sandbox analysis: {path.name}")

        # Create temporary output directory
        output_dir = tempfile.mkdtemp(prefix="nexus_sandbox_")

        try:
            # Run in Docker container
            container_id = await self._start_container(file_path, output_dir)

            # Wait for execution + collect data
            await self._wait_and_collect(container_id, output_dir)

            # Parse results
            report = await self._parse_results(path.name, output_dir)

            return report

        except Exception as e:
            logger.error(f"❌ Sandbox analysis failed: {e}")
            return SandboxReport(
                sample_name=path.name,
                execution_time=0,
                processes=[], network_activity=[], file_activity=[],
                registry_activity=[], screenshots=[], extracted_artifacts=[],
                risk_score=0, verdict="error",
            )

    async def _start_container(self, sample_path: str, output_dir: str) -> str:
        """Start a Docker container for sandbox analysis."""
        network_flag = "--network=none" if not self.network_enabled else ""

        cmd = (
            f"docker run -d --rm "
            f"--memory=512m --cpus=1 "
            f"{network_flag} "
            f"-v {sample_path}:/sample:ro "
            f"-v {output_dir}:/output "
            f"--name nexus_sandbox_{os.getpid()} "
            f"{self.sandbox_image}"
        )

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"Docker start failed: {stderr.decode()}")

        container_id = stdout.decode().strip()
        logger.info(f"🐳 Container started: {container_id[:12]}")
        return container_id

    async def _wait_and_collect(self, container_id: str, output_dir: str):
        """Wait for container execution and collect results."""
        try:
            await asyncio.wait_for(
                self._docker_wait(container_id),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Sandbox timeout ({self.timeout}s), stopping container")
            await asyncio.create_subprocess_shell(f"docker stop {container_id}")

    async def _docker_wait(self, container_id: str):
        """Wait for Docker container to finish."""
        proc = await asyncio.create_subprocess_shell(
            f"docker wait {container_id}",
            stdout=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

    async def _parse_results(self, sample_name: str, output_dir: str) -> SandboxReport:
        """Parse sandbox output into a structured report."""
        output_path = Path(output_dir)

        # Parse process log
        processes = self._read_json(output_path / "processes.json")
        network = self._read_json(output_path / "network.json")
        files = self._read_json(output_path / "files.json")
        registry = self._read_json(output_path / "registry.json")

        # Collect screenshots
        screenshots = [str(f) for f in output_path.glob("screenshot_*.png")]

        # Extract artifacts (PS/CMD/Arguments)
        artifacts = await self._extract_artifacts(processes)

        # Calculate risk score
        risk_score = self._calculate_risk(processes, network, files, artifacts)
        verdict = "clean" if risk_score < 3 else "suspicious" if risk_score < 7 else "malicious"

        return SandboxReport(
            sample_name=sample_name,
            execution_time=self.timeout,
            processes=processes,
            network_activity=network,
            file_activity=files,
            registry_activity=registry,
            screenshots=screenshots,
            extracted_artifacts=artifacts,
            risk_score=risk_score,
            verdict=verdict,
        )

    async def _extract_artifacts(self, processes: list[dict]) -> list[dict]:
        """Extract PowerShell scripts, CMD arguments, and other artifacts."""
        artifacts = []

        for proc in processes:
            cmdline = proc.get("command_line", "")

            # PowerShell detection
            if any(ps in cmdline.lower() for ps in ["powershell", "pwsh"]):
                artifacts.append({
                    "type": "powershell",
                    "pid": proc.get("pid"),
                    "command": cmdline,
                    "decoded": self._decode_ps_base64(cmdline),
                    "severity": "high",
                })

            # CMD detection
            if "cmd.exe" in cmdline.lower() or "cmd /c" in cmdline.lower():
                artifacts.append({
                    "type": "cmd",
                    "pid": proc.get("pid"),
                    "command": cmdline,
                    "severity": "medium",
                })

            # Suspicious arguments
            suspicious_args = ["-enc", "-nop", "-w hidden", "bypass", "downloadstring", "invoke-expression"]
            if any(arg in cmdline.lower() for arg in suspicious_args):
                artifacts.append({
                    "type": "suspicious_argument",
                    "pid": proc.get("pid"),
                    "command": cmdline,
                    "severity": "critical",
                })

        return artifacts

    def _decode_ps_base64(self, cmdline: str) -> str | None:
        """Decode base64-encoded PowerShell commands."""
        import base64
        import re

        match = re.search(r'-[Ee](?:nc(?:oded)?[Cc]ommand)?\s+([A-Za-z0-9+/=]+)', cmdline)
        if match:
            try:
                decoded = base64.b64decode(match.group(1))
                return decoded.decode('utf-16-le', errors='ignore')
            except Exception:
                pass
        return None

    def _calculate_risk(self, processes, network, files, artifacts) -> float:
        """Calculate overall risk score 0-10."""
        score = 0.0

        # Process indicators
        if len(processes) > 10:
            score += 1
        if any("powershell" in p.get("name", "").lower() for p in processes):
            score += 2

        # Network indicators
        if network:
            score += min(3, len(network) * 0.5)

        # File indicators
        drops = [f for f in files if f.get("action") == "create"]
        if len(drops) > 5:
            score += 2

        # Artifact severity
        for a in artifacts:
            if a["severity"] == "critical":
                score += 3
            elif a["severity"] == "high":
                score += 2

        return min(10, score)

    def _read_json(self, path: Path) -> list[dict]:
        """Safely read a JSON file."""
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]
            except Exception:
                pass
        return []
