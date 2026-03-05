#!/usr/bin/env python3
"""
Smoke test: create LLM from env and run one completion.

Usage:
    Set OPENROUTER_API_KEY in .env or environment, then:
    python scripts/smoke_llm.py

    Or from repo root with PYTHONPATH:
    PYTHONPATH=. python scripts/smoke_llm.py
"""

import sys
from pathlib import Path

# Ensure adaptive_rag is importable when run from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from langchain_core.messages import HumanMessage

    from adaptive_rag.config.settings import get_settings
    from adaptive_rag.core.model_factory import create_llm

    get_settings.cache_clear()
    try:
        settings = get_settings()
    except Exception as e:
        print("Config error:", e, file=sys.stderr)
        print("Set OPENROUTER_API_KEY in .env or environment.", file=sys.stderr)
        return 1

    print("Creating LLM (OpenRouter)...", flush=True)
    llm = create_llm()
    print("Invoking: 'Say hello in one word.'", flush=True)
    response = llm.invoke([HumanMessage(content="Say hello in one word.")])
    content = response.content if hasattr(response, "content") else str(response)
    print("Response:", content)
    if not content or not content.strip():
        print("Smoke test failed: empty response.", file=sys.stderr)
        return 1
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
