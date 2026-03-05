"""
Model-agnostic LLM factory for the Adaptive Agentic RAG System.

Produces LangChain chat models configured for OpenRouter (default) so that
multiple backends (Google, OpenAI, Anthropic, etc.) are available via a single
API key and base URL. Designed for dependency injection and testability.
"""

from typing import TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from adaptive_rag.config.settings import get_settings

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable

# OpenRouter API endpoint (OpenAI-compatible)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Supported providers in this phase; more can be added later
SUPPORTED_PROVIDERS = frozenset({"openrouter"})


def create_llm(
    *,
    provider: str | None = None,
    model_id: str | None = None,
    api_key: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """
    Create a LangChain chat model (LLM) for the given provider and model.

    Uses OpenRouter as the default gateway: a single API key and base URL
    give access to multiple models (e.g. Google Gemini, OpenAI GPT-4).

    Args:
        provider: LLM provider. Currently only "openrouter" is supported.
            Defaults to config DEFAULT_PROVIDER.
        model_id: Model identifier (e.g. OpenRouter model id like
            "google/gemini-2.0-flash-exp"). Defaults to config DEFAULT_MODEL.
        api_key: API key for the provider. Defaults to config OPENROUTER_API_KEY.
        temperature: Sampling temperature in [0, 2]. Default 0.0 for reproducibility.
        max_tokens: Maximum tokens to generate. None uses model default.

    Returns:
        A LangChain BaseChatModel (Runnable) ready for .invoke() or LCEL chains.

    Raises:
        ValueError: If provider is not supported or API key is missing.
    """
    # Resolve provider first so we can raise a clear error before loading settings
    if provider is not None:
        resolved_provider = provider.strip().lower()
    else:
        settings = get_settings()
        resolved_provider = settings.default_provider.strip().lower()

    if resolved_provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider: '{resolved_provider}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_PROVIDERS))}."
        )

    settings = get_settings()
    resolved_model = (model_id or settings.default_model).strip()
    resolved_key = (api_key or settings.openrouter_api_key).strip()

    if resolved_provider == "openrouter" and not resolved_key:
        raise ValueError(
            "OpenRouter requires an API key. Set OPENROUTER_API_KEY in .env or pass api_key."
        )

    if not resolved_model:
        raise ValueError("model_id (or DEFAULT_MODEL) must be non-empty.")

    # OpenRouter is OpenAI-compatible; use ChatOpenAI with base_url
    llm = ChatOpenAI(
        model=resolved_model,
        api_key=resolved_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        # Prefer deterministic behavior for RAG/agent use
        model_kwargs={} if temperature == 0.0 else {},
    )

    return llm
