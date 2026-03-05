"""
Optional reranker for retrieved documents.

Reorders documents by relevance to the query using a cross-encoder or similar.
Minimal interface so retrieval_engine can call it when configured.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from langchain_core.documents import Document

if TYPE_CHECKING:
    pass


class RerankerProtocol(Protocol):
    """Protocol for reranker: query, documents, top_n -> reordered documents."""

    def rerank(self, query: str, documents: list[Document], top_n: int) -> list[Document]:
        ...


class Reranker:
    """
    Rerank documents by relevance to the query.

    Uses a lightweight cross-encoder (e.g. sentence-transformers) when available.
    If sentence_transformers is not installed or model fails, falls back to
    returning the first top_n documents unchanged.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n: int = 5,
    ) -> None:
        self._model_name = model_name
        self._top_n = top_n
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self._model_name)
            except Exception:
                self._model = False  # type: ignore[assignment]
        return self._model if self._model is not False else None

    def rerank(self, query: str, documents: list[Document], top_n: int | None = None) -> list[Document]:
        """
        Reorder documents by relevance to the query; return at most top_n.

        If CrossEncoder is unavailable, returns documents[:top_n] unchanged.
        """
        n = top_n if top_n is not None else self._top_n
        if not documents:
            return []
        if n >= len(documents):
            return list(documents)

        model = self._get_model()
        if model is None:
            return list(documents)[:n]

        pairs = [(query, doc.page_content) for doc in documents]
        try:
            scores = model.predict(pairs)
        except Exception:
            return list(documents)[:n]

        indexed = list(zip(scores, documents, range(len(documents))))
        indexed.sort(key=lambda x: (float(x[0]), -x[2]), reverse=True)
        return [doc for _, doc, _ in indexed[:n]]
