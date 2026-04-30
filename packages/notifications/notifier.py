# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS — Gmail, Telegram, Webhook (Slack/Discord)
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import os, logging, base64
from typing import Any
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("nexus.notifications")


class GmailNotifier:
    """Send notifications via Gmail API."""

    def __init__(self):
        self._service = None
        logger.info("📧 Gmail Notifier initialized")

    async def init(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.send"])
            self._service = build("gmail", "v1", credentials=creds)
        except Exception as e:
            logger.warning(f"⚠️ Gmail init failed: {e}")

    async def send(self, to: str, subject: str, html_body: str):
        if not self._service:
            await self.init()
        msg = MIMEMultipart("alternative")
        msg["to"] = to
        msg["subject"] = subject
        msg.attach(MIMEText(html_body, "html"))
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        try:
            self._service.users().messages().send(userId="me", body={"raw": raw}).execute()
            logger.info(f"📧 Email sent to {to}: {subject}")
        except Exception as e:
            logger.error(f"❌ Gmail send error: {e}")

    async def send_error_report(self, error_data: dict):
        subject = f"🚨 [{error_data.get('type', 'ERROR')}] — WA Nexus v3.0"
        html = f"""<h2 style="color:#ff2d78">🚨 {error_data.get('type')}</h2>
        <p><b>Message:</b> {error_data.get('message')}</p>
        <pre style="background:#0d0d1a;color:#dde2f0;padding:16px;border-radius:8px">{error_data.get('traceback','')}</pre>
        <h3>🤖 AI Diagnosis</h3><p>{error_data.get('ai_diagnosis', {}).get('cause', '')}</p>"""
        await self.send(os.getenv("ADMIN_EMAIL", ""), subject, html)


class TelegramNotifier:
    """Send notifications via Telegram Bot."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    async def send(self, message: str, parse_mode: str = "HTML"):
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"https://api.telegram.org/bot{self.token}/sendMessage", json={
                    "chat_id": self.chat_id, "text": message, "parse_mode": parse_mode,
                })
        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")


class WebhookSender:
    """Send notifications to Slack/Discord via webhooks."""

    async def send_discord(self, webhook_url: str, content: str, embeds: list | None = None):
        import httpx
        payload = {"content": content}
        if embeds:
            payload["embeds"] = embeds
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)

    async def send_slack(self, webhook_url: str, text: str, blocks: list | None = None):
        import httpx
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=payload)


class NotificationHub:
    """Central notification dispatcher."""

    def __init__(self):
        self.gmail = GmailNotifier()
        self.telegram = TelegramNotifier()
        self.webhook = WebhookSender()

    async def notify_all(self, message: str, severity: str = "info"):
        """Send notification to all configured channels."""
        if severity in ("critical", "error"):
            await self.telegram.send(f"🚨 {message}")
        if severity == "critical":
            await self.gmail.send(os.getenv("ADMIN_EMAIL", ""), f"🚨 CRITICAL: Nexus", f"<p>{message}</p>")
        logger.info(f"📢 Notification sent ({severity}): {message[:80]}")
