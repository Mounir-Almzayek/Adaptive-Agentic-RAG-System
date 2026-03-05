# Adaptive Agentic RAG System

**Modular • Multi-Provider • MCP-Ready • Production Architecture**

A production-ready, model-agnostic RAG (Retrieval-Augmented Generation) system with adaptive retrieval, conversation memory, tool orchestration, and MCP compatibility. Built for scalability and portfolio/SaaS readiness.

---

## Documentation (Planning Phase)

| Document | Purpose |
|----------|---------|
| [PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | Vision, goals, scope, success criteria |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, data flow |
| [TECH_STACK.md](docs/TECH_STACK.md) | OpenRouter, LangChain, and dependencies |
| [PHASES.md](docs/PHASES.md) | Master implementation roadmap |
| [PHASE_01_FOUNDATION.md](docs/phases/PHASE_01_FOUNDATION.md) | Config, structure, model factory |
| [PHASE_02_RAG_CORE.md](docs/phases/PHASE_02_RAG_CORE.md) | Retrieval engine, vector store, ingestion |
| [PHASE_03_AGENT_MEMORY.md](docs/phases/PHASE_03_AGENT_MEMORY.md) | Agent factory, memory, tool registry |
| [PHASE_04_SERVICE_LAYER.md](docs/phases/PHASE_04_SERVICE_LAYER.md) | RAG service, self-reflection, CRAG |
| [PHASE_05_UI_MCP.md](docs/phases/PHASE_05_UI_MCP.md) | Streamlit app, MCP layer |
| [CONVENTIONS.md](docs/CONVENTIONS.md) | Code style, naming, patterns |
| [GLOSSARY.md](docs/GLOSSARY.md) | Terms and abbreviations |

---

## Target Structure (Post-Implementation)

```
adaptive_rag/
├── app/                 # Streamlit UI
├── core/                # Agent, model, tool factories
├── rag/                 # Retrieval, reranker, adaptive router
├── memory/              # Conversation memory
├── knowledge/           # Vector store, ingestion
├── services/            # RAG service, orchestration
├── config/              # Settings, env
├── mcp/                 # MCP server / tool exposure
└── docs/                # Planning and reference
```

---

## Status

**Current phase:** Planning and documentation. No implementation yet.

Next step: Review docs, then start **Phase 1 – Foundation**.
