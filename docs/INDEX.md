# Documentation Index — Adaptive Agentic RAG System

Use this index to navigate planning and implementation. **No implementation has started yet;** this is the planning and documentation phase.

---

## Start Here

1. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** — Vision, goals, scope, success criteria.
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design, components, data flow.
3. **[TECH_STACK.md](TECH_STACK.md)** — OpenRouter, LangChain, and dependencies.
4. **[PHASES.md](PHASES.md)** — Master implementation roadmap and phase order.

---

## Phased Implementation (Detailed)

| # | Document | When to use |
|---|----------|-------------|
| 1 | [phases/PHASE_01_FOUNDATION.md](phases/PHASE_01_FOUNDATION.md) | First: config, package layout, model factory |
| 2 | [phases/PHASE_02_RAG_CORE.md](phases/PHASE_02_RAG_CORE.md) | After Phase 1: vector store, ingestion, retrieval |
| 3 | [phases/PHASE_03_AGENT_MEMORY.md](phases/PHASE_03_AGENT_MEMORY.md) | After Phase 1: agent, tools, memory |
| 4 | [phases/PHASE_04_SERVICE_LAYER.md](phases/PHASE_04_SERVICE_LAYER.md) | After 2 & 3: RAGService, self-check, CRAG |
| 5 | [phases/PHASE_05_UI_MCP.md](phases/PHASE_05_UI_MCP.md) | After Phase 4: Streamlit, FastAPI MCP |

---

## Reference

- **[CONVENTIONS.md](CONVENTIONS.md)** — Code style, naming, layout.
- **[GLOSSARY.md](GLOSSARY.md)** — Terms and abbreviations.
- **[RUNNING.md](RUNNING.md)** — How to run the app and MCP server (after Phase 5).

---

## Repo Root

- **README.md** — Project summary and doc links.
- **.env.example** — Required environment variables.
- **requirements.txt** — Python dependencies.
- **.gitignore** — Ignore rules.

---

**Next step:** Read PROJECT_OVERVIEW and ARCHITECTURE, then start implementation with Phase 1 using [phases/PHASE_01_FOUNDATION.md](phases/PHASE_01_FOUNDATION.md).
