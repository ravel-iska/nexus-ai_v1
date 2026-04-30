# ═══════════════════════════════════════════════════════════════
# OPENROUTER AGENT — Cloud LLM Agent (GPT-4o, Claude, Gemini)
# Fallback for complex reasoning tasks
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
import httpx
from typing import Any

logger = logging.getLogger("nexus.agent.cloud")

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class OpenRouterAgent:
    """Cloud LLM agent via OpenRouter API supporting multiple models."""

    def __init__(self, config: dict[str, Any]):
        self.api_key = config.get("openrouter_api_key", "")
        self.default_model = config.get("openrouter_default_model", "anthropic/claude-sonnet-4")
        self.timeout = config.get("openrouter_timeout", 60)
        self.client = httpx.AsyncClient(
            base_url=OPENROUTER_BASE,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://nexus-agent.local",
                "X-Title": "WA Agent Nexus v3.0",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        logger.info(f"☁️ OpenRouter Agent initialized: {self.default_model}")

    async def generate(
        self,
        prompt: str,
        context: list[dict] | None = None,
        model: str | None = None,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Generate response from cloud LLM via OpenRouter."""

        selected_model = model or self.default_model
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if context:
            for msg in context[-8:]:  # Limit context for cost control
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.post("/chat/completions", json={
                "model": selected_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9,
            })
            response.raise_for_status()
            data = response.json()

            choice = data.get("choices", [{}])[0]
            text = choice.get("message", {}).get("content", "")
            usage = data.get("usage", {})

            total_tokens = usage.get("total_tokens", 0)
            cost = self._estimate_cost(selected_model, usage)

            return {
                "text": text,
                "model": selected_model,
                "confidence": 0.92,
                "tokens": total_tokens,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "cost": cost,
                "finish_reason": choice.get("finish_reason", ""),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ OpenRouter error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ OpenRouter unexpected error: {e}")
            raise

    def _estimate_cost(self, model: str, usage: dict) -> float:
        """Estimate cost in USD based on model pricing."""
        # Approximate pricing per 1M tokens (prompt/completion)
        pricing = {
            "anthropic/claude-sonnet-4": (3.0, 15.0),
            "openai/gpt-4o": (2.5, 10.0),
            "openai/gpt-4o-mini": (0.15, 0.6),
            "google/gemini-2.5-pro": (1.25, 10.0),
            "mistralai/mixtral-8x7b": (0.24, 0.24),
        }
        prompt_rate, completion_rate = pricing.get(model, (1.0, 2.0))
        prompt_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * prompt_rate
        completion_cost = (usage.get("completion_tokens", 0) / 1_000_000) * completion_rate
        return round(prompt_cost + completion_cost, 6)

    async def list_models(self) -> list[str]:
        """List available models from OpenRouter."""
        try:
            resp = await self.client.get("/models")
            return [m["id"] for m in resp.json().get("data", [])]
        except Exception:
            return []

    async def close(self):
        await self.client.aclose()
