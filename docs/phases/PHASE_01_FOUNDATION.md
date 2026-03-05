# Phase 1 — Foundation

**Goal:** Establish project structure, configuration, and a model-agnostic LLM factory using OpenRouter and LangChain. No UI or RAG yet.

---

## Objectives

1. Create the full directory layout for the Adaptive Agentic RAG System.
2. Implement env-based configuration with validation (e.g. pydantic-settings).
3. Implement `model_factory` that returns a LangChain LLM for OpenRouter (and optionally other providers via OpenRouter).
4. Provide a minimal script or test that instantiates the LLM and runs one completion (smoke test).
5. Document required env vars in `.env.example`.

---

## Directory Layout to Create

```
adaptive_rag/
├── __init__.py
├── app/
│   └── __init__.py
├── core/
│   └── __init__.py
├── rag/
│   └── __init__.py
├── memory/
│   └── __init__.py
├── knowledge/
│   └── __init__.py
├── services/
│   └── __init__.py
├── config/
│   └── __init__.py
├── mcp/
│   └── __init__.py
└── docs/          (already present at repo root docs/)
```

Root of repo also contains: `README.md`, `requirements.txt` or `pyproject.toml`, `.env.example`, and optionally `tests/`.

---

## File-by-File Tasks

### 1. `config/settings.py`

- Use pydantic-settings (or dotenv + pydantic) to load from environment.
- Fields (examples):
  - `openrouter_api_key: str`
  - `default_model: str = "google/gemini-2.0-flash-exp"` (or similar OpenRouter model id)
  - `default_embedding_model: str | None` (optional, for later RAG)
  - `retrieval_strategy: str = "adaptive"`
  - `vector_store_path: str = "./data/vector_store"`
- Validate that `openrouter_api_key` is non-empty when OpenRouter is used.
- Export a single `get_settings()` or `settings` singleton used across the app.

### 2. `core/model_factory.py`

- Function: `create_llm(provider: str | None = None, model_id: str | None = None, api_key: str | None = None) -> Runnable` (LangChain runnable, e.g. ChatOpenAI-compatible).
- Use OpenRouter as the default provider: OpenAI-compatible client with:
  - `base_url="https://openrouter.ai/api/v1"`
  - `api_key` from config or argument.
  - `model` = OpenRouter model id (e.g. `google/gemini-2.0-flash-exp`).
- Read default provider and model from `config/settings`.
- Return a LangChain chat model instance (e.g. `ChatOpenAI` with base_url and model).
- Raise a clear error if API key is missing or provider is unsupported.

### 3. `.env.example`

- List all required and optional env vars with short descriptions:
  - `OPENROUTER_API_KEY=`
  - `DEFAULT_MODEL=google/gemini-2.0-flash-exp`
  - `RETRIEVAL_STRATEGY=adaptive`
  - `VECTOR_STORE_PATH=./data/vector_store`
- No real keys; only placeholders and comments.

### 4. `requirements.txt` or `pyproject.toml`

- Include: `langchain`, `langchain-openai` (for OpenRouter via OpenAI client), `langchain-core`, `pydantic`, `pydantic-settings`, `python-dotenv`.
- Pin versions for reproducibility (or use ranges and document in TECH_STACK).

### 5. Smoke Test (optional but recommended)

- Script or test: load settings, call `create_llm()`, invoke `llm.invoke("Say hello in one word.")` and assert response is non-empty.
- Can live in `tests/test_model_factory.py` or `scripts/smoke_llm.py`.

---

## Acceptance Criteria

- [ ] All directories and `__init__.py` files exist.
- [ ] `config/settings.py` loads from env and validates required keys.
- [ ] `core/model_factory.py` returns a LangChain chat model that works with OpenRouter.
- [ ] Smoke test passes when `OPENROUTER_API_KEY` is set.
- [ ] `.env.example` is present and documented.
- [ ] No API keys in code; all from env.

---

## Out of Scope in This Phase

- Agent, tools, RAG, memory, UI, MCP. These are in later phases.

---

## Next Phase

After Phase 1 is complete, proceed to [PHASE_02_RAG_CORE.md](PHASE_02_RAG_CORE.md) and/or [PHASE_03_AGENT_MEMORY.md](PHASE_03_AGENT_MEMORY.md).
