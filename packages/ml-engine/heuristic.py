# ═══════════════════════════════════════════════════════════════
# ML ENGINE — Heuristic Behaviour Analysis
# Pattern-based + ML anomaly detection for behaviour profiling
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import numpy as np
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("nexus.ml.heuristic")


@dataclass
class BehaviourProfile:
    entity_id: str
    risk_score: float           # 0-10
    risk_level: str             # low, medium, high, critical
    patterns: list[dict] = field(default_factory=list)
    anomalies: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class HeuristicAnalyzer:
    """Heuristic behaviour analysis using pattern matching + ML."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._threshold = 0.75
        logger.info("🔬 Heuristic Behaviour Analyzer initialized")

    async def analyze_network_behaviour(self, traffic_data: list[dict]) -> BehaviourProfile:
        """Analyze network traffic for anomalous behaviour."""
        if not traffic_data:
            return BehaviourProfile("unknown", 0.0, "low")

        patterns = []
        anomalies = []

        # Pattern 1: Unusual port access
        port_counts = {}
        for entry in traffic_data:
            port = entry.get("dst_port", 0)
            port_counts[port] = port_counts.get(port, 0) + 1

        suspicious_ports = {4444, 5555, 6666, 31337, 1337, 8888, 9999}
        for port, count in port_counts.items():
            if port in suspicious_ports:
                anomalies.append({
                    "type": "suspicious_port",
                    "port": port,
                    "count": count,
                    "severity": "high",
                    "description": f"Port {port} diakses {count}x — port umum malware/backdoor",
                })

        # Pattern 2: High-frequency requests (possible C2 beaconing)
        timestamps = [entry.get("timestamp", 0) for entry in traffic_data]
        if len(timestamps) > 10:
            intervals = np.diff(sorted(timestamps))
            if len(intervals) > 0:
                std_dev = np.std(intervals)
                mean_interval = np.mean(intervals)
                if std_dev < mean_interval * 0.1 and mean_interval < 60:
                    anomalies.append({
                        "type": "beaconing",
                        "interval_mean": round(float(mean_interval), 2),
                        "interval_std": round(float(std_dev), 2),
                        "severity": "critical",
                        "description": f"Regular beaconing setiap ~{mean_interval:.0f}s — kemungkinan C2 communication",
                    })

        # Pattern 3: Data exfiltration (large outbound)
        total_outbound = sum(entry.get("bytes_out", 0) for entry in traffic_data)
        total_inbound = sum(entry.get("bytes_in", 0) for entry in traffic_data)
        if total_outbound > total_inbound * 3 and total_outbound > 10_000_000:
            anomalies.append({
                "type": "data_exfiltration",
                "bytes_out": total_outbound,
                "ratio": round(total_outbound / max(total_inbound, 1), 2),
                "severity": "critical",
                "description": f"Outbound traffic {total_outbound/1e6:.1f}MB >> inbound — kemungkinan data exfiltration",
            })

        # Pattern 4: DNS tunneling
        dns_queries = [e for e in traffic_data if e.get("protocol") == "DNS"]
        long_dns = [q for q in dns_queries if len(q.get("query", "")) > 50]
        if len(long_dns) > 5:
            anomalies.append({
                "type": "dns_tunneling",
                "count": len(long_dns),
                "severity": "high",
                "description": f"{len(long_dns)} DNS query dengan panjang tidak wajar — kemungkinan DNS tunneling",
            })

        # Calculate risk score
        severity_scores = {"low": 1, "medium": 3, "high": 6, "critical": 10}
        risk_score = min(10, sum(severity_scores.get(a["severity"], 0) for a in anomalies))
        risk_level = "low" if risk_score < 3 else "medium" if risk_score < 6 else "high" if risk_score < 9 else "critical"

        recommendations = self._generate_recommendations(anomalies)

        return BehaviourProfile(
            entity_id=traffic_data[0].get("src_ip", "unknown"),
            risk_score=risk_score,
            risk_level=risk_level,
            patterns=patterns,
            anomalies=anomalies,
            recommendations=recommendations,
        )

    async def analyze_file_behaviour(self, file_actions: list[dict]) -> BehaviourProfile:
        """Analyze file system behaviour for malware indicators."""
        anomalies = []

        # Check for mass file encryption (ransomware indicator)
        rename_count = sum(1 for a in file_actions if a.get("action") == "rename")
        encrypt_extensions = {".encrypted", ".locked", ".crypto", ".crypt", ".enc"}
        encrypt_renames = sum(
            1 for a in file_actions
            if a.get("action") == "rename" and any(a.get("new_name", "").endswith(ext) for ext in encrypt_extensions)
        )

        if encrypt_renames > 10:
            anomalies.append({
                "type": "ransomware_behaviour",
                "count": encrypt_renames,
                "severity": "critical",
                "description": f"{encrypt_renames} file di-rename ke extension encrypted — RANSOMWARE DETECTED",
            })

        # Check for credential file access (stealer indicator)
        sensitive_paths = ["passwords", "cookies", "login", "wallet", "keystore", ".ssh", "credentials"]
        credential_access = [
            a for a in file_actions
            if any(sp in a.get("path", "").lower() for sp in sensitive_paths)
        ]
        if credential_access:
            anomalies.append({
                "type": "credential_stealing",
                "count": len(credential_access),
                "severity": "critical",
                "description": f"{len(credential_access)} akses ke file sensitif — kemungkinan STEALER",
            })

        risk_score = min(10, len(anomalies) * 4)
        risk_level = "low" if risk_score < 3 else "medium" if risk_score < 6 else "high" if risk_score < 9 else "critical"

        return BehaviourProfile(
            entity_id="file_analysis",
            risk_score=risk_score,
            risk_level=risk_level,
            anomalies=anomalies,
            recommendations=self._generate_recommendations(anomalies),
        )

    def _generate_recommendations(self, anomalies: list[dict]) -> list[str]:
        """Generate actionable recommendations based on anomalies."""
        recs = []
        types = {a["type"] for a in anomalies}

        if "beaconing" in types:
            recs.append("🔴 Isolasi host segera — kemungkinan terinfeksi C2 malware")
            recs.append("🔍 Analisa proses yang menjalankan koneksi periodik")
        if "data_exfiltration" in types:
            recs.append("🔴 Block outbound traffic untuk host ini")
            recs.append("🔍 Periksa file yang dikirim keluar")
        if "ransomware_behaviour" in types:
            recs.append("🚨 ISOLASI SEGERA — Ransomware terdeteksi!")
            recs.append("💾 Restore dari backup terbaru")
        if "credential_stealing" in types:
            recs.append("🔴 Ganti semua password yang terekspos")
            recs.append("🔑 Aktifkan 2FA di semua akun")
        if "dns_tunneling" in types:
            recs.append("🔍 Monitor DNS query panjang (>50 chars)")
            recs.append("🛡️ Implementasi DNS filtering")
        if not recs:
            recs.append("✅ Tidak ada anomali signifikan terdeteksi")

        return recs
