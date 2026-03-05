"""
Vector store abstraction for the Adaptive Agentic RAG System.

Uses Chroma when available; falls back to FAISS on Python 3.14 (where Chroma fails).
Same interface: add_documents, vector_search, hybrid_search.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# Default collection name; can be overridden for multi-tenant or multi-index scenarios.
DEFAULT_COLLECTION_NAME = "adaptive_rag"


def _chroma_available() -> bool:
    """Return True if Chroma can be imported (fails on Python 3.14 due to chromadb/pydantic)."""
    try:
        import chromadb  # noqa: F401
        return True
    except Exception:
        return False


class VectorStoreProtocol(Protocol):
    """Protocol for retrieval engine: only needs search methods."""

    def vector_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...

    def hybrid_search(self, query: str, top_k: int = 5) -> list[Document]:
        ...


class VectorStore:
    """
    Unified vector store: Chroma when available, otherwise FAISS (Python 3.14 compatible).

    Same interface: add_documents, vector_search, hybrid_search. Hybrid is implemented
    as broader vector search then trim. Persistence path is used for Chroma or FAISS save/load.
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
        self._store: Any = None
        self._use_faiss = not _chroma_available()
        if self._use_faiss:
            self._init_faiss()
        else:
            self._init_chroma()

    def _init_chroma(self) -> None:
        from langchain_chroma import Chroma

        self._store = Chroma(
            collection_name=self._collection_name,
            embedding_function=self._embedding,
            persist_directory=self._persist_directory,
        )

    def _init_faiss(self) -> None:
        from langchain_community.vectorstores import FAISS

        path = Path(self._persist_directory)
        index_file = path / "index.faiss"
        if index_file.exists():
            self._store = FAISS.load_local(
                str(path),
                self._embedding,
                allow_dangerous_deserialization=True,
            )
        else:
            path.mkdir(parents=True, exist_ok=True)
            self._store = FAISS.from_documents(
                [Document(page_content=" ", metadata={"__placeholder": True})],
                self._embedding,
            )
            self._store.save_local(
                self._persist_directory,
                index_name="index",
            )

    def add_documents(self, documents: list[Document]) -> list[str] | None:
        """Embed and add documents to the store. Returns IDs if available."""
        if not documents:
            return []
        if self._use_faiss:
            self._store.add_documents(documents)
            self._store.save_local(self._persist_directory, index_name="index")
            return None
        return self._store.add_documents(documents)

    def vector_search(self, query: str, top_k: int = 5) -> list[Document]:
        """Return the top_k most similar documents to the query (dense only)."""
        docs = self._store.similarity_search(query, k=top_k)
        if self._use_faiss:
            docs = [d for d in docs if not d.metadata.get("__placeholder")]
        return docs

    def hybrid_search(self, query: str, top_k: int = 5) -> list[Document]:
        """
        Broader retrieval: fetch more candidates via vector search, then return top_k.
        """
        fetch_k = max(top_k * 2, 10)
        docs = self._store.similarity_search(query, k=min(fetch_k, 100))
        if self._use_faiss:
            docs = [d for d in docs if not d.metadata.get("__placeholder")]
        return docs[:top_k]

    @property
    def store(self) -> Any:
        """Expose underlying store for advanced use."""
        return self._store
