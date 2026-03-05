# Knowledge: vector store, ingestion, embeddings

from adaptive_rag.knowledge.embedding_factory import create_embedding
from adaptive_rag.knowledge.ingestion_service import IngestionService
from adaptive_rag.knowledge.vector_store import VectorStore, VectorStoreProtocol

__all__ = [
    "create_embedding",
    "IngestionService",
    "VectorStore",
    "VectorStoreProtocol",
]
