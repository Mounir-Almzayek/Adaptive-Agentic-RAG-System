"""
Unit tests for Phase 3: conversation memory, tool registry, and agent factory.

Agent test uses a mock LLM to avoid API calls; smoke test with real LLM is optional.
"""

import pytest


# --- ConversationMemory ---


@pytest.mark.unit
def test_conversation_memory_add_and_get_context():
    from adaptive_rag.memory.conversation_memory import ConversationMemory

    mem = ConversationMemory(max_turns=10)
    mem.add("Hello", "Hi there.")
    mem.add("What is 2+2?", "4.")
    ctx = mem.get_context(limit=5)
    assert len(ctx) == 2
    assert ctx[0]["user"] == "Hello" and ctx[0]["assistant"] == "Hi there."
    assert ctx[1]["user"] == "What is 2+2?" and ctx[1]["assistant"] == "4."


@pytest.mark.unit
def test_conversation_memory_get_context_limit():
    from adaptive_rag.memory.conversation_memory import ConversationMemory

    mem = ConversationMemory(max_turns=10)
    for i in range(5):
        mem.add(f"u{i}", f"a{i}")
    assert len(mem.get_context(limit=3)) == 3
    assert len(mem.get_context(limit=10)) == 5


@pytest.mark.unit
def test_conversation_memory_get_context_as_messages():
    from adaptive_rag.memory.conversation_memory import ConversationMemory

    mem = ConversationMemory()
    mem.add("Q", "A")
    msgs = mem.get_context_as_messages(limit=5)
    assert msgs == [("user", "Q"), ("assistant", "A")]


@pytest.mark.unit
def test_conversation_memory_clear():
    from adaptive_rag.memory.conversation_memory import ConversationMemory

    mem = ConversationMemory()
    mem.add("a", "b")
    mem.clear()
    assert len(mem) == 0
    assert mem.get_context(5) == []


# --- ToolRegistry ---


@pytest.mark.unit
def test_tool_registry_includes_builtin():
    from adaptive_rag.core.tool_registry import ToolRegistry

    reg = ToolRegistry(include_builtin=True)
    tools = reg.get_tools()
    names = [t.name for t in tools]
    assert "calculator" in names
    assert "search_knowledge" in names


@pytest.mark.unit
def test_tool_registry_register_and_get():
    from langchain_core.tools import tool

    from adaptive_rag.core.tool_registry import ToolRegistry

    @tool
    def extra_tool(x: str) -> str:
        """Extra."""
        return x

    reg = ToolRegistry(include_builtin=False)
    reg.register(extra_tool)
    tools = reg.get_tools()
    assert len(tools) == 1
    assert tools[0].name == "extra_tool"


@pytest.mark.unit
def test_tool_registry_register_from_mcp():
    from adaptive_rag.core.tool_registry import ToolRegistry

    reg = ToolRegistry(include_builtin=False)

    def handler(q: str) -> str:
        return f"Result: {q}"

    reg.register_from_mcp("mcp_search", "Search via MCP", handler)
    tools = reg.get_tools()
    assert len(tools) == 1
    assert tools[0].name == "mcp_search"
    assert "Result: hello" in tools[0].invoke({"q": "hello"})


# --- Calculator tool ---


@pytest.mark.unit
def test_calculator_tool():
    from adaptive_rag.core.tools import calculator

    assert calculator.invoke({"expression": "2 + 3"}) in ("5", "5.0")
    assert calculator.invoke({"expression": "10 / 2"}) == "5.0"
    assert "Error" in calculator.invoke({"expression": "1/0"})


# --- Agent (mock LLM) ---


@pytest.mark.unit
def test_create_agent_invoke_with_mock_llm():
    from langchain_core.messages import AIMessage

    from adaptive_rag.core.agent_factory import create_agent
    from adaptive_rag.core.tool_registry import ToolRegistry

    class MockLLM:
        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            return AIMessage(content="Mocked answer.")

    reg = ToolRegistry(include_builtin=True)
    llm = MockLLM()
    agent = create_agent(llm, reg.get_tools())
    out = agent.invoke("Hello", context=[], knowledge_docs=None)
    assert out == "Mocked answer."


@pytest.mark.unit
def test_agent_inject_knowledge_docs():
    from langchain_core.documents import Document

    from adaptive_rag.core.agent_factory import _format_knowledge, _messages_from_context_and_query

    docs = [
        Document(page_content="First chunk.", metadata={}),
        Document(page_content="Second chunk.", metadata={}),
    ]
    block = _format_knowledge(docs)
    assert "Retrieved knowledge" in block
    assert "First chunk" in block and "Second chunk" in block

    msgs = _messages_from_context_and_query(
        context_tuples=[],
        query="Q",
        knowledge_docs=docs,
        system_prompt="You are helpful.",
    )
    assert len(msgs) >= 2
    assert msgs[0].content and "First chunk" in msgs[0].content
