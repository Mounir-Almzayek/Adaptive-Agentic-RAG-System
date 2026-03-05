"""
Tool registry for the Adaptive Agentic RAG System.

Central place to register and retrieve tools for the agent. Supports
LangChain BaseTool instances and optional MCP-style tools (Phase 5).
"""

from __future__ import annotations

from typing import Callable

from langchain_core.tools import BaseTool

from adaptive_rag.core.tools import get_builtin_tools


class ToolRegistry:
    """
    Registry of tools available to the agent.

    Register LangChain tools (BaseTool or @tool) and optionally MCP-wrapped
    handlers. get_tools() returns a list suitable for llm.bind_tools(...).
    """

    def __init__(self, include_builtin: bool = True) -> None:
        self._tools: list[BaseTool] = []
        if include_builtin:
            self._tools.extend(get_builtin_tools())

    def register(self, tool: BaseTool | Callable) -> None:
        """
        Add a tool for the agent. Accepts a LangChain BaseTool or a callable
        that will be wrapped (e.g. with @tool or StructuredTool.from_function).
        """
        if isinstance(tool, BaseTool):
            self._tools.append(tool)
            return
        # Callable: assume it's already a @tool-decorated function (has .name, .invoke, etc.)
        if hasattr(tool, "name") and callable(tool):
            self._tools.append(tool)  # type: ignore[arg-type]
            return
        raise TypeError("Tool must be a LangChain BaseTool or a @tool-decorated callable")

    def get_tools(self) -> list[BaseTool]:
        """Return all registered tools in order (builtin first, then registered)."""
        return list(self._tools)

    def register_from_mcp(self, name: str, description: str, handler: Callable[..., str]) -> None:
        """
        Register an MCP-style tool by name, description, and handler.

        Wraps the handler as a LangChain StructuredTool so the agent can call it.
        Use in Phase 5 when exposing RAG or other services to external agents.
        """
        from langchain_core.tools import StructuredTool

        wrapped = StructuredTool.from_function(
            func=handler,
            name=name,
            description=description,
        )
        self._tools.append(wrapped)
