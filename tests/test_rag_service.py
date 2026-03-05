"""
Unit tests for Phase 4: self_check, RAGService, and wiring.

Uses mocks for agent, retrieval_engine, and memory so no LLM or vector store is required.
"""

import pytest


# --- self_check ---


@pytest.mark.unit
def test_self_check_empty_answer_fails():
    from adaptive_rag.services.self_check import self_check

    assert self_check("", []) is False
    assert self_check("   ", []) is False


@pytest.mark.unit
def test_self_check_non_empty_passes():
    from adaptive_rag.services.self_check import self_check

    assert self_check("Valid answer here.", []) is True
    assert self_check("Short.", [], min_length=3) is True


@pytest.mark.unit
def test_self_check_min_length():
    from adaptive_rag.services.self_check import self_check

    assert self_check("Hi", [], min_length=10) is False
    assert self_check("Hello world.", [], min_length=10) is True


@pytest.mark.unit
def test_self_check_require_source_hint():
    from adaptive_rag.services.self_check import self_check

    docs = [type("Doc", (), {"page_content": "x"})()]
    assert self_check("According to the document, yes.", docs, require_source_hint=True) is True
    assert self_check("Just yes.", docs, require_source_hint=True) is False


# --- RAGService ---


@pytest.mark.unit
def test_rag_service_ask_empty_query():
    from adaptive_rag.services.rag_service import RAGResponse, RAGService

    class MockAgent:
        def invoke(self, query, context=None, knowledge_docs=None):
            return "Never called"

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return []

    class MockMemory:
        def get_context_as_messages(self, limit=5):
            return []

        def add(self, user, assistant):
            pass

    svc = RAGService(MockAgent(), MockRetrieval(), MockMemory())
    r = svc.ask("")
    assert isinstance(r, RAGResponse)
    assert "question" in r.content.lower() or "provide" in r.content.lower()
    assert r.sources == []
    assert r.used_corrective_retry is False


@pytest.mark.unit
def test_rag_service_ask_updates_memory():
    from adaptive_rag.services.rag_service import RAGService

    class MockAgent:
        def invoke(self, query, context=None, knowledge_docs=None):
            return "Answer"

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return []

    calls = []

    class MockMemory:
        def get_context_as_messages(self, limit=5):
            return []

        def add(self, user, assistant):
            calls.append((user, assistant))

    svc = RAGService(MockAgent(), MockRetrieval(), MockMemory())
    svc.ask("What is 2+2?")
    assert len(calls) == 1
    assert calls[0][0] == "What is 2+2?"
    assert calls[0][1] == "Answer"


@pytest.mark.unit
def test_rag_service_ask_returns_response_with_sources():
    from langchain_core.documents import Document

    from adaptive_rag.services.rag_service import RAGResponse, RAGService

    class MockAgent:
        def invoke(self, query, context=None, knowledge_docs=None):
            return "Based on the docs."

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return [Document(page_content="Doc1", metadata={})]

    class MockMemory:
        def get_context_as_messages(self, limit=5):
            return []

        def add(self, user, assistant):
            pass

    svc = RAGService(MockAgent(), MockRetrieval(), MockMemory())
    r = svc.ask("Query")
    assert isinstance(r, RAGResponse)
    assert r.content == "Based on the docs."
    assert len(r.sources) == 1
    assert r.sources[0].page_content == "Doc1"


@pytest.mark.unit
def test_rag_service_corrective_retry_when_self_check_fails():
    from langchain_core.documents import Document

    from adaptive_rag.services.rag_service import RAGService

    invoke_count = 0

    class MockAgent:
        def invoke(self, query, context=None, knowledge_docs=None):
            nonlocal invoke_count
            invoke_count += 1
            # First response: too short (fails self_check). Second: long enough.
            if invoke_count == 1:
                return "No"
            return "This is a sufficiently long and valid answer."

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return [Document(page_content="x", metadata={})]

    class MockMemory:
        def get_context_as_messages(self, limit=5):
            return []

        def add(self, user, assistant):
            pass

    svc = RAGService(
        MockAgent(),
        MockRetrieval(),
        MockMemory(),
        enable_self_check=True,
        max_corrective_retries=1,
    )
    r = svc.ask("Query")
    assert invoke_count == 2
    assert r.used_corrective_retry is True
    assert "sufficiently long" in r.content


# --- Wiring: search_knowledge tool ---


@pytest.mark.unit
def test_make_search_knowledge_tool_returns_formatted_docs():
    from langchain_core.documents import Document

    from adaptive_rag.services.wiring import make_search_knowledge_tool

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return [
                Document(page_content="First chunk", metadata={}),
                Document(page_content="Second chunk", metadata={}),
            ]

    tool = make_search_knowledge_tool(MockRetrieval(), top_k=5)
    out = tool.invoke({"query": "test"})
    assert "[1]" in out and "First chunk" in out
    assert "[2]" in out and "Second chunk" in out


@pytest.mark.unit
def test_make_search_knowledge_tool_empty_retrieval():
    from adaptive_rag.services.wiring import make_search_knowledge_tool

    class MockRetrieval:
        def retrieve(self, query, strategy, top_k):
            return []

    tool = make_search_knowledge_tool(MockRetrieval())
    out = tool.invoke({"query": "test"})
    assert "No relevant" in out


# --- Phase 5: FastAPI app (route presence only; no RAG build) ---


@pytest.mark.unit
def test_mcp_app_has_ask_and_health_routes():
    from fastapi.testclient import TestClient

    from adaptive_rag.mcp.mcp_server import app

    client = TestClient(app)
    # Health does not require RAG to be loaded
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    # /ask with body; may return 503 if RAG failed to build at startup
    r2 = client.post("/ask", json={"query": "test"})
    assert r2.status_code in (200, 503)
