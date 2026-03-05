"""
Embedding model factory for the Adaptive Agentic RAG System.

Provides a single place to create LangChain Embeddings from config, so that
vector store and ingestion can stay embedding-agnostic. Default is a local
model (HuggingFace) to avoid requiring a separate API key for embeddings.
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Default model: small, fast, good for retrieval; no API key required
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def create_embedding(
    model_name: str | None = None,
) -> Embeddings:
    """
    Create a LangChain Embeddings instance for the vector store.

    Uses HuggingFace sentence-transformers by default so the RAG pipeline
    works with only OPENROUTER_API_KEY (for the LLM). For OpenAI embeddings
    or other providers, extend this factory and config.

    Args:
        model_name: HuggingFace model id. Defaults to all-MiniLM-L6-v2.

    Returns:
        Embeddings instance (e.g. HuggingFaceEmbeddings).
    """
    name = (model_name or DEFAULT_EMBEDDING_MODEL).strip()
    return HuggingFaceEmbeddings(
        model_name=name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
