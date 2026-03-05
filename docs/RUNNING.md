# Running the Adaptive Agentic RAG System

## Prerequisites

- Python 3.11+ (3.11–3.12 recommended; Chroma has known issues on 3.14)
- `.env` file with required variables (copy from `.env.example`)

## Environment

```bash
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY (required). Optionally set DEFAULT_MODEL, RETRIEVAL_STRATEGY, VECTOR_STORE_PATH.
pip install -r requirements.txt
```

### Key variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for the LLM |
| `DEFAULT_MODEL` | No | OpenRouter model id (default: google/gemini-2.0-flash-exp) |
| `RETRIEVAL_STRATEGY` | No | `adaptive`, `vector`, or `hybrid` |
| `VECTOR_STORE_PATH` | No | Directory for Chroma persistence (default: ./data/vector_store) |

## Streamlit UI

From the **project root** (so `adaptive_rag` is on the Python path):

```bash
streamlit run adaptive_rag/app/streamlit_app.py
```

Or with explicit module run:

```bash
python -m streamlit run adaptive_rag/app/streamlit_app.py
```

- **Chat:** Type a question and press Enter. The first message triggers RAG initialization (requires `OPENROUTER_API_KEY`).
- **Sidebar:** Choose retrieval strategy, enable/disable self-check (CRAG), upload PDF/TXT/MD files for ingestion, clear conversation memory.
- Config (model, etc.) is read from `.env`; no provider/model dropdown in UI for Phase 5 (can be added later).

## MCP API (FastAPI)

From the **project root**:

```bash
uvicorn adaptive_rag.mcp.mcp_server:app --reload --port 8000
```

- **Health:** `GET http://localhost:8000/health`
- **Ask:** `POST http://localhost:8000/ask` with body `{"query": "Your question"}`
- **Tool (MCP-style):** `POST http://localhost:8000/tool/search_knowledge` with body `{"query": "Your question"}`

Response shape: `{"answer": "...", "sources_count": N, "used_corrective_retry": false}`.

RAGService is built once at startup. If `OPENROUTER_API_KEY` is missing, the app starts but `/ask` and `/tool/search_knowledge` return 503 until the key is set and the server is restarted.

## Ingesting documents

- **From Streamlit:** Use the sidebar “Upload document” to add PDF, TXT, or MD files. They are chunked and indexed into the vector store used by RAG.
- **From API:** Phase 5 does not expose a public `/ingest` endpoint; add one in `mcp_server.py` if MCP clients should trigger ingestion.
