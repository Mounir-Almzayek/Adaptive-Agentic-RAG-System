# Implementation Phases — Adaptive Agentic RAG System

This document is the **master roadmap**. Each phase has a dedicated file in `docs/phases/` with detailed tasks, file list, and acceptance criteria. Implementation starts only after planning sign-off.

---

## Phase Summary

| Phase | Name | Focus | Deliverables |
|-------|------|--------|--------------|
| **1** | Foundation | Project layout, config, model factory (OpenRouter + LangChain) | `config/settings.py`, `core/model_factory.py`, package structure, `.env.example` |
| **2** | RAG Core | Vector store, ingestion, retrieval engine, adaptive router, optional reranker | `knowledge/`, `rag/` implemented and testable |
| **3** | Agent & Memory | Agent factory, tool registry, conversation memory | `core/agent_factory.py`, `core/tool_registry.py`, `memory/conversation_memory.py` |
| **4** | Service Layer | RAGService, self-check, CRAG-style corrective loop | `services/rag_service.py`, optional validator/retry logic |
| **5** | UI & MCP | Streamlit app, MCP API | `app/streamlit_app.py`, `mcp/mcp_server.py` |

---

## Dependencies Between Phases

```
Phase 1 (Foundation)
    │
    ├──► Phase 2 (RAG Core) ──► Phase 4 (Service Layer)
    │
    └──► Phase 3 (Agent & Memory) ──► Phase 4 (Service Layer)
                                        │
                                        └──► Phase 5 (UI & MCP)
```

- **Phase 1** must be done first (config and model factory).
- **Phases 2 and 3** can be done in parallel after Phase 1 (RAG vs Agent/Memory).
- **Phase 4** depends on both 2 and 3 (RAGService wires RAG + Agent + Memory).
- **Phase 5** depends on Phase 4 (UI and MCP call RAGService).

---

## Phase Files

| Phase | Document | Content |
|-------|----------|---------|
| 1 | [PHASE_01_FOUNDATION.md](phases/PHASE_01_FOUNDATION.md) | Package layout, settings, model factory, OpenRouter + LangChain |
| 2 | [PHASE_02_RAG_CORE.md](phases/PHASE_02_RAG_CORE.md) | Vector store, ingestion, retrieval engine, adaptive router, reranker |
| 3 | [PHASE_03_AGENT_MEMORY.md](phases/PHASE_03_AGENT_MEMORY.md) | Agent factory, tool registry, conversation memory |
| 4 | [PHASE_04_SERVICE_LAYER.md](phases/PHASE_04_SERVICE_LAYER.md) | RAGService, self-check, corrective retrieval (CRAG) |
| 5 | [PHASE_05_UI_MCP.md](phases/PHASE_05_UI_MCP.md) | Streamlit app, FastAPI MCP layer |

---

## Definition of Done (Per Phase)

- All files listed in the phase doc created/updated.
- Acceptance criteria in the phase doc met.
- No business logic in UI (only in service/core/rag/memory).
- Config and secrets via env; no hardcoded keys.
- English used for code comments and docstrings; Arabic only in user-facing copy if required.

---

## Next Step

Open [PHASE_01_FOUNDATION.md](phases/PHASE_01_FOUNDATION.md) when ready to implement Phase 1.
