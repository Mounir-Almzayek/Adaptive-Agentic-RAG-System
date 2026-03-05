"""
App factory: build RAGService and dependencies with retrieval-backed search_knowledge.

Single place to wire retrieval_engine into the agent's search_knowledge tool so that
UI (Phase 5) and MCP can get a ready-to-use RAGService without duplicating logic.
"""

from __future__ import annotations

import logging
from typing import Any

from adaptive_rag.config.settings import get_settings
from adaptive_rag.core.agent_factory import create_agent
from adaptive_rag.core.model_factory import create_llm
from adaptive_rag.core.tools import calculator
from adaptive_rag.core.tool_registry import ToolRegistry
from adaptive_rag.knowledge.embedding_factory import create_embedding
from adaptive_rag.knowledge.vector_store import VectorStore
from adaptive_rag.memory.conversation_memory import ConversationMemory
from adaptive_rag.rag.retrieval_engine import RetrievalEngine
from adaptive_rag.services.rag_service import RAGService
from adaptive_rag.services.wiring import make_search_knowledge_tool

logger = logging.getLogger(__name__)


def build_rag_service(
    *,
    enable_self_check: bool = False,
    default_top_k: int = 5,
    retrieval_strategy: str | None = None,
) -> RAGService:
    """
    Build and return a RAGService with all dependencies wired.

    The agent's search_knowledge tool is backed by the same retrieval_engine
    used for the main RAG flow, so tool calls get real retrieved docs.

    Args:
        enable_self_check: If True, run post-answer validation and one corrective retry on failure.
        default_top_k: Default number of docs to retrieve per query.
        retrieval_strategy: Override config strategy (vector/hybrid/adaptive).

    Returns:
        RAGService ready for .ask(query).
    """
    settings = get_settings()
    llm = create_llm()
    embedding = create_embedding(settings.default_embedding_model)
    vector_store = VectorStore(
        embedding=embedding,
        persist_directory=settings.vector_store_path,
    )
    retrieval_engine = RetrievalEngine(
        vector_store,
        min_docs_threshold=settings.adaptive_retrieval_min_docs,
    )
    memory = ConversationMemory()

    # Registry: calculator + retrieval-backed search_knowledge (no stub)
    registry = ToolRegistry(include_builtin=False)
    registry.register(calculator)
    registry.register(
        make_search_knowledge_tool(
            retrieval_engine,
            top_k=default_top_k,
            strategy=retrieval_strategy or settings.retrieval_strategy,
        ),
    )
    tools = registry.get_tools()
    agent = create_agent(llm, tools)

    return RAGService(
        agent=agent,
        retrieval_engine=retrieval_engine,
        memory=memory,
        enable_self_check=enable_self_check,
        default_top_k=default_top_k,
    )


def build_rag_service_with_ingestion(
    *,
    enable_self_check: bool = False,
    default_top_k: int = 5,
) -> tuple[RAGService, "IngestionService"]:
    """
    Build RAGService and IngestionService for UIs that need file upload.

    Returns (rag_service, ingestion_service). IngestionService uses the same
    vector_store as the RAGService's retrieval engine.
    """
    from adaptive_rag.knowledge.ingestion_service import IngestionService

    settings = get_settings()
    llm = create_llm()
    embedding = create_embedding(settings.default_embedding_model)
    vector_store = VectorStore(
        embedding=embedding,
        persist_directory=settings.vector_store_path,
    )
    retrieval_engine = RetrievalEngine(
        vector_store,
        min_docs_threshold=settings.adaptive_retrieval_min_docs,
    )
    memory = ConversationMemory()

    registry = ToolRegistry(include_builtin=False)
    registry.register(calculator)
    registry.register(
        make_search_knowledge_tool(retrieval_engine, top_k=default_top_k, strategy=settings.retrieval_strategy),
    )
    agent = create_agent(llm, registry.get_tools())
    rag_service = RAGService(
        agent=agent,
        retrieval_engine=retrieval_engine,
        memory=memory,
        enable_self_check=enable_self_check,
        default_top_k=default_top_k,
    )
    ingestion = IngestionService(
        vector_store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return rag_service, ingestion
