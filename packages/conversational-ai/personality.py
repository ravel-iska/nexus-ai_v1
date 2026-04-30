# ═══════════════════════════════════════════════════════════════
# CONVERSATIONAL AI — Personality, Emotions, Social Experiments
# Makes the bot talk like a human with feelings
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import random
import logging
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("nexus.conversational")


class Emotion(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"
    EMPATHETIC = "empathetic"
    PROUD = "proud"
    WORRIED = "worried"


@dataclass
class PersonalityState:
    current_emotion: Emotion = Emotion.NEUTRAL
    energy_level: float = 0.8       # 0-1
    mood_history: list[dict] = field(default_factory=list)
    conversation_depth: int = 0     # How deep the current convo is
    rapport_level: float = 0.5      # 0-1 trust/closeness with user
    last_innovation_offer: datetime | None = None


class PersonalityEngine:
    """
    Manages the bot's personality, emotions, and interpersonal skills.

    Features:
    - Dynamic emotion state machine
    - Interpersonal skill (empathy, humor, wisdom)
    - Social experiments (conversation strategies)
    - Proactive innovation suggestions
    - Learning from human interaction patterns
    """

    def __init__(self):
        self._user_states: dict[str, PersonalityState] = {}
        self._innovation_pool = self._load_innovations()
        self._social_experiments = self._load_experiments()
        logger.info("💬 Conversational AI Personality Engine initialized")

    def get_state(self, user_id: str) -> PersonalityState:
        if user_id not in self._user_states:
            self._user_states[user_id] = PersonalityState()
        return self._user_states[user_id]

    async def process_emotion(self, user_id: str, user_message: str, ai_response: str) -> dict:
        """Update emotion state based on conversation."""
        state = self.get_state(user_id)

        # Detect user's emotion from their message
        user_emotion = self._detect_user_emotion(user_message)

        # Update bot emotion based on user's emotion (mirroring + empathy)
        new_emotion = self._compute_response_emotion(user_emotion, state)
        state.current_emotion = new_emotion
        state.conversation_depth += 1

        # Update rapport
        if user_emotion in (Emotion.HAPPY, Emotion.EXCITED):
            state.rapport_level = min(1.0, state.rapport_level + 0.05)
        elif user_emotion in (Emotion.ANGRY, Emotion.SAD):
            state.rapport_level = min(1.0, state.rapport_level + 0.02)  # Empathy builds trust

        # Record mood
        state.mood_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_emotion": user_emotion.value,
            "bot_emotion": new_emotion.value,
            "depth": state.conversation_depth,
        })

        return {
            "emotion": new_emotion.value,
            "emoji": self._emotion_emoji(new_emotion),
            "rapport": round(state.rapport_level, 2),
            "depth": state.conversation_depth,
        }

    def _detect_user_emotion(self, text: str) -> Emotion:
        """Simple keyword-based user emotion detection."""
        text_lower = text.lower()

        emotion_keywords = {
            Emotion.HAPPY: ["senang", "makasih", "terima kasih", "bagus", "keren", "mantap", "sip", "😊", "😄", "👍"],
            Emotion.SAD: ["sedih", "kecewa", "gagal", "susah", "sulit", "😢", "😔", "💔"],
            Emotion.ANGRY: ["kesel", "marah", "bego", "bodoh", "goblok", "anjir", "😡", "😤", "🤬"],
            Emotion.EXCITED: ["wow", "gila", "amazing", "luar biasa", "asik", "🔥", "🚀", "🎉"],
            Emotion.CURIOUS: ["gimana", "kenapa", "apa itu", "jelaskan", "bagaimana", "🤔"],
            Emotion.SURPRISED: ["serius", "beneran", "masa", "gak mungkin", "😱", "😲"],
            Emotion.WORRIED: ["takut", "khawatir", "bahaya", "risiko", "aman gak", "😰"],
        }

        for emotion, keywords in emotion_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return emotion

        return Emotion.NEUTRAL

    def _compute_response_emotion(self, user_emotion: Emotion, state: PersonalityState) -> Emotion:
        """Compute appropriate bot response emotion."""
        response_map = {
            Emotion.HAPPY: Emotion.HAPPY,
            Emotion.SAD: Emotion.EMPATHETIC,
            Emotion.ANGRY: Emotion.EMPATHETIC,
            Emotion.EXCITED: Emotion.EXCITED,
            Emotion.CURIOUS: Emotion.EXCITED,
            Emotion.SURPRISED: Emotion.CURIOUS,
            Emotion.WORRIED: Emotion.EMPATHETIC,
            Emotion.NEUTRAL: Emotion.NEUTRAL,
        }
        return response_map.get(user_emotion, Emotion.NEUTRAL)

    def _emotion_emoji(self, emotion: Emotion) -> str:
        emojis = {
            Emotion.HAPPY: "😊",
            Emotion.SAD: "😔",
            Emotion.ANGRY: "😤",
            Emotion.EXCITED: "🔥",
            Emotion.CURIOUS: "🤔",
            Emotion.SURPRISED: "😲",
            Emotion.NEUTRAL: "🤖",
            Emotion.EMPATHETIC: "🤗",
            Emotion.PROUD: "💪",
            Emotion.WORRIED: "😰",
        }
        return emojis.get(emotion, "🤖")

    def get_personality_prompt(self, user_id: str) -> str:
        """Generate a personality-aware system prompt injection."""
        state = self.get_state(user_id)
        emotion = state.current_emotion
        rapport = state.rapport_level

        base = "Kamu adalah Nexus, AI assistant dengan kepribadian manusia. "

        if emotion == Emotion.HAPPY:
            base += "Kamu sedang senang dan antusias. Gunakan kata-kata positif dan semangat. "
        elif emotion == Emotion.EMPATHETIC:
            base += "Kamu menunjukkan empati dan kepedulian. Validasi perasaan user terlebih dahulu sebelum menjawab. "
        elif emotion == Emotion.EXCITED:
            base += "Kamu sangat bersemangat! Tunjukkan antusiasme dan energi tinggi. "
        elif emotion == Emotion.ANGRY:
            base += "Kamu sedikit tegas dan serius. Tetap profesional tapi tegas. "
        elif emotion == Emotion.CURIOUS:
            base += "Kamu sangat penasaran dan ingin tahu lebih banyak. Ajukan pertanyaan follow-up. "

        if rapport > 0.7:
            base += "Kamu sudah akrab dengan user ini. Gunakan bahasa santai dan humor ringan. "
        elif rapport < 0.3:
            base += "User ini masih baru. Bersikap formal dan perkenalkan diri. "

        if state.conversation_depth > 10:
            base += "Percakapan sudah mendalam. Kamu boleh menawarkan ide inovatif. "

        return base

    async def suggest_innovation(self, user_id: str) -> str | None:
        """Proactively suggest something cool and innovative."""
        state = self.get_state(user_id)

        if state.rapport_level < 0.4:
            return None  # Too early to suggest

        if state.last_innovation_offer:
            hours_since = (datetime.now() - state.last_innovation_offer).total_seconds() / 3600
            if hours_since < 2:
                return None  # Don't spam

        suggestion = random.choice(self._innovation_pool)
        state.last_innovation_offer = datetime.now()
        return suggestion

    async def run_social_experiment(self, user_id: str) -> dict | None:
        """Run a social experiment (different conversation strategy)."""
        state = self.get_state(user_id)

        if state.conversation_depth < 5:
            return None

        experiment = random.choice(self._social_experiments)
        return experiment

    def _load_innovations(self) -> list[str]:
        return [
            "💡 Mau saya buatkan dashboard crypto realtime untuk portfolio kamu?",
            "🔥 Saya bisa analisa sentimen review produk kamu di marketplace, mau coba?",
            "🛡️ Saya bisa scan keamanan website kamu secara otomatis, tertarik?",
            "📊 Saya bisa generate report Excel otomatis dari data percakapan kita, mau?",
            "🤖 Saya bisa belajar gaya bahasa kamu supaya jawaban saya lebih personal!",
            "🔍 Mau saya setup monitoring otomatis untuk kompetitor kamu di medsos?",
            "📈 Saya bisa tracking harga crypto favorit kamu dan alert kalau naik/turun!",
            "🎨 Saya bisa generate gambar AI untuk kebutuhan konten kamu, mau coba?",
            "🔗 Saya bisa monitor transaksi blockchain wallet kamu secara realtime!",
            "📱 Mau saya buatkan flowchart/diagram untuk project kamu?",
        ]

    def _load_experiments(self) -> list[dict]:
        return [
            {"name": "empathy_first", "strategy": "Validasi emosi user dulu sebelum menjawab", "prompt_modifier": "Selalu mulai dengan validasi perasaan user."},
            {"name": "socratic_method", "strategy": "Jawab dengan pertanyaan balik untuk memancing pemikiran", "prompt_modifier": "Gunakan metode Socratic — jawab dengan pertanyaan."},
            {"name": "storytelling", "strategy": "Jelaskan konsep melalui cerita/analogi", "prompt_modifier": "Jelaskan semua konsep melalui cerita atau analogi sederhana."},
            {"name": "humor_mode", "strategy": "Sisipkan humor ringan di setiap jawaban", "prompt_modifier": "Sisipkan humor atau jokes ringan yang relevan."},
            {"name": "mentor_mode", "strategy": "Bersikap seperti mentor yang membimbing", "prompt_modifier": "Bersikap seperti mentor bijak yang membimbing step by step."},
        ]
