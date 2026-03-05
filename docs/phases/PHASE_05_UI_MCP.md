# Phase 5 — UI & MCP

**Goal:** Add the Streamlit chat UI as a thin view layer and expose the RAG system as tools via a FastAPI-based MCP layer so external agents can call it.

---

## Objectives

1. Implement a Streamlit app that: displays chat, allows file upload for ingestion, allows provider/model selection (from config), and calls only `RAGService.ask()` for each user message.
2. Implement an MCP layer (FastAPI app) with at least one endpoint that maps to “search knowledge” or “ask” (e.g. `POST /tool/search_knowledge` or `POST /ask`) and returns the RAG response.
3. Ensure RAGService (and its dependencies) are instantiated once and reused (e.g. in Streamlit session state or FastAPI app state).
4. Document how to run the app and the MCP server (e.g. README or docs).

---

## Dependencies

- Phase 4 complete (RAGService and wiring).

---

## File-by-File Tasks

### 1. `app/streamlit_app.py`

- Entry point: `streamlit run app/streamlit_app.py` (or from repo root).
- Components:
  - **Sidebar:** Provider/model dropdown (from settings or env); optional retrieval strategy; “Upload document” for ingestion (calls IngestionService). Optional: clear memory button.
  - **Main area:** Chat UI (messages from session state). On user submit: call `RAGService.ask(query)`, append user message and assistant response to session state, display in chat.
- **Initialization:** In session state, create or reuse: settings, vector store, retrieval engine, memory, agent (with model_factory + tool_registry), RAGService. Lazy init on first message or on “Load” so startup is fast.
- No business logic in the app: only UI and single call to `rag_service.ask(query)` and ingestion service for uploads.
- Use English for labels/placeholders unless product requires Arabic.

### 2. `mcp/mcp_server.py`

- FastAPI app (e.g. `app = FastAPI()`).
- **Lifespan or startup:** Create RAGService and dependencies once (model, retrieval_engine, memory, agent, then RAGService). Store in `app.state.rag_service`.
- **Endpoints:**
  - `POST /tool/search_knowledge` or `POST /ask`: body `{ "query": "..." }`, response `{ "answer": "...", "sources": [...] }` (or similar). Call `app.state.rag_service.ask(query)` and return structured response.
  - Optional: `POST /ingest` for document ingestion if MCP clients should trigger ingestion.
- CORS if needed for external callers. Document that this is “MCP-ready” in the sense that external agents can use it as a tool; actual MCP protocol compliance can be a later iteration.
- Run with uvicorn: `uvicorn mcp.mcp_server:app --reload`.

### 3. Dependency Injection / App Factory (optional but recommended)

- Optional file: `services/app_factory.py` or `app/deps.py` that builds: settings → model → vector_store → retrieval_engine → ingestion_service, memory, tool_registry (with search_knowledge wired to retrieval_engine), agent, RAGService. Both Streamlit and FastAPI can call this factory so wiring lives in one place.
- If not a separate file, document in ARCHITECTURE where the wiring is done (e.g. inside `streamlit_app.py` and `mcp_server.py` with duplicated logic minimized).

### 4. Documentation

- README or `docs/RUNNING.md`: how to set `.env`, run `streamlit run app/streamlit_app.py`, run `uvicorn mcp.mcp_server:app --port 8000`. List required env vars again.

---

## Acceptance Criteria

- [ ] Streamlit app runs and displays chat; user can send a message and get a response from RAGService.
- [ ] File upload triggers ingestion into the vector store (and user sees success/error).
- [ ] Provider/model and retrieval strategy can be selected from UI or config.
- [ ] FastAPI app exposes at least one RAG endpoint; calling it returns the same kind of answer as the UI.
- [ ] No business logic in Streamlit beyond calling service and ingestion; no business logic in MCP beyond calling RAGService.
- [ ] Running instructions are documented.

---

## Out of Scope

- Authentication, rate limiting, multi-tenancy (future SaaS).
- Full MCP protocol (stdin/stdio or spec-compliant JSON-RPC) — can be added later; HTTP tool endpoint is sufficient for “MCP-ready” in this phase.

---

## End of Phased Implementation

After Phase 5, the system is end-to-end: config, model, RAG, agent, memory, service, UI, and MCP API. Next steps (from PROJECT_OVERVIEW) could be: multi-agent, n8n, SaaS features, or cost-aware routing.
