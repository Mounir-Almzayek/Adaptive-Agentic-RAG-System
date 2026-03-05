"""
Post-answer validation for the Adaptive Agentic RAG System (CRAG-style).

Simple heuristics to decide whether to accept the answer or trigger corrective
retrieval. Can be extended later with NLI, citation verification, or learned classifiers.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Defaults: accept if non-empty and above min length when docs were provided
DEFAULT_MIN_LENGTH = 10
DEFAULT_REQUIRE_SOURCE_HINT = False


def self_check(
    answer: str,
    docs: list | None,
    *,
    min_length: int = DEFAULT_MIN_LENGTH,
    require_source_hint: bool = DEFAULT_REQUIRE_SOURCE_HINT,
) -> bool:
    """
    Return True if the answer is acceptable; False to trigger corrective retrieval.

    Checks:
    - Answer is non-empty and not only whitespace.
    - When docs were provided: answer length >= min_length (avoids trivial refusals).
    - Optionally: answer contains a source/citation hint (e.g. "according to", "[1]", "source").

    This is a placeholder for more advanced validation (e.g. NLI, citation extraction).
    """
    if not answer or not answer.strip():
        return False
    if min_length > 0 and len(answer.strip()) < min_length:
        return False
    if require_source_hint and docs:
        hint_words = ("according to", "source", "[1]", "[2]", "document", "excerpt", "stated")
        lower = answer.lower()
        if not any(h in lower for h in hint_words):
            return False
    return True
