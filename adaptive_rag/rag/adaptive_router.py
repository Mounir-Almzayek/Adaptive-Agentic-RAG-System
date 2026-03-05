"""
Adaptive retrieval strategy selection.

Encapsulates the heuristic for when to use vector-only vs hybrid retrieval.
Can be extended later with a classifier or query-type detection.
"""

from __future__ import annotations

# Minimum number of vector results below which we fall back to hybrid
DEFAULT_MIN_DOCS_THRESHOLD = 3


def choose_strategy(
    vector_result_count: int,
    min_docs_threshold: int = DEFAULT_MIN_DOCS_THRESHOLD,
) -> str:
    """
    Choose retrieval strategy based on vector result count.

    If vector search returned too few documents, fall back to hybrid to broaden
    coverage. Otherwise stick to vector for efficiency.

    Args:
        vector_result_count: Number of docs returned by vector search.
        min_docs_threshold: If vector_result_count < this, return "hybrid".

    Returns:
        "vector" or "hybrid".
    """
    if vector_result_count < min_docs_threshold:
        return "hybrid"
    return "vector"
