# ═══════════════════════════════════════════════════════════════
# NEXUS AGENT — Local Ollama LLM Agent
# Uses Nexus-3-Llama-3.1 for cost-free, private inference
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import httpx
from typing import Any

logger = logging.getLogger("nexus.agent.local")


class NexusAgent:
    """Local AI agent using Ollama with Nexus-3 model."""

    def __init__(self, config: dict[str, Any]):
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.model = config.get("ollama_model", "nexus3:latest")
        self.timeout = config.get("ollama_timeout", 120)
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        logger.info(f"🧠 Nexus Agent initialized: {self.model} @ {self.base_url}")

    async def generate(
        self,
        prompt: str,
        context: list[dict] | None = None,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        """Generate response from local Ollama model."""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation context
        if context:
            for msg in context[-10:]:  # Last 10 messages for context window
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.post("/api/chat", json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                },
            })
            response.raise_for_status()
            data = response.json()

            text = data.get("message", {}).get("content", "")
            emotion = self._detect_emotion(text)

            return {
                "text": text,
                "emotion": emotion,
                "confidence": 0.85,
                "model": self.model,
                "eval_count": data.get("eval_count", 0),
                "eval_duration_ms": data.get("eval_duration", 0) / 1_000_000,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Ollama HTTP error: {e.response.status_code}")
            raise
        except httpx.ConnectError:
            logger.error("❌ Cannot connect to Ollama. Is it running?")
            raise ConnectionError("Ollama server not reachable")

    def _detect_emotion(self, text: str) -> str:
        """Simple keyword-based emotion detection from response."""
        text_lower = text.lower()
        emotion_keywords = {
            "happy": ["senang", "baik", "hebat", "mantap", "bagus", "😊", "😄"],
            "excited": ["luar biasa", "keren", "wow", "amazing", "🔥", "🚀"],
            "sad": ["sedih", "maaf", "sayangnya", "tidak bisa", "😔"],
            "angry": ["tidak boleh", "berbahaya", "dilarang", "😤", "⚠️"],
            "curious": ["menarik", "hmm", "mari kita", "bagaimana", "🤔"],
            "surprised": ["ternyata", "tidak disangka", "😲", "wow"],
        }
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return emotion
        return "neutral"

    async def health_check(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            resp = await self.client.get("/api/tags")
            models = [m["name"] for m in resp.json().get("models", [])]
            return self.model in models
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
