# ═══════════════════════════════════════════════════════════════
# SECURITY — Pentest Suite + OSINT Engine + Leak Checker
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging, asyncio
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.security")


@dataclass
class ScanReport:
    target: str
    scan_type: str
    findings: list[dict] = field(default_factory=list)
    risk_score: float = 0.0
    risk_level: str = "low"


class PentestSuite:
    """Security scanning tools orchestrator."""

    async def port_scan(self, target: str, ports: str = "1-1000") -> ScanReport:
        """Nmap port scan via python-nmap."""
        try:
            import nmap
            scanner = nmap.PortScanner()
            scanner.scan(target, ports, arguments="-sV -T4")

            findings = []
            for host in scanner.all_hosts():
                for proto in scanner[host].all_protocols():
                    for port in scanner[host][proto]:
                        state = scanner[host][proto][port]
                        findings.append({
                            "port": port, "state": state["state"],
                            "service": state.get("name", ""), "version": state.get("version", ""),
                        })

            open_ports = [f for f in findings if f["state"] == "open"]
            risk = min(10, len(open_ports) * 0.5)
            return ScanReport(target, "port_scan", findings, risk, "low" if risk < 3 else "medium" if risk < 7 else "high")
        except Exception as e:
            return ScanReport(target, "port_scan", [{"error": str(e)}])

    async def ssl_check(self, domain: str) -> dict:
        """Check SSL certificate validity."""
        import ssl, socket
        from datetime import datetime
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(10)
                s.connect((domain, 443))
                cert = s.getpeercert()

            expire_str = cert.get("notAfter", "")
            expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (expire_date - datetime.utcnow()).days

            return {
                "domain": domain, "issuer": dict(cert.get("issuer", [[]])[0]).get("organizationName", ""),
                "expires": expire_str, "days_left": days_left,
                "valid": days_left > 0, "warning": days_left < 30,
            }
        except Exception as e:
            return {"domain": domain, "error": str(e)}


class OSINTEngine:
    """Open Source Intelligence gathering engine."""

    async def whois_lookup(self, domain: str) -> dict:
        try:
            import whois
            w = whois.whois(domain)
            return {
                "domain": domain, "registrar": w.registrar,
                "creation_date": str(w.creation_date), "expiration_date": str(w.expiration_date),
                "name_servers": w.name_servers, "status": w.status,
                "org": w.org, "country": w.country,
            }
        except Exception as e:
            return {"domain": domain, "error": str(e)}

    async def dns_recon(self, domain: str) -> dict:
        import asyncio
        try:
            import dns.resolver
            records = {}
            for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    records[rtype] = [str(r) for r in answers]
                except Exception:
                    records[rtype] = []
            return {"domain": domain, "records": records}
        except Exception as e:
            return {"domain": domain, "error": str(e)}

    async def check_headers(self, url: str) -> dict:
        """Check HTTP security headers."""
        import httpx
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(url, timeout=15)
                headers = dict(resp.headers)

                security_headers = {
                    "Content-Security-Policy": headers.get("content-security-policy"),
                    "X-Frame-Options": headers.get("x-frame-options"),
                    "X-Content-Type-Options": headers.get("x-content-type-options"),
                    "Strict-Transport-Security": headers.get("strict-transport-security"),
                    "X-XSS-Protection": headers.get("x-xss-protection"),
                    "Referrer-Policy": headers.get("referrer-policy"),
                    "Permissions-Policy": headers.get("permissions-policy"),
                }

                missing = [k for k, v in security_headers.items() if v is None]
                return {"url": url, "headers": security_headers, "missing": missing, "score": max(0, 10 - len(missing) * 1.5)}
        except Exception as e:
            return {"url": url, "error": str(e)}


class LeakChecker:
    """Check for data breaches and leaked credentials."""

    def __init__(self, hibp_api_key: str = ""):
        self.hibp_key = hibp_api_key

    async def check_email(self, email: str) -> dict:
        """Check email against Have I Been Pwned."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    headers={"hibp-api-key": self.hibp_key, "user-agent": "NexusAgent/3.0"},
                    params={"truncateResponse": "false"},
                )
                if resp.status_code == 200:
                    breaches = resp.json()
                    return {
                        "email": email, "breached": True, "breach_count": len(breaches),
                        "breaches": [{"name": b["Name"], "date": b["BreachDate"], "data_classes": b["DataClasses"]} for b in breaches[:5]],
                    }
                elif resp.status_code == 404:
                    return {"email": email, "breached": False, "breach_count": 0}
                return {"email": email, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"email": email, "error": str(e)}
