"""
Conversation memory for the Adaptive Agentic RAG System.

Stores recent user/assistant turns and exposes them as context for the agent.
Designed for single-session use per RAGService instance; backend can be
swapped for persistence later without changing the interface.
"""

from __future__ import annotations

from typing import TypedDict


class Turn(TypedDict):
    """A single conversation turn."""

    user: str
    assistant: str


class ConversationMemory:
    """
    In-memory store of recent conversation turns for context in multi-turn RAG.

    Thread-safe for single-writer use (one session per instance). For
    multi-user deployments, use one instance per session or add locking.
    """

    def __init__(self, max_turns: int = 100) -> None:
        self._turns: list[Turn] = []
        self._max_turns = max(1, max_turns)

    def add(self, user_message: str, assistant_message: str) -> None:
        """Append one user/assistant turn. Trims oldest if over max_turns."""
        self._turns.append(
            Turn(user=(user_message or "").strip(), assistant=(assistant_message or "").strip())
        )
        while len(self._turns) > self._max_turns:
            self._turns.pop(0)

    def get_context(self, limit: int = 5) -> list[Turn]:
        """Return the last `limit` turns (oldest first). Empty list if none."""
        n = max(0, limit)
        if n == 0:
            return []
        return list(self._turns[-n:])

    def get_context_as_messages(self, limit: int = 5) -> list[tuple[str, str]]:
        """
        Return last `limit` turns as (role, content) pairs for prompt building.

        Role is "user" or "assistant". Order: oldest first.
        """
        turns = self.get_context(limit=limit)
        out: list[tuple[str, str]] = []
        for t in turns:
            if t["user"]:
                out.append(("user", t["user"]))
            if t["assistant"]:
                out.append(("assistant", t["assistant"]))
        return out

    def clear(self) -> None:
        """Reset memory for a new session."""
        self._turns.clear()

    def __len__(self) -> int:
        return len(self._turns)
