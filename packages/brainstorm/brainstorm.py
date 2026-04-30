# ═══════════════════════════════════════════════════════════════
# BRAINSTORM — RAG Pipeline + Flowchart Generator
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import logging, json
from typing import Any

logger = logging.getLogger("nexus.brainstorm")


class BrainstormEngine:
    """RAG-powered brainstorming and flowchart generation."""

    def __init__(self):
        self._rag = None
        logger.info("💡 Brainstorm Engine initialized")

    async def init_rag(self):
        from packages.memory_manager.manager import RAGPipeline
        self._rag = RAGPipeline("data/brainstorm_knowledge")
        await self._rag.init()

    async def brainstorm(self, topic: str, context: str = "") -> dict:
        """Generate brainstorming ideas with RAG context."""
        related = []
        if self._rag:
            related = await self._rag.search(topic, top_k=3)

        ideas = self._generate_ideas(topic, context, related)
        return {
            "topic": topic,
            "ideas": ideas,
            "related_knowledge": [r["text"][:100] for r in related],
        }

    def _generate_ideas(self, topic: str, context: str, related: list) -> list[dict]:
        """Generate structured brainstorming ideas."""
        return [
            {"category": "Feature", "ideas": [
                f"Implementasi {topic} dengan pendekatan modular",
                f"Tambahkan dashboard monitoring untuk {topic}",
                f"Buat API endpoint untuk integrasi {topic}",
            ]},
            {"category": "Improvement", "ideas": [
                f"Optimasi performa {topic} dengan caching",
                f"Tambahkan unit test untuk {topic}",
                f"Implementasi error handling yang lebih baik",
            ]},
            {"category": "Innovation", "ideas": [
                f"Gunakan AI untuk auto-optimize {topic}",
                f"Tambahkan realtime monitoring dengan WebSocket",
                f"Implementasi plugin system untuk extensibility",
            ]},
        ]

    async def generate_flowchart(self, title: str, steps: list[dict]) -> str:
        """Generate Mermaid flowchart from steps."""
        lines = ["```mermaid", "flowchart TD"]
        for i, step in enumerate(steps):
            node_id = f"S{i}"
            label = step.get("label", f"Step {i+1}")
            shape = step.get("shape", "rect")

            if shape == "diamond":
                lines.append(f'    {node_id}{{{{{label}}}}}')
            elif shape == "circle":
                lines.append(f'    {node_id}(({label}))')
            else:
                lines.append(f'    {node_id}["{label}"]')

            if i > 0:
                prev = f"S{i-1}"
                edge_label = step.get("edge_label", "")
                if edge_label:
                    lines.append(f'    {prev} -->|{edge_label}| {node_id}')
                else:
                    lines.append(f'    {prev} --> {node_id}')

        lines.append("```")
        return "\n".join(lines)

    async def generate_usecase(self, system_name: str, actors: list[str], usecases: list[str]) -> str:
        """Generate PlantUML use-case diagram."""
        lines = ["@startuml", f"title {system_name} — Use Case Diagram", ""]
        for actor in actors:
            lines.append(f'actor "{actor}" as {actor.replace(" ", "_")}')
        lines.append(f'\nrectangle "{system_name}" {{')
        for uc in usecases:
            uc_id = uc.replace(" ", "_")
            lines.append(f'  usecase "{uc}" as {uc_id}')
        lines.append("}")
        for actor in actors:
            for uc in usecases[:3]:
                lines.append(f'{actor.replace(" ", "_")} --> {uc.replace(" ", "_")}')
        lines.append("@enduml")
        return "\n".join(lines)
