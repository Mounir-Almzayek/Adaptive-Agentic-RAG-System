"""
Vector store abstraction for the Adaptive Agentic RAG System.

Wraps LangChain Chroma with a stable interface: add_documents, vector_search,
and hybrid_search. Persistence and embedding are configured at construction.
"""

from __future__ import annotations

from typing import Protocol

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

# Default collection name; can be overridden for multi-tenant or multi-index scenarios.
DEFAULT_COLLECTION_NAME = "adaptive_rag"


class VectorStoreProtocol(Protocol):
    """Protocol for retrieval engine: only needs search methods."""

    def vector_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...

    def hybrid_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...


class VectorStore:
    """
    LangChain Chroma-backed vector store with vector and hybrid-style retrieval.

    Hybrid search is implemented as a broader vector search (2x top_k) then
    trimmed to top_k, so fallback in adaptive retrieval has more candidates.
    Full BM25 + vector fusion can be added later via a separate retriever.
    """

    def __init__(
        self,
        embedding: Embeddings,
        persist_directory: str,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        self._embedding = embedding
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        self._store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory=persist_directory,
        )

    def add_documents(self, documents: list[Document]) -> list[str] | None:
        """Embed and add documents to the store. Returns IDs if available."""
        if not documents:
            return []
        ids = self._store.add_documents(documents)
        return ids

    def vector_search(self, query: str, top_k: int = 5) -> list[Document]:
        """Return the top_k most similar documents to the query (dense only)."""
        return self._store.similarity_search(query, k=top_k)

    def hybrid_search(self, query: str, top_k: int = 5) -> list[Document]:
        """
        Broader retrieval: fetch more candidates via vector search, then return top_k.

        This gives adaptive retrieval a fallback with more coverage when vector-only
        returns few results. Full hybrid (e.g. BM25 + vector fusion) can be added later.
        """
        fetch_k = max(top_k * 2, 10)
        docs = self._store.similarity_search(query, k=min(fetch_k, 100))
        return docs[:top_k]

    @property
    def store(self) -> Chroma:
        """Expose underlying Chroma store for advanced use (e.g. direct filters)."""
        return self._store
