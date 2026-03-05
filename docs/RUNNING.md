# Running the Adaptive Agentic RAG System

*(To be used after Phase 5 implementation.)*

## Prerequisites

- Python 3.11+
- `.env` file with required variables (copy from `.env.example`).

## Environment

```bash
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY and any other variables.
pip install -r requirements.txt
```

## Streamlit UI

From the project root:

```bash
streamlit run adaptive_rag/app/streamlit_app.py
```

Or, if the app is runnable from the package:

```bash
python -m streamlit run adaptive_rag/app/streamlit_app.py
```

## MCP API (FastAPI)

From the project root:

```bash
uvicorn adaptive_rag.mcp.mcp_server:app --reload --port 8000
```

- Ask endpoint (example): `POST http://localhost:8000/tool/search_knowledge` with body `{"query": "Your question"}`.

## Optional: Ingest Documents

Use the Streamlit sidebar “Upload document” to ingest files into the vector store before asking questions.
