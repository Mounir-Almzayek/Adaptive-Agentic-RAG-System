"""
Agent factory for the Adaptive Agentic RAG System.

Builds a tool-calling agent (LLM + tools) that accepts query, conversation
context, and retrieved knowledge docs. Uses LangChain message types and
bind_tools for a clean, provider-agnostic loop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

if TYPE_CHECKING:
    pass

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant with access to tools and to retrieved knowledge.

When the user asks a question:
1. Use the "Retrieved knowledge" section below if it is provided; it contains relevant excerpts from the knowledge base.
2. You may call tools (e.g. calculator, search_knowledge) when they would help answer the question.
3. Answer clearly and concisely. If you use information from the retrieved knowledge, you can say so briefly.

Current conversation context is included so you can refer to earlier turns if needed."""

MAX_TOOL_ROUNDS = 10


def _format_knowledge(docs: list[Document] | None) -> str:
    if not docs:
        return ""
    parts = []
    for i, doc in enumerate(docs, 1):
        content = (doc.page_content or "").strip()
        if content:
            parts.append(f"[{i}] {content}")
    if not parts:
        return ""
    return "Retrieved knowledge:\n" + "\n\n".join(parts)


def _messages_from_context_and_query(
    context_tuples: list[tuple[str, str]],
    query: str,
    knowledge_docs: list[Document] | None,
    system_prompt: str,
) -> list[BaseMessage]:
    """Build message list: system (with knowledge) + context + current user message."""
    knowledge_block = _format_knowledge(knowledge_docs)
    system_content = system_prompt
    if knowledge_block:
        system_content = system_prompt.rstrip() + "\n\n" + knowledge_block
    messages: list[BaseMessage] = [SystemMessage(content=system_content)]

    for role, content in context_tuples:
        if role == "user" and content:
            messages.append(HumanMessage(content=content))
        elif role == "assistant" and content:
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=query))
    return messages


def _run_tool_loop(
    llm: BaseChatModel,
    tools: list[BaseTool],
    messages: list[BaseMessage],
) -> AIMessage:
    """Invoke LLM with tools until no more tool calls or max rounds."""
    tool_map = {t.name: t for t in tools}
    current = list(messages)
    for _ in range(MAX_TOOL_ROUNDS):
        response = llm.invoke(current)
        if not isinstance(response, AIMessage):
            break
        if not getattr(response, "tool_calls", None):
            return response
        current.append(response)
        for tc in response.tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {}) or {}
            tid = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", str(id(tc)))
            if name not in tool_map:
                current.append(ToolMessage(content=f"Unknown tool: {name}", tool_call_id=tid))
                continue
            try:
                result = tool_map[name].invoke(args)
                content = result if isinstance(result, str) else str(result)
            except Exception as e:
                content = f"Error: {e}"
            current.append(ToolMessage(content=content, tool_call_id=tid))
    return current[-1] if current and isinstance(current[-1], AIMessage) else AIMessage(content="")


def create_agent(
    llm: BaseChatModel,
    tools: list[BaseTool],
    system_prompt: str | None = None,
):
    """
    Create a runnable agent that accepts query, context, and knowledge_docs.

    The agent uses the LLM with bind_tools(tools) and runs a tool-calling loop.
    Returns an object with .invoke(query, context=..., knowledge_docs=...) that
    returns the final assistant message content (str).
    """

    prompt = (system_prompt or DEFAULT_SYSTEM_PROMPT).strip()
    bound_llm = llm.bind_tools(tools)

    class AgentRunnable:
        def invoke(
            self,
            query: str,
            context: list[tuple[str, str]] | None = None,
            knowledge_docs: list[Document] | None = None,
        ) -> str:
            ctx = context or []
            msgs = _messages_from_context_and_query(
                context_tuples=ctx,
                query=(query or "").strip(),
                knowledge_docs=knowledge_docs,
                system_prompt=prompt,
            )
            # Use bound LLM for the tool loop (same tools)
            response = _run_tool_loop(bound_llm, tools, msgs)
            return (response.content or "").strip()

    return AgentRunnable()
