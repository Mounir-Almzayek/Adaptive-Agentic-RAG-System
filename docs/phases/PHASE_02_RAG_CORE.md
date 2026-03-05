# Phase 2 — RAG Core

**Goal:** Implement the knowledge layer (vector store, ingestion) and the retrieval engine with vector, hybrid, and adaptive strategies. Optional reranker. LangChain used throughout.

---

## Objectives

1. Implement a vector store abstraction (LangChain vectorstore: Chroma or FAISS) with `vector_search` and, if supported, `hybrid_search`.
2. Implement an ingestion service that loads documents (e.g. PDF, text), chunks them (LangChain text splitter), and indexes into the vector store.
3. Implement a retrieval engine that supports strategies: `vector`, `hybrid`, `adaptive`.
4. Implement an adaptive router (simple heuristic: e.g. if vector returns fewer than N docs, fall back to hybrid or broaden search).
5. Optionally implement a reranker module that reorders retrieved chunks (e.g. cross-encoder or LangChain reranker).

---

## Dependencies

- Phase 1 complete (config, settings).
- LangChain, embedding model (e.g. OpenAI embeddings or OpenRouter-compatible), Chroma or FAISS.

---

## File-by-File Tasks

### 1. `knowledge/vector_store.py`

- Class (e.g. `VectorStore` or wrapper around LangChain vectorstore) that:
  - Accepts embedding model and persistence path (from config).
  - `add_documents(documents: list[Document])` — embed and add to store.
  - `vector_search(query: str, top_k: int = 5)` — returns list of documents (or similar) with metadata.
  - `hybrid_search(query: str, top_k: int = 5)` — if using Chroma with hybrid support, use it; otherwise implement as vector_search or BM25+vector fusion in a simple form.
- Use LangChain’s Chroma or FAISS integration; hide implementation details behind a small interface so retrieval_engine only sees `vector_search` and `hybrid_search`.

### 2. `knowledge/ingestion_service.py`

- Class `IngestionService`:
  - Constructor: takes vector store instance (from `vector_store.py`) and optional chunk size/overlap.
  - `ingest_file(path: str)` or `ingest_documents(documents: list[Document])`: load with LangChain loaders (e.g. PyPDFLoader, TextLoader), split with RecursiveCharacterTextSplitter (or equivalent), then call `vector_store.add_documents()`.
  - Support at least PDF and plain text; extensible for more types later.
- Use config for chunk size/overlap if desired.

### 3. `rag/retrieval_engine.py`

- Class `RetrievalEngine`:
  - Constructor: takes vector store (or interface with `vector_search` and `hybrid_search`).
  - `retrieve(query: str, strategy: str = "adaptive", top_k: int = 5)`:
    - `strategy == "vector"`: return `vector_store.vector_search(query, top_k)`.
    - `strategy == "hybrid"`: return `vector_store.hybrid_search(query, top_k)`.
    - `strategy == "adaptive"`: call `_adaptive_retrieve(query, top_k)`.
  - `_adaptive_retrieve(query, top_k)`: run vector search; if result count &lt; threshold (e.g. 3), fall back to hybrid or increase top_k and retry; return list of docs.
- Optional: accept a reranker in constructor; if present, run reranker on retrieved docs before returning.

### 4. `rag/adaptive_router.py`

- Module or class that encapsulates “when to use which strategy.”
- Function or method: `choose_strategy(query: str, vector_result_count: int) -> str` (e.g. return `"vector"` or `"hybrid"`).
- Simple rule: e.g. if `vector_result_count < 3` then `"hybrid"`, else `"vector"`. Can be extended later with a classifier.

### 5. `rag/reranker.py` (optional)

- Class or function: `rerank(query: str, documents: list, top_n: int) -> list` — reorder documents by relevance (e.g. cross-encoder). Integrate with LangChain if a reranker abstraction exists; otherwise keep a minimal interface so retrieval_engine can call it.

---

## Acceptance Criteria

- [ ] Vector store persists and can be populated via ingestion service.
- [ ] Ingestion service loads PDF and/or text, chunks, and indexes.
- [ ] RetrievalEngine.retrieve() works for `vector`, `hybrid`, and `adaptive` strategies.
- [ ] Adaptive strategy uses a simple fallback (e.g. low result count → hybrid).
- [ ] Optional reranker integrates without breaking existing retrieval flow.
- [ ] All components use LangChain where applicable (loaders, splitters, vectorstore).

---

## Out of Scope

- Agent, memory, UI. Those are in Phase 3, 4, and 5.

---

## Next Phase

Proceed to [PHASE_04_SERVICE_LAYER.md](PHASE_04_SERVICE_LAYER.md) after Phase 2 (and Phase 3) are done.
