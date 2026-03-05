# Project Overview — Adaptive Agentic RAG System

## Vision

Build **AI Knowledge Infrastructure**: a production-ready, model-agnostic RAG system that is modular, multi-provider, MCP-ready, and designed for portfolio demonstration or future SaaS.

---

## Goals

| Before (Demo) | After (Production-Ready) |
|---------------|--------------------------|
| Single-model (e.g. Gemini only) | **Model-agnostic** (OpenRouter, multiple backends) |
| Vector-only retrieval | **Adaptive / hybrid** retrieval with fallbacks |
| Stateless Q&A | **Memory layer** for multi-turn conversations |
| Single tool / hardcoded logic | **Tool registry** + MCP-ready tool exposure |
| Monolithic UI + agent | **Clean architecture**: UI ↔ Service ↔ Core/RAG |
| Not extensible | **MCP-ready**, scalable, SaaS-path |

---

## Scope (In Scope for This Plan)

- **Model layer:** OpenRouter + LangChain; support multiple providers via single interface.
- **RAG:** Vector store (e.g. LangChain vectorstore), hybrid/adaptive retrieval, optional reranker.
- **Agent:** LangChain-based agent with tool registry; pluggable tools (search, calculator, MCP wrappers).
- **Memory:** Conversation memory (bounded history) for context in agent/RAG.
- **Service layer:** Single entry point (e.g. `RAGService`) coordinating retrieval, memory, and agent.
- **Optional self-reflection:** Post-answer validation and corrective retrieval (CRAG-style).
- **UI:** Streamlit as view layer only; no business logic in UI.
- **MCP:** API/tool layer so external agents can call the system (e.g. search_knowledge).

---

## Out of Scope (For Initial Phases)

- Full SaaS (auth, tenants, billing) — documented as future direction.
- Multi-agent (Researcher / Critic / Synthesizer) — future phase.
- n8n orchestration — future integration.
- Distributed / multi-node deployment — architecture should allow it later.

---

## Success Criteria

1. **Model-agnostic:** Swap provider/model via config without code changes.
2. **Adaptive retrieval:** Strategy (vector / hybrid / adaptive) selectable or automatic.
3. **Stateful:** Multi-turn conversations use stored context.
4. **Extensible tools:** New tools (including MCP) added via registry.
5. **Clean separation:** UI → Service → Core/RAG/Memory; testable in isolation.
6. **MCP-ready:** At least one endpoint/tool (e.g. search_knowledge) callable by external agents.
7. **Documented:** Architecture and phased plan in English; implementation follows plan.

---

## Stakeholders and Use Cases

- **Portfolio:** Demonstrates production-grade RAG + agent design.
- **Future SaaS:** Same core can power API + tenant-specific memory/knowledge.
- **Research / experimentation:** Easy to add new retrieval strategies or agents.

---

## Next Step

Proceed to [ARCHITECTURE.md](ARCHITECTURE.md) for system design, then [PHASES.md](PHASES.md) for the implementation roadmap.
