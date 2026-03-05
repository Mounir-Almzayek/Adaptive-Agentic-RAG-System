# Phase 4 — Service Layer

**Goal:** Implement the RAG service as the single entry point that coordinates retrieval, memory, and agent. Add optional self-check and corrective retrieval (CRAG-style) for production quality.

---

## Objectives

1. Implement `RAGService` that: given a query, retrieves docs, gets conversation context, runs the agent with query + context + docs, and updates memory.
2. Optionally implement a post-answer validator (e.g. check for presence of “source” or citation in answer, or simple quality heuristic).
3. If validation fails, implement corrective flow: e.g. re-retrieve with higher top_k or hybrid strategy, then re-run the agent once.
4. Keep the service independent of Streamlit so that both UI and MCP can call it.

---

## Dependencies

- Phase 1 (config, model_factory), Phase 2 (retrieval_engine, vector store), Phase 3 (agent_factory, tool_registry, conversation_memory).

---

## File-by-File Tasks

### 1. `services/rag_service.py`

- Class `RAGService`:
  - Constructor: `__init__(self, agent, retrieval_engine, memory, *, enable_self_check: bool = False)`.
  - Method: `ask(query: str, strategy: str | None = None) -> Response` (or similar return type):
    1. Get retrieval strategy from param or config.
    2. `docs = self.retrieval_engine.retrieve(query, strategy=strategy)`.
    3. `context = self.memory.get_context()`.
    4. Invoke agent with query, context, and docs (formatted as “Retrieved knowledge: …” in prompt or via message).
    5. `response = agent.invoke(...)`.
    6. If `enable_self_check`: run `self_check(response, docs)`; if False, optionally retry with `top_k` increased and/or strategy `hybrid`, then re-invoke agent (max one retry to avoid loops).
    7. `self.memory.add(query, response.content)` (or equivalent).
    8. Return response.
  - Use dependency injection: agent, retrieval_engine, and memory are passed in so the service is testable and UI-agnostic.

### 2. Self-Check (optional module or inside RAGService)

- Function: `self_check(answer: str, docs: list) -> bool`.
  - Simple checks: e.g. answer is non-empty; optionally “answer mentions at least one source” or “answer length above threshold.”
  - Return True if acceptable, False if corrective step should run.
- Document that this is a placeholder for more advanced validation (e.g. NLI, citation verification) in future.

### 3. Corrective Retrieval (CRAG-style)

- When `self_check` fails:
  - Retry retrieval with `top_k` increased (e.g. double) or switch to `hybrid` if current strategy was `vector`.
  - Re-run agent with new docs; update memory with the new response.
  - Optionally cap at one retry to avoid infinite loops.
- Log or metric: “self_check_failed_retry” for observability (can be console log in Phase 4).

### 4. Wiring “Search Knowledge” Tool (if not done in Phase 3)

- Ensure the tool used by the agent for “search knowledge” is backed by the same retrieval_engine (or RAGService) so that when the agent calls the tool, it gets real retrieved docs. This may require passing a callback or the retrieval_engine into the tool at construction time (in the place where RAGService is built, e.g. in app or a factory). Document where this wiring happens (e.g. in `app/streamlit_app.py` or a small `services/app_factory.py`).

---

## Acceptance Criteria

- [ ] RAGService.ask(query) returns a response using retrieval + memory + agent.
- [ ] Memory is updated after each successful ask.
- [ ] Optional self_check and one corrective retry implemented and toggleable via `enable_self_check`.
- [ ] No Streamlit or FastAPI imports in RAGService; only core/rag/memory dependencies.
- [ ] Agent’s “search knowledge” tool (if any) uses real retrieval when wired from the app.

---

## Out of Scope

- Streamlit UI and MCP HTTP API (Phase 5).
- Advanced validation (NLI, citation extraction) — leave as future improvement in docs.

---

## Next Phase

Proceed to [PHASE_05_UI_MCP.md](PHASE_05_UI_MCP.md) to add Streamlit and MCP layer.
