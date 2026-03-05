"""
Retrieval engine for the Adaptive Agentic RAG System.

Supports vector, hybrid, and adaptive strategies. Optional reranker
integration for production-quality relevance ordering.
"""

from __future__ import annotations

from typing import Literal, Protocol

from langchain_core.documents import Document

from adaptive_rag.rag.adaptive_router import choose_strategy
from adaptive_rag.rag.reranker import RerankerProtocol


class VectorStoreProtocol(Protocol):
    """Protocol for retrieval: only needs search methods. Keeps rag independent of knowledge."""

    def vector_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...

    def hybrid_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...


RetrievalStrategy = Literal["vector", "hybrid", "adaptive"]


class RetrievalEngine:
    """
    Single entry point for document retrieval with configurable strategy.

    - vector: dense similarity only.
    - hybrid: broader retrieval (e.g. more candidates) then trim.
    - adaptive: run vector first; if too few results, fall back to hybrid.
    """

    def __init__(
        self,
        vector_store: VectorStoreProtocol,
        *,
        min_docs_threshold: int = 3,
        reranker: RerankerProtocol | None = None,
    ) -> None:
        self._store = vector_store
        self._min_docs_threshold = min_docs_threshold
        self._reranker = reranker

    def retrieve(
        self,
        query: str,
        strategy: RetrievalStrategy | str = "adaptive",
        top_k: int = 5,
    ) -> list[Document]:
        """
        Retrieve the most relevant documents for the query.

        Args:
            query: User or agent query.
            strategy: "vector", "hybrid", or "adaptive".
            top_k: Maximum number of documents to return.

        Returns:
            List of documents, optionally reranked if a reranker is configured.
        """
        strategy = strategy.strip().lower()
        if strategy not in ("vector", "hybrid", "adaptive"):
            strategy = "adaptive"

        if strategy == "vector":
            docs = self._store.vector_search(query, top_k=top_k)
        elif strategy == "hybrid":
            docs = self._store.hybrid_search(query, top_k=top_k)
        else:
            docs = self._adaptive_retrieve(query, top_k)

        if self._reranker and docs:
            docs = self._reranker.rerank(query, docs, top_n=top_k)
        return docs

    def _adaptive_retrieve(self, query: str, top_k: int) -> list[Document]:
        """Run vector search; if result count below threshold, fall back to hybrid."""
        docs = self._store.vector_search(query, top_k=top_k)
        chosen = choose_strategy(len(docs), min_docs_threshold=self._min_docs_threshold)
        if chosen == "hybrid":
            docs = self._store.hybrid_search(query, top_k=top_k)
        return docs
