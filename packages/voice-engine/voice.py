# ═══════════════════════════════════════════════════════════════
# VOICE ENGINE — Whisper STT + TTS + Intent Parser
# Process voice notes from WhatsApp
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger("nexus.voice")


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_seconds: float
    segments: list[dict]


class SpeechToText:
    """Whisper-based speech-to-text engine."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        logger.info(f"🎤 STT Engine initialized (Whisper {model_size})")

    async def init(self):
        if self._model is not None:
            return
        try:
            import whisper
            self._model = whisper.load_model(self.model_size)
            logger.info(f"✅ Whisper {self.model_size} model loaded")
        except ImportError:
            logger.error("❌ openai-whisper not installed. Run: pip install openai-whisper")
            raise

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """Transcribe audio bytes to text."""
        await self.init()

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            result = self._model.transcribe(
                temp_path,
                language=None,  # Auto-detect
                task="transcribe",
                fp16=False,
            )

            segments = [
                {"start": s["start"], "end": s["end"], "text": s["text"]}
                for s in result.get("segments", [])
            ]

            duration = segments[-1]["end"] if segments else 0

            return TranscriptionResult(
                text=result["text"].strip(),
                language=result.get("language", "unknown"),
                confidence=self._avg_confidence(result),
                duration_seconds=duration,
                segments=segments,
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def _avg_confidence(self, result: dict) -> float:
        segments = result.get("segments", [])
        if not segments:
            return 0.0
        probs = [1.0 - s.get("no_speech_prob", 0) for s in segments]
        return round(sum(probs) / len(probs), 4)


class TextToSpeech:
    """Text-to-speech engine using gTTS or pyttsx3."""

    def __init__(self, engine: str = "gtts", language: str = "id"):
        self.engine_type = engine
        self.language = language
        logger.info(f"🔊 TTS Engine initialized ({engine}, lang={language})")

    async def synthesize(self, text: str, language: str | None = None) -> bytes:
        """Convert text to audio bytes."""
        lang = language or self.language

        if self.engine_type == "gtts":
            return await self._gtts_synthesize(text, lang)
        elif self.engine_type == "pyttsx3":
            return await self._pyttsx3_synthesize(text)
        else:
            raise ValueError(f"Unknown TTS engine: {self.engine_type}")

    async def _gtts_synthesize(self, text: str, lang: str) -> bytes:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()

    async def _pyttsx3_synthesize(self, text: str) -> bytes:
        import pyttsx3
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            engine.save_to_file(text, f.name)
            engine.runAndWait()
            return Path(f.name).read_bytes()


class IntentParser:
    """Parse user intent from transcribed voice text."""

    INTENT_PATTERNS = {
        "search": ["cari", "carikan", "tolong cari", "search"],
        "download": ["download", "unduh", "ambil video", "ambil musik"],
        "scan": ["scan", "periksa", "cek keamanan"],
        "analyze": ["analisa", "analisis", "evaluasi"],
        "convert": ["convert", "ubah", "konversi"],
        "help": ["bantuan", "help", "tolong", "bagaimana"],
        "greeting": ["halo", "hai", "hi", "selamat"],
    }

    def parse(self, text: str) -> dict:
        """Parse intent from text."""
        text_lower = text.lower()

        for intent, keywords in self.INTENT_PATTERNS.items():
            for kw in keywords:
                if kw in text_lower:
                    # Extract the query (everything after the keyword)
                    idx = text_lower.index(kw) + len(kw)
                    query = text[idx:].strip()
                    return {
                        "intent": intent,
                        "keyword": kw,
                        "query": query,
                        "original_text": text,
                        "confidence": 0.85,
                    }

        return {
            "intent": "conversation",
            "keyword": None,
            "query": text,
            "original_text": text,
            "confidence": 0.5,
        }
