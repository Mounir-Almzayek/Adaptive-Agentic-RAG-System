"""
Document ingestion for the Adaptive Agentic RAG System.

Loads files (PDF, text), chunks with LangChain splitters, and indexes into
the vector store. Extensible for more formats and loaders.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from adaptive_rag.knowledge.vector_store import VectorStore

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Supported extensions and their loader names (for dispatch)
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def _load_pdf(path: str) -> list[Document]:
    from langchain_community.document_loaders import PyPDFLoader

    loader = PyPDFLoader(path)
    return loader.load()


def _load_text(path: str) -> list[Document]:
    from langchain_community.document_loaders import TextLoader

    loader = TextLoader(path, encoding="utf-8", autodetect_encoding=True)
    return loader.load()


def _load_markdown(path: str) -> list[Document]:
    from langchain_community.document_loaders import TextLoader

    loader = TextLoader(path, encoding="utf-8", autodetect_encoding=True)
    return loader.load()


_LOADERS: dict[str, Callable[[str], list[Document]]] = {
    ".pdf": _load_pdf,
    ".txt": _load_text,
    ".md": _load_markdown,
}


class IngestionService:
    """
    Load documents from disk, chunk them, and add to the vector store.

    Supports PDF, plain text, and Markdown. Chunk size and overlap are
    configurable for downstream retrieval quality.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self._store = vector_store
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def ingest_file(self, path: str | Path) -> int:
        """
        Load a single file, split into chunks, and add to the vector store.

        Returns the number of chunks indexed. Raises ValueError for unsupported format.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        suffix = path.suffix.lower()
        if suffix not in _LOADERS:
            raise ValueError(
                f"Unsupported file type: {suffix}. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
            )
        loader_fn = _LOADERS[suffix]
        try:
            docs = loader_fn(str(path))
        except Exception as e:
            logger.exception("Failed to load %s", path)
            raise RuntimeError(f"Failed to load {path}: {e}") from e
        return self.ingest_documents(docs)

    def ingest_documents(self, documents: list[Document]) -> int:
        """Split documents into chunks and add them to the vector store. Returns chunk count."""
        if not documents:
            return 0
        chunks = self._splitter.split_documents(documents)
        ids = self._store.add_documents(chunks)
        count = len(ids) if ids is not None else len(chunks)
        logger.info("Ingested %d chunks from %d document(s)", count, len(documents))
        return count

    @staticmethod
    def supported_extensions() -> set[str]:
        """Return the set of supported file extensions."""
        return set(SUPPORTED_EXTENSIONS)
