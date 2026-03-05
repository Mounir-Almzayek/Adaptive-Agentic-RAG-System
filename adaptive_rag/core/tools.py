"""
Built-in tools for the Adaptive Agentic RAG System agent.

All tools are LangChain-compatible (BaseTool / @tool) so they work with
bind_tools and tool-calling loops. search_knowledge is a stub in Phase 3;
Phase 4 wires it to real retrieval.
"""

from __future__ import annotations

import ast
import operator
import re
from typing import Annotated

from langchain_core.tools import tool

# Safe binary ops for calculator (no __import__, no open, etc.)
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    raise ValueError("Unsupported expression")


@tool
def calculator(
    expression: Annotated[str, "A single mathematical expression, e.g. '2 + 3 * 4' or '10 / 2'"],
) -> str:
    """
    Evaluate a safe mathematical expression. Supports +, -, *, /, //, ** and parentheses.
    Use for arithmetic only; input must be a single expression.
    """
    expression = (expression or "").strip()
    if not expression:
        return "Error: empty expression"
    # Restrict to a single expression (no newlines, no semicolons)
    if re.search(r"[\n;]", expression):
        return "Error: only one expression allowed"
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except (ValueError, TypeError, ZeroDivisionError, SyntaxError) as e:
        return f"Error: {e}"


# Stub: in Phase 4 this is replaced or wrapped to call retrieval_engine.retrieve / RAGService
@tool
def search_knowledge(
    query: Annotated[str, "Search query to find relevant documents in the knowledge base"],
) -> str:
    """
    Search the knowledge base for documents relevant to the query. Use this when you need
    information from uploaded or indexed documents. Returns relevant text excerpts.
    """
    # Phase 3 stub: real retrieval is wired in Phase 4 (RAGService / retrieval_engine)
    return (
        "[Knowledge search is not yet wired; retrieved context is provided in the conversation. "
        "Answer using the 'Retrieved knowledge' section above when available.]"
    )


def get_builtin_tools() -> list:
    """Return the list of built-in tools (calculator, search_knowledge) for the agent."""
    return [calculator, search_knowledge]
