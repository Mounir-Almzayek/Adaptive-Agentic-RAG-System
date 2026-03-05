"""
RAG service: single entry point that coordinates retrieval, memory, and agent.

Keeps UI and MCP layers thin; no Streamlit or FastAPI imports here.
Optional self-check and one corrective retrieval (CRAG-style) when validation fails.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from langchain_core.documents import Document

from adaptive_rag.services.self_check import self_check as run_self_check

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RAGResponse:
    """Immutable response from RAGService.ask()."""

    content: str
    sources: list[Document]
    used_corrective_retry: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "sources", list(self.sources))


class RAGService:
    """
    Orchestrates retrieval, conversation memory, and agent for each user query.

    Dependency-injected: pass in agent, retrieval_engine, and memory so the
    service stays testable and UI-agnostic.
    """

    def __init__(
        self,
        agent: Any,
        retrieval_engine: Any,
        memory: Any,
        *,
        enable_self_check: bool = False,
        default_top_k: int = 5,
        max_corrective_retries: int = 1,
    ) -> None:
        self._agent = agent
        self._retrieval_engine = retrieval_engine
        self._memory = memory
        self._enable_self_check = enable_self_check
        self._default_top_k = default_top_k
        self._max_corrective_retries = max(0, max_corrective_retries)

    def ask(
        self,
        query: str,
        strategy: str | None = None,
        top_k: int | None = None,
    ) -> RAGResponse:
        """
        Answer the query using retrieval, context, and the agent. Update memory.

        If enable_self_check is True and validation fails, retry once with
        broader retrieval (higher top_k and/or hybrid) then return the new answer.
        """
        query = (query or "").strip()
        if not query:
            return RAGResponse(content="Please provide a question.", sources=[], used_corrective_retry=False)

        k = top_k if top_k is not None else self._default_top_k
        strat = (strategy or "adaptive").strip().lower()
        if strat not in ("vector", "hybrid", "adaptive"):
            strat = "adaptive"

        docs = self._retrieval_engine.retrieve(query, strategy=strat, top_k=k)
        context = self._memory.get_context_as_messages(limit=5)
        content = self._agent.invoke(query, context=context, knowledge_docs=docs)
        used_retry = False

        if self._enable_self_check and not run_self_check(content, docs):
            for _ in range(self._max_corrective_retries):
                retry_k = k * 2
                retry_strat = "hybrid" if strat == "vector" else strat
                docs = self._retrieval_engine.retrieve(query, strategy=retry_strat, top_k=retry_k)
                content = self._agent.invoke(query, context=context, knowledge_docs=docs)
                used_retry = True
                logger.info("self_check_failed_retry: applied corrective retrieval (top_k=%s, strategy=%s)", retry_k, retry_strat)
                if run_self_check(content, docs):
                    break

        self._memory.add(query, content)
        return RAGResponse(content=content, sources=docs, used_corrective_retry=used_retry)
