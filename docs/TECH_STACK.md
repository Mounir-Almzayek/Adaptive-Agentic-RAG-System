# Tech Stack — Adaptive Agentic RAG System

## Core Principles

- **Model-agnostic:** OpenRouter as primary gateway; LangChain for LLM and agent abstractions.
- **LangChain-first:** Chains, agents, vectorstores, and tools use LangChain interfaces for consistency and testability.
- **Production-oriented:** Typing, env-based config, structured logging, and clear dependency boundaries.

---

## Required Stack

### 1. LLM & Agent

| Component | Choice | Role |
|-----------|--------|------|
| API gateway | **OpenRouter** | Single API for multiple models (OpenAI, Google, Anthropic, etc.) |
| Framework | **LangChain** | LCEL, agents, tools, prompt management |
| LangChain OpenRouter | `langchain-openai`-style client or **OpenRouter**-compatible endpoint | Use OpenAI-compatible client with OpenRouter base URL |

**Notes:**

- OpenRouter base URL: `https://openrouter.ai/api/v1`; use OpenAI client with `base_url` and `api_key`.
- Model IDs are OpenRouter model names (e.g. `google/gemini-2.0-flash`, `openai/gpt-4o-mini`).

### 2. RAG & Embeddings

| Component | Choice | Role |
|-----------|--------|------|
| Embeddings | **LangChain embedding model** (e.g. OpenAI, or OpenRouter-compatible embedding) | Chunk embedding for vector store |
| Vector store | **Chroma** or **FAISS** (LangChain integration) | Vector search; Chroma supports persistence and optional hybrid |
| Document loaders | **LangChain document loaders** | PDF, text, etc. |
| Text splitters | **LangChain text splitters** | RecursiveCharacterTextSplitter or similar |

**Optional:**

- Reranker: **cross-encoder** (e.g. sentence-transformers) or LangChain reranker abstraction if available.

### 3. Application & API

| Component | Choice | Role |
|-----------|--------|------|
| UI | **Streamlit** | Chat interface, file upload, settings |
| MCP / API | **FastAPI** | Expose RAG as HTTP tools for external agents |
| Config | **pydantic-settings** or **python-dotenv** | Env-based settings and validation |

### 4. Language & Tooling

| Component | Choice |
|-----------|--------|
| Language | Python 3.11+ |
| Package management | `uv` or `pip` + `requirements.txt` / `pyproject.toml` |
| Env | `.env` for local; keys in env in production |

---

## Dependency Groups (Suggested)

- **core:** langchain-core, langchain-openai (OpenRouter via base_url), langchain-community (vectorstores, loaders), pydantic, pydantic-settings.
- **rag:** chromadb or faiss-cpu, sentence-transformers (optional reranker).
- **app:** streamlit.
- **mcp:** fastapi, uvicorn.

---

## Environment Variables (Reference)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes (default path) | OpenRouter API key |
| `DEFAULT_PROVIDER` | No | e.g. `openrouter` |
| `DEFAULT_MODEL` | No | e.g. `google/gemini-2.0-flash-exp` |
| `RETRIEVAL_STRATEGY` | No | `vector` \| `hybrid` \| `adaptive` |
| `EMBEDDING_MODEL` | No | Model for embeddings (if different from LLM) |
| `VECTOR_STORE_PATH` | No | Persistence path for Chroma/FAISS |

---

## Out of Scope for Initial Phases

- Database for conversation persistence (can add later with same memory interface).
- Celery/Redis for async (optional later).
- Docker/K8s (document in deployment doc when needed).

---

## Next Step

See [PHASES.md](PHASES.md) for the implementation roadmap and [CONVENTIONS.md](CONVENTIONS.md) for code and repo conventions.
