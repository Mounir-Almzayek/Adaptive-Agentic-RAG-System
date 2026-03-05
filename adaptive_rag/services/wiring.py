"""
Wiring: build a search_knowledge tool backed by the retrieval engine.

Used when constructing the agent for RAGService so that when the agent
calls search_knowledge, it gets real retrieved docs instead of the stub.
"""

from __future__ import annotations

from typing import Annotated, Protocol

from langchain_core.tools import StructuredTool


class RetrievalProtocol(Protocol):
    def retrieve(self, query: str, strategy: str, top_k: int) -> list:
        ...


def make_search_knowledge_tool(
    retrieval_engine: RetrievalProtocol,
    top_k: int = 5,
    strategy: str = "adaptive",
) -> StructuredTool:
    """
    Return a LangChain tool that searches the knowledge base via the retrieval engine.

    Register this tool (instead of or in addition to the stub) when building the
    agent for RAGService so the agent can pull additional context on demand.
    """
    def search(query: Annotated[str, "Search query to find relevant documents"]) -> str:
        docs = retrieval_engine.retrieve(query, strategy=strategy, top_k=top_k)
        if not docs:
            return "No relevant documents found."
        parts = []
        for i, doc in enumerate(docs, 1):
            content = (getattr(doc, "page_content", None) or str(doc)).strip()
            if content:
                parts.append(f"[{i}] {content}")
        return "\n\n".join(parts) if parts else "No relevant documents found."

    return StructuredTool.from_function(
        func=search,
        name="search_knowledge",
        description=(
            "Search the knowledge base for documents relevant to the query. "
            "Use this when you need more information from uploaded or indexed documents. "
            "Returns relevant text excerpts."
        ),
    )
