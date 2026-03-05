"""
Unit tests for Phase 2 RAG core: vector store, ingestion, adaptive router, retrieval engine.

Uses in-memory Chroma (no persist_directory) or a temp directory so no global state.
Tests that need embeddings/Chroma are skipped when langchain_community or langchain_chroma
are not installed (pip install -e . from repo root installs them).
"""

import tempfile
from pathlib import Path

import pytest

# Skip embedding-dependent tests if optional RAG deps are missing or broken (e.g. chromadb on Python 3.14)
def _check_rag_deps() -> bool:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings  # noqa: F401
    except ImportError:
        return False
    try:
        from langchain_chroma import Chroma  # noqa: F401
    except Exception:
        return False
    return True


_RAG_DEPS_AVAILABLE = _check_rag_deps()


@pytest.fixture
def temp_persist_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def embedding():
    """Create a small embedding model for tests (HuggingFace). Used only when _RAG_DEPS_AVAILABLE."""
    from adaptive_rag.knowledge.embedding_factory import create_embedding

    return create_embedding()


@pytest.fixture
def vector_store(embedding, temp_persist_dir):
    from adaptive_rag.knowledge.vector_store import VectorStore

    return VectorStore(
        embedding=embedding,
        persist_directory=temp_persist_dir,
        collection_name="test_rag",
    )


@pytest.mark.unit
def test_adaptive_router_chooses_hybrid_when_few_docs():
    from adaptive_rag.rag.adaptive_router import choose_strategy

    assert choose_strategy(0, min_docs_threshold=3) == "hybrid"
    assert choose_strategy(2, min_docs_threshold=3) == "hybrid"


@pytest.mark.unit
def test_adaptive_router_chooses_vector_when_enough_docs():
    from adaptive_rag.rag.adaptive_router import choose_strategy

    assert choose_strategy(3, min_docs_threshold=3) == "vector"
    assert choose_strategy(5, min_docs_threshold=3) == "vector"


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_vector_store_add_and_search(vector_store):
    from langchain_core.documents import Document

    docs = [
        Document(page_content="Alpha content here", metadata={"source": "a"}),
        Document(page_content="Beta content there", metadata={"source": "b"}),
    ]
    vector_store.add_documents(docs)
    results = vector_store.vector_search("Alpha", top_k=2)
    assert len(results) >= 1
    assert any("Alpha" in d.page_content for d in results)


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_vector_store_hybrid_search(vector_store):
    from langchain_core.documents import Document

    docs = [
        Document(page_content="First chunk", metadata={}),
        Document(page_content="Second chunk", metadata={}),
    ]
    vector_store.add_documents(docs)
    results = vector_store.hybrid_search("chunk", top_k=2)
    assert len(results) <= 2
    assert len(results) >= 1


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_retrieval_engine_vector_strategy(vector_store):
    from langchain_core.documents import Document

    from adaptive_rag.rag.retrieval_engine import RetrievalEngine

    docs = [Document(page_content="Retrieval test content", metadata={})]
    vector_store.add_documents(docs)
    engine = RetrievalEngine(vector_store, min_docs_threshold=3)
    out = engine.retrieve("Retrieval test", strategy="vector", top_k=2)
    assert isinstance(out, list)
    assert len(out) <= 2


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_retrieval_engine_adaptive_fallback(vector_store):
    from langchain_core.documents import Document

    from adaptive_rag.rag.retrieval_engine import RetrievalEngine

    # Empty store: vector returns 0, adaptive should still return list (hybrid also 0)
    engine = RetrievalEngine(vector_store, min_docs_threshold=3)
    out = engine.retrieve("anything", strategy="adaptive", top_k=5)
    assert isinstance(out, list)
    assert len(out) == 0

    # One doc: vector returns 1 < 3, so adaptive uses hybrid
    vector_store.add_documents([Document(page_content="Only one", metadata={})])
    out2 = engine.retrieve("Only", strategy="adaptive", top_k=5)
    assert isinstance(out2, list)


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_ingestion_service_ingest_documents(vector_store):
    from langchain_core.documents import Document

    from adaptive_rag.knowledge.ingestion_service import IngestionService

    service = IngestionService(vector_store, chunk_size=50, chunk_overlap=10)
    docs = [Document(page_content="A " * 30, metadata={"source": "test"})]
    n = service.ingest_documents(docs)
    assert n >= 1


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_ingestion_service_ingest_text_file(vector_store, tmp_path):
    from adaptive_rag.knowledge.ingestion_service import IngestionService

    path = tmp_path / "sample.txt"
    path.write_text("Hello world.\n\nSecond paragraph here.", encoding="utf-8")
    service = IngestionService(vector_store, chunk_size=100, chunk_overlap=0)
    n = service.ingest_file(str(path))
    assert n >= 1


@pytest.mark.unit
@pytest.mark.skipif(not _RAG_DEPS_AVAILABLE, reason="langchain_community and langchain_chroma required")
def test_ingestion_service_unsupported_extension_raises(vector_store, tmp_path):
    from adaptive_rag.knowledge.ingestion_service import IngestionService

    path = tmp_path / "file.xyz"
    path.write_text("x", encoding="utf-8")
    service = IngestionService(vector_store)
    with pytest.raises(ValueError, match="Unsupported file type"):
        service.ingest_file(str(path))


@pytest.mark.unit
def test_reranker_fallback_without_sentence_transformers():
    """Reranker returns first top_n when sentence_transformers not used or unavailable."""
    from langchain_core.documents import Document

    from adaptive_rag.rag.reranker import Reranker

    docs = [
        Document(page_content="A", metadata={}),
        Document(page_content="B", metadata={}),
        Document(page_content="C", metadata={}),
    ]
    r = Reranker()
    # May or may not have CrossEncoder; either way rerank returns list of len top_n
    out = r.rerank("query", docs, top_n=2)
    assert len(out) <= 2
    assert all(isinstance(d, Document) for d in out)
