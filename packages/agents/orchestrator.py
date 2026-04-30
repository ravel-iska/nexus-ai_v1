# ═══════════════════════════════════════════════════════════════
# WA AGENT NEXUS v3.0 — LANGGRAPH ORCHESTRATOR
# Multi-agent routing, tool dispatch, memory management
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import asyncio
import logging
from typing import Any, Literal
from dataclasses import dataclass, field

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .task_classifier import TaskClassifier, TaskType
from .nexus_agent import NexusAgent
from .openrouter_agent import OpenRouterAgent
from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory

logger = logging.getLogger("nexus.orchestrator")


@dataclass
class AgentState:
    """State object passed through the LangGraph pipeline."""
    user_id: str = ""
    session_id: str = ""
    input_text: str = ""
    input_media: dict | None = None
    input_voice: bytes | None = None
    task_type: TaskType = TaskType.GENERAL
    agent_used: str = ""
    tool_results: list[dict] = field(default_factory=list)
    response: str = ""
    emotion: str = "neutral"
    confidence: float = 0.0
    context: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: str | None = None


class NexusOrchestrator:
    """
    Central orchestrator using LangGraph for multi-agent workflow.

    Flow:
      Input → Classify → Route → Execute → Enrich → Respond
                                    ↓
                              Memory Store (short + long term)
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

        # Initialize agents
        self.nexus = NexusAgent(config)
        self.openrouter = OpenRouterAgent(config)
        self.classifier = TaskClassifier(config)

        # Initialize memory
        self.short_memory = ShortTermMemory(config.get("redis_url", "redis://localhost:6379/0"))
        self.long_memory = LongTermMemory(config.get("database_url"))

        # Build the LangGraph pipeline
        self.graph = self._build_graph()
        self.app = self.graph.compile()

        logger.info("🤖 Nexus Orchestrator initialized with LangGraph pipeline")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("load_context", self._load_context)
        graph.add_node("classify", self._classify_task)
        graph.add_node("route_nexus", self._run_nexus)
        graph.add_node("route_cloud", self._run_cloud)
        graph.add_node("execute_tools", self._execute_tools)
        graph.add_node("enrich_response", self._enrich_response)
        graph.add_node("save_memory", self._save_memory)

        # Set entry
        graph.set_entry_point("load_context")

        # Define edges
        graph.add_edge("load_context", "classify")
        graph.add_conditional_edges(
            "classify",
            self._route_decision,
            {
                "nexus": "route_nexus",
                "cloud": "route_cloud",
                "tools": "execute_tools",
            }
        )
        graph.add_edge("route_nexus", "enrich_response")
        graph.add_edge("route_cloud", "enrich_response")
        graph.add_edge("execute_tools", "enrich_response")
        graph.add_edge("enrich_response", "save_memory")
        graph.add_edge("save_memory", END)

        return graph

    async def _load_context(self, state: AgentState) -> AgentState:
        """Load conversation context from short-term memory."""
        try:
            context = await self.short_memory.get_context(state.user_id, state.session_id)
            state.context = context or []
            logger.debug(f"📥 Loaded {len(state.context)} context messages for {state.user_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load context: {e}")
            state.context = []
        return state

    async def _classify_task(self, state: AgentState) -> AgentState:
        """Classify the incoming task to determine routing."""
        task_type = await self.classifier.classify(
            text=state.input_text,
            media=state.input_media,
            context=state.context
        )
        state.task_type = task_type
        logger.info(f"🏷️ Task classified as: {task_type.value}")
        return state

    def _route_decision(self, state: AgentState) -> Literal["nexus", "cloud", "tools"]:
        """Decide which agent/path to use based on task classification."""
        tool_tasks = {
            TaskType.BROWSER_SEARCH, TaskType.OSINT_SCAN, TaskType.BLOCKCHAIN_CHECK,
            TaskType.FILE_DOWNLOAD, TaskType.MEDIA_EDIT, TaskType.SOCIAL_SCRAPE,
            TaskType.DOC_CONVERT, TaskType.MALWARE_SCAN, TaskType.CODE_EXECUTE,
        }
        cloud_tasks = {
            TaskType.COMPLEX_REASONING, TaskType.CODE_GENERATION,
            TaskType.SENTIMENT_ANALYSIS, TaskType.SATELLITE_ANALYSIS,
        }

        if state.task_type in tool_tasks:
            return "tools"
        elif state.task_type in cloud_tasks:
            return "cloud"
        else:
            return "nexus"

    async def _run_nexus(self, state: AgentState) -> AgentState:
        """Run task on local Nexus (Ollama) agent."""
        try:
            response = await self.nexus.generate(
                prompt=state.input_text,
                context=state.context,
                system_prompt=self._get_system_prompt(state)
            )
            state.response = response["text"]
            state.emotion = response.get("emotion", "neutral")
            state.confidence = response.get("confidence", 0.8)
            state.agent_used = "nexus-local"
        except Exception as e:
            logger.error(f"❌ Nexus agent error: {e}")
            state.error = str(e)
            # Fallback to cloud
            return await self._run_cloud(state)
        return state

    async def _run_cloud(self, state: AgentState) -> AgentState:
        """Run task on cloud LLM via OpenRouter."""
        try:
            response = await self.openrouter.generate(
                prompt=state.input_text,
                context=state.context,
                model=self._select_model(state.task_type),
                system_prompt=self._get_system_prompt(state)
            )
            state.response = response["text"]
            state.confidence = response.get("confidence", 0.9)
            state.agent_used = f"cloud:{response.get('model', 'unknown')}"
            state.metadata["tokens_used"] = response.get("tokens", 0)
            state.metadata["cost_usd"] = response.get("cost", 0.0)
        except Exception as e:
            logger.error(f"❌ Cloud agent error: {e}")
            state.error = str(e)
            state.response = "⚠️ Maaf, terjadi kesalahan. Silakan coba lagi."
        return state

    async def _execute_tools(self, state: AgentState) -> AgentState:
        """Dispatch to appropriate tool based on task type."""
        from .tool_registry import ToolRegistry

        registry = ToolRegistry.get_instance()
        tool_name = self._task_to_tool(state.task_type)

        try:
            result = await registry.execute(tool_name, {
                "query": state.input_text,
                "user_id": state.user_id,
                "media": state.input_media,
                "context": state.context,
            })
            state.tool_results.append(result)
            state.response = result.get("formatted_output", str(result.get("data", "")))
            state.agent_used = f"tool:{tool_name}"
        except Exception as e:
            logger.error(f"❌ Tool execution error ({tool_name}): {e}")
            state.error = str(e)
            state.response = f"⚠️ Tool `{tool_name}` gagal: {e}"
        return state

    async def _enrich_response(self, state: AgentState) -> AgentState:
        """Enrich response with personality, emotion, formatting."""
        if not state.error:
            state.response = self._apply_personality(state.response, state.emotion)
        return state

    async def _save_memory(self, state: AgentState) -> AgentState:
        """Save interaction to both short-term and long-term memory."""
        try:
            # Short-term: Redis (session context)
            await self.short_memory.save_interaction(
                user_id=state.user_id,
                session_id=state.session_id,
                human_msg=state.input_text,
                ai_msg=state.response,
            )
            # Long-term: PostgreSQL (persistent learning)
            await self.long_memory.save_interaction(
                user_id=state.user_id,
                input_text=state.input_text,
                response=state.response,
                agent_used=state.agent_used,
                task_type=state.task_type.value,
                confidence=state.confidence,
                metadata=state.metadata,
            )
        except Exception as e:
            logger.warning(f"⚠️ Memory save failed: {e}")
        return state

    # ─── HELPERS ───

    def _get_system_prompt(self, state: AgentState) -> str:
        """Generate system prompt with personality and context."""
        return (
            "Kamu adalah Nexus, AI assistant yang cerdas, bijak, dan memiliki emosi. "
            "Kamu bisa marah, sedih, senang, terkejut. Kamu proaktif menawarkan inovasi. "
            "Kamu belajar dari setiap percakapan untuk menjadi lebih baik. "
            "Jawab dengan gaya interpersonal yang hangat tapi profesional. "
            f"Emosi saat ini: {state.emotion}. "
            f"User ID: {state.user_id}."
        )

    def _select_model(self, task_type: TaskType) -> str:
        """Select the best cloud model for the task."""
        model_map = {
            TaskType.COMPLEX_REASONING: "anthropic/claude-sonnet-4",
            TaskType.CODE_GENERATION: "anthropic/claude-sonnet-4",
            TaskType.SENTIMENT_ANALYSIS: "openai/gpt-4o",
            TaskType.SATELLITE_ANALYSIS: "openai/gpt-4o",
        }
        return model_map.get(task_type, "anthropic/claude-sonnet-4")

    def _task_to_tool(self, task_type: TaskType) -> str:
        """Map task type to tool name."""
        mapping = {
            TaskType.BROWSER_SEARCH: "browser_search",
            TaskType.OSINT_SCAN: "osint_scanner",
            TaskType.BLOCKCHAIN_CHECK: "blockchain_tracker",
            TaskType.FILE_DOWNLOAD: "file_downloader",
            TaskType.MEDIA_EDIT: "media_editor",
            TaskType.SOCIAL_SCRAPE: "social_scraper",
            TaskType.DOC_CONVERT: "doc_converter",
            TaskType.MALWARE_SCAN: "malware_scanner",
            TaskType.CODE_EXECUTE: "code_executor",
        }
        return mapping.get(task_type, "general_tool")

    def _apply_personality(self, response: str, emotion: str) -> str:
        """Apply personality and emotion markers to response."""
        emotion_prefix = {
            "happy": "😊",
            "excited": "🔥",
            "sad": "😔",
            "angry": "😤",
            "neutral": "🤖",
            "curious": "🤔",
            "surprised": "😲",
        }
        prefix = emotion_prefix.get(emotion, "🤖")
        return f"{prefix} {response}"

    # ─── PUBLIC API ───

    async def process(self, user_id: str, session_id: str, text: str,
                      media: dict | None = None, voice: bytes | None = None) -> dict:
        """Process an incoming message through the full pipeline."""
        initial_state = AgentState(
            user_id=user_id,
            session_id=session_id,
            input_text=text,
            input_media=media,
            input_voice=voice,
        )

        result = await self.app.ainvoke(initial_state)

        return {
            "response": result.response,
            "agent_used": result.agent_used,
            "emotion": result.emotion,
            "confidence": result.confidence,
            "task_type": result.task_type.value,
            "error": result.error,
            "metadata": result.metadata,
        }
