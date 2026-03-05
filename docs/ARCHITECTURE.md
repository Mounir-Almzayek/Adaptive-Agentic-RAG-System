# Architecture — Adaptive Agentic RAG System

## High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Streamlit App (app/streamlit_app.py)                                │ │
│  │  - Chat UI, file upload, settings (provider/model)                   │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  RAGService (services/rag_service.py)                                │ │
│  │  - ask(query) → retrieval → context → agent → memory update          │ │
│  │  - Optional: self-check / corrective loop (CRAG)                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐
│  CORE            │  │  RAG            │  │  MEMORY                    │
│  - ModelFactory  │  │  - RetrievalEng │  │  - ConversationMemory      │
│  - AgentFactory  │  │  - Reranker     │  │  - get_context / add       │
│  - ToolRegistry  │  │  - AdaptiveRtr  │  └─────────────────────────────┘
└────────┬────────┘  └────────┬────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────────────────────────────────┐
│  LLM (OpenRouter│  │  KNOWLEDGE                                        │
│  / LangChain)   │  │  - VectorStore (knowledge/vector_store.py)        │
│  - Chat models  │  │  - IngestionService (knowledge/ingestion_service)  │
└─────────────────┘  └─────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  MCP LAYER (mcp/mcp_server.py)                                            │
│  - Exposes RAG as tools (e.g. POST /tool/search_knowledge) for external  │
│    agents / orchestration                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### 1. Presentation (app/)

- **streamlit_app.py:** View only. Renders chat, file upload, provider/model selection. Calls `RAGService.ask()` and displays responses. No retrieval or agent logic.

### 2. Service Layer (services/)

- **rag_service.py:** Single entry point for “ask a question.”
  - Calls retrieval engine with query (and strategy).
  - Gets conversation context from memory.
  - Invokes agent with query + context + retrieved docs.
  - Updates memory with user/assistant turn.
  - Optional: run self-check on answer; on failure, adjust retrieval (e.g. top_k) and re-run (CRAG).

### 3. Core (core/)

- **model_factory.py:** Builds LangChain-compatible LLM from config (provider, model id, API key). OpenRouter as default gateway for multi-provider.
- **agent_factory.py:** Builds agent (e.g. LangChain agent) with LLM from model_factory and tools from tool_registry.
- **tool_registry.py:** Registers and exposes tools (search_knowledge, calculator, web search, MCP wrappers). Used by agent_factory.

### 4. RAG (rag/)

- **retrieval_engine.py:** Implements `retrieve(query, strategy)`. Strategies: `vector`, `hybrid`, `adaptive`. Delegates to vector store and optional reranker.
- **reranker.py:** Optional cross-encoder or model-based reranking of retrieved chunks.
- **adaptive_router.py:** Decides strategy (e.g. simple heuristic: if vector result count &lt; threshold → hybrid).

### 5. Memory (memory/)

- **conversation_memory.py:** In-memory (or later persistent) store of recent turns. `add(user, assistant)`, `get_context()` (e.g. last N turns). Used by RAGService.

### 6. Knowledge (knowledge/)

- **vector_store.py:** LangChain vectorstore (e.g. Chroma/FAISS) — `vector_search`, `hybrid_search` (if supported), add_documents.
- **ingestion_service.py:** Loads documents (PDF, text, etc.), chunks, and indexes into vector_store.

### 7. Config (config/)

- **settings.py:** Loads env (e.g. OPENROUTER_API_KEY, default provider/model, retrieval strategy). Single source of configuration.

### 8. MCP (mcp/)

- **mcp_server.py:** FastAPI (or similar) app exposing RAG as tools (e.g. `search_knowledge(query)`). Calls RAGService internally. Enables external agents to use the system as a tool.

---

## Data Flow (Single Query)

1. User submits query in Streamlit.
2. Streamlit calls `RAGService.ask(query)`.
3. RAGService:
   - `docs = retrieval_engine.retrieve(query, strategy)`
   - `context = memory.get_context()`
   - `response = agent.run(query, context=context, knowledge_docs=docs)`
   - `memory.add(query, response.content)`
4. Optional: validate response; if invalid, retry with different retrieval params.
5. Return response to UI (or to MCP caller).

---

## Technology Alignment

- **LLM / routing:** OpenRouter + LangChain (LCEL, agents). Model factory returns LangChain runnables.
- **Retrieval:** LangChain vectorstore abstractions; adaptive logic in retrieval_engine + optional reranker.
- **Agent:** LangChain agent (e.g. create_react_agent) with tools from tool_registry.
- **MCP:** FastAPI endpoints that map to RAGService; can later align with MCP protocol if needed.

---

## Security and Configuration

- All API keys and secrets from environment (or secret manager); never in code.
- Config validated at startup (e.g. required keys present for selected provider).

---

## Next Step

See [TECH_STACK.md](TECH_STACK.md) for concrete libraries and versions, then [PHASES.md](PHASES.md) for the phased implementation plan.
