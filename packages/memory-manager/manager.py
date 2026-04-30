# ═══════════════════════════════════════════════════════════════
# MEMORY MANAGER — RAG Pipeline + Knowledge Graph
# Central knowledge management for self-improving AI
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("nexus.memory.manager")


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using ChromaDB."""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.persist_dir = persist_dir
        self._collection = None
        logger.info(f"📚 RAG Pipeline initialized (dir: {persist_dir})")

    async def init(self):
        """Initialize ChromaDB collection."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = client.get_or_create_collection(
                name="nexus_knowledge",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"✅ ChromaDB collection ready ({self._collection.count()} documents)")
        except ImportError:
            logger.warning("⚠️ chromadb not installed, RAG pipeline disabled")

    async def add_knowledge(self, text: str, metadata: dict | None = None, doc_id: str | None = None):
        """Add a piece of knowledge to the vector store."""
        if not self._collection:
            return

        import hashlib
        _id = doc_id or hashlib.md5(text.encode()).hexdigest()

        self._collection.upsert(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[_id],
        )
        logger.debug(f"📥 Added knowledge: {_id[:12]}...")

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant knowledge using semantic similarity."""
        if not self._collection:
            return []

        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        docs = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            meta = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
            distance = results.get("distances", [[]])[0][i] if results.get("distances") else 0
            docs.append({
                "text": doc,
                "metadata": meta,
                "relevance": 1.0 - distance,
            })
        return docs

    async def learn_from_conversation(self, user_id: str, human_msg: str, ai_msg: str):
        """Learn from a conversation by storing it in the knowledge base."""
        combined = f"User asked: {human_msg}\nNexus answered: {ai_msg}"
        await self.add_knowledge(
            text=combined,
            metadata={"source": "conversation", "user_id": user_id},
        )


class KnowledgeGraph:
    """Neo4j-backed knowledge graph for relational knowledge."""

    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "changeme"):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        logger.info("🕸️ Knowledge Graph (Neo4j) initialized")

    async def init(self):
        """Initialize Neo4j connection."""
        try:
            from neo4j import AsyncGraphDatabase
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("✅ Neo4j connected")
        except ImportError:
            logger.warning("⚠️ neo4j not installed, Knowledge Graph disabled")

    async def add_entity(self, name: str, entity_type: str, properties: dict | None = None):
        """Add an entity node to the knowledge graph."""
        if not self._driver:
            return

        async with self._driver.session() as session:
            query = (
                f"MERGE (e:{entity_type} {{name: $name}}) "
                f"SET e += $props "
                f"RETURN e"
            )
            await session.run(query, name=name, props=properties or {})

    async def add_relation(self, from_name: str, relation: str, to_name: str, properties: dict | None = None):
        """Add a relationship between two entities."""
        if not self._driver:
            return

        async with self._driver.session() as session:
            query = (
                "MATCH (a {name: $from_name}), (b {name: $to_name}) "
                f"MERGE (a)-[r:{relation}]->(b) "
                "SET r += $props "
                "RETURN r"
            )
            await session.run(query, from_name=from_name, to_name=to_name, props=properties or {})

    async def query_related(self, entity_name: str, depth: int = 2) -> list[dict]:
        """Find entities related to a given entity."""
        if not self._driver:
            return []

        async with self._driver.session() as session:
            query = (
                f"MATCH path = (e {{name: $name}})-[*1..{depth}]-(related) "
                "RETURN related.name as name, labels(related) as types, "
                "length(path) as distance "
                "LIMIT 20"
            )
            result = await session.run(query, name=entity_name)
            records = [dict(record) async for record in result]
            return records

    async def learn_topic(self, topic: str, related_topics: list[str], user_id: str):
        """Learn topic relationships from conversation."""
        await self.add_entity(topic, "Topic", {"learned_from": user_id})
        for related in related_topics:
            await self.add_entity(related, "Topic")
            await self.add_relation(topic, "RELATED_TO", related)

    async def close(self):
        if self._driver:
            await self._driver.close()
