# Phase 3 — Agent & Memory

**Goal:** Implement conversation memory, a tool registry, and an agent factory that produces a LangChain agent (e.g. ReAct) using the model factory and registered tools. MCP-ready design (tools can be added from external sources later).

---

## Objectives

1. Implement a conversation memory that stores recent user/assistant turns and provides context for the agent.
2. Implement a tool registry that registers and exposes tools (e.g. search_knowledge stub, calculator); design so MCP tools can be wrapped and registered later.
3. Implement an agent factory that builds a LangChain agent with the LLM from model_factory and tools from the registry.
4. Ensure the agent can receive “knowledge docs” (retrieved chunks) as context in the prompt, and use tools when needed.

---

## Dependencies

- Phase 1 complete (model_factory, config).

---

## File-by-File Tasks

### 1. `memory/conversation_memory.py`

- Class `ConversationMemory`:
  - `add(user_message: str, assistant_message: str)` — append one turn.
  - `get_context(limit: int = 5)` — return last `limit` turns (e.g. list of dicts or formatted string for prompt).
  - Optional: `clear()` for new session.
- Storage: in-memory list is sufficient for Phase 3; interface should allow swapping to persistent store later (e.g. same methods, different backend).
- Thread-safe or session-scoped if multiple users in future (document intended use: single session per RAGService instance for now).

### 2. `core/tool_registry.py`

- Class `ToolRegistry`:
  - `register(tool: BaseTool | Callable)` — add a tool (LangChain tool or wrapped callable).
  - `get_tools() -> list` — return all registered tools for the agent.
  - Optional: `register_from_mcp(name, description, handler)` to wrap an MCP-style tool later.
- Pre-register at least one tool so the agent has something to use (e.g. a “search_knowledge” stub that returns a fixed message, or a simple calculator). Real search_knowledge that calls retrieval will be wired in Phase 4 via RAGService.

### 3. `core/agent_factory.py`

- Function or class: `create_agent(llm, tools: list, system_prompt: str | None = None)`.
  - Build a LangChain ReAct (or equivalent) agent with the given LLM and tools.
  - Optionally accept a default system prompt that instructs the agent to use provided context (knowledge_docs) and tools.
- Return an runnable agent that can be invoked with:
  - `query` (user message),
  - `context` (conversation history from memory),
  - `knowledge_docs` (retrieved chunks from RAG).
- Prompt structure: combine system prompt + conversation context + “Retrieved knowledge: …” + current query. Use LangChain message types (SystemMessage, HumanMessage, etc.) or a single prompt template.

### 4. Tool Examples for Registry

- **Calculator (optional):** Simple LangChain tool that evaluates math expressions (safe subset).
- **Search knowledge (stub):** Tool that accepts a query and returns a placeholder string; in Phase 4 this will be replaced or delegated to RAGService.retrieve or similar so the agent can “search” the indexed knowledge.
- Design: tools are LangChain tools (e.g. `@tool` or `StructuredTool`) so they work with `create_react_agent`.

---

## Acceptance Criteria

- [x] ConversationMemory correctly stores and returns last N turns.
- [x] ToolRegistry allows registering and retrieving tools (and register_from_mcp for MCP later).
- [x] Agent is created with model_factory LLM and registry tools (create_agent).
- [x] Agent run accepts query + context + knowledge_docs and returns a response (agent.invoke).
- [x] At least one tool (calculator, search_knowledge stub) is registered and callable by the agent.
- [x] Design allows adding MCP-wrapped tools later without changing agent_factory signature.

---

## Out of Scope

- Full RAGService orchestration (Phase 4). Wiring “search_knowledge” to real retrieval is Phase 4.
- UI and MCP API (Phase 5).

---

## Next Phase

Proceed to [PHASE_04_SERVICE_LAYER.md](PHASE_04_SERVICE_LAYER.md) to implement RAGService and wire retrieval + memory + agent.
