# ═══════════════════════════════════════════════════════════════
# ML ENGINE — Sentiment Analysis
# Pre-trained BERT/RoBERTa for text sentiment classification
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger("nexus.ml.sentiment")


@dataclass
class SentimentResult:
    label: str          # positive, negative, neutral
    score: float        # confidence 0-1
    summary: str        # AI-generated summary
    details: dict       # per-sentence breakdown


class SentimentAnalyzer:
    """Sentiment analysis using HuggingFace transformers."""

    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        self.model_name = model_name
        self._pipeline = None
        self._summarizer = None
        logger.info(f"🧠 Sentiment Analyzer initialized: {model_name}")

    async def init(self):
        """Lazy-load the model pipeline."""
        if self._pipeline is not None:
            return

        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=-1,  # CPU, use 0 for GPU
                truncation=True,
                max_length=512,
            )
            logger.info("✅ Sentiment model loaded")
        except ImportError:
            logger.error("❌ transformers not installed. Run: pip install transformers torch")
            raise

    async def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of a text."""
        await self.init()

        # Split into sentences for detailed analysis
        sentences = self._split_sentences(text)
        results = []

        for sentence in sentences:
            if len(sentence.strip()) < 3:
                continue
            pred = self._pipeline(sentence[:512])[0]
            results.append({
                "text": sentence,
                "label": self._normalize_label(pred["label"]),
                "score": round(pred["score"], 4),
            })

        # Overall sentiment = weighted average
        if not results:
            return SentimentResult("neutral", 0.5, "Teks terlalu pendek untuk dianalisa.", {})

        pos_count = sum(1 for r in results if r["label"] == "positive")
        neg_count = sum(1 for r in results if r["label"] == "negative")
        neu_count = sum(1 for r in results if r["label"] == "neutral")
        total = len(results)

        avg_score = sum(r["score"] for r in results) / total

        if pos_count > neg_count and pos_count > neu_count:
            overall = "positive"
        elif neg_count > pos_count and neg_count > neu_count:
            overall = "negative"
        else:
            overall = "neutral"

        summary = self._generate_summary(overall, pos_count, neg_count, neu_count, total)

        return SentimentResult(
            label=overall,
            score=round(avg_score, 4),
            summary=summary,
            details={
                "sentences": results,
                "positive_ratio": round(pos_count / total, 2),
                "negative_ratio": round(neg_count / total, 2),
                "neutral_ratio": round(neu_count / total, 2),
            },
        )

    def _normalize_label(self, label: str) -> str:
        """Normalize model output to pos/neg/neu."""
        label = label.lower()
        if "1" in label or "2" in label or "neg" in label:
            return "negative"
        elif "4" in label or "5" in label or "pos" in label:
            return "positive"
        return "neutral"

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        import re
        return [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]

    def _generate_summary(self, overall: str, pos: int, neg: int, neu: int, total: int) -> str:
        """Generate AI-like summary of sentiment analysis."""
        emoji = {"positive": "😊", "negative": "😔", "neutral": "😐"}.get(overall, "🤔")
        summary_map = {
            "positive": f"{emoji} Analisis menunjukkan sentimen POSITIF secara keseluruhan. "
                       f"Dari {total} kalimat: {pos} positif, {neg} negatif, {neu} netral. "
                       f"Teks menunjukkan nada optimis dan mendukung.",
            "negative": f"{emoji} Analisis menunjukkan sentimen NEGATIF secara keseluruhan. "
                       f"Dari {total} kalimat: {pos} positif, {neg} negatif, {neu} netral. "
                       f"Teks menunjukkan ketidakpuasan atau kritik.",
            "neutral": f"{emoji} Analisis menunjukkan sentimen NETRAL secara keseluruhan. "
                      f"Dari {total} kalimat: {pos} positif, {neg} negatif, {neu} netral. "
                      f"Teks bersifat informatif tanpa kecenderungan emosional kuat.",
        }
        return summary_map.get(overall, "Tidak dapat menentukan sentimen.")
