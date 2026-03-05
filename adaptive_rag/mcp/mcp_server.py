"""
MCP-ready HTTP API for the Adaptive Agentic RAG System.

Exposes RAG as POST /ask and POST /tool/search_knowledge so external agents
or orchestration (e.g. n8n) can call it as a tool. No Streamlit or UI deps.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    """Request body for /ask and /tool/search_knowledge."""

    query: str = Field(..., min_length=1, description="User question or search query.")


class AskResponse(BaseModel):
    """Response for /ask and /tool/search_knowledge."""

    answer: str = Field(..., description="Model answer or search result summary.")
    sources_count: int = Field(0, description="Number of retrieved source chunks.")
    used_corrective_retry: bool = Field(False, description="Whether CRAG corrective retrieval was used.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build and cache RAGService once at startup."""
    try:
        from adaptive_rag.services.app_factory import build_rag_service

        app.state.rag_service = build_rag_service(enable_self_check=False, default_top_k=5)
        logger.info("RAGService initialized.")
    except Exception as e:
        logger.exception("Failed to build RAGService: %s", e)
        app.state.rag_service = None
    yield
    app.state.rag_service = None


app = FastAPI(
    title="Adaptive Agentic RAG — MCP API",
    description="Ask questions against the knowledge base. MCP-ready for external agents.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def _get_rag_service(request: Request) -> Any:
    """Return app.state.rag_service or raise 503 if not available."""
    svc = getattr(request.app.state, "rag_service", None)
    if svc is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not available. Check OPENROUTER_API_KEY and server logs.",
        )
    return svc


@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: Request, req: AskRequest):
    """
    Answer a question using the RAG pipeline (retrieval + agent + memory).

    Returns the model answer and metadata. Memory is updated for multi-turn support.
    """
    svc = _get_rag_service(request)
    try:
        response = svc.ask(req.query)
        return AskResponse(
            answer=response.content,
            sources_count=len(response.sources),
            used_corrective_retry=response.used_corrective_retry,
        )
    except Exception as e:
        logger.exception("ask failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/search_knowledge", response_model=AskResponse)
async def tool_search_knowledge(request: Request, req: AskRequest):
    """
    MCP-style tool: run the same RAG ask pipeline and return the answer.

    External agents can call this as a single tool to query the knowledge base.
    """
    return await ask_endpoint(request, req)


@app.get("/health")
async def health():
    """Health check; does not require RAG to be loaded."""
    return {"status": "ok"}
