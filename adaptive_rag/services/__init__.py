# Services: RAG service, orchestration

from adaptive_rag.services.rag_service import RAGResponse, RAGService
from adaptive_rag.services.self_check import self_check

# Lazy import to avoid pulling Chroma/settings when only RAGService or self_check is used
def __getattr__(name: str):
    if name in ("build_rag_service", "build_rag_service_with_ingestion"):
        from adaptive_rag.services.app_factory import build_rag_service, build_rag_service_with_ingestion
        return build_rag_service if name == "build_rag_service" else build_rag_service_with_ingestion
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "build_rag_service",
    "build_rag_service_with_ingestion",
    "RAGResponse",
    "RAGService",
    "self_check",
]
