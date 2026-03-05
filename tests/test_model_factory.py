"""
Smoke and unit tests for the LLM model factory.

Smoke test: requires OPENROUTER_API_KEY in env; skipped with a clear message if missing.
Unit tests: validate error handling and config resolution without calling the API.
"""

import os

import pytest


def _has_openrouter_key() -> bool:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    return bool(key)


@pytest.mark.unit
def test_create_llm_raises_on_unsupported_provider(monkeypatch):
    """Unsupported provider must raise ValueError with a clear message."""
    from adaptive_rag.config.settings import get_settings
    from adaptive_rag.core.model_factory import create_llm

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-dummy")
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")
    with pytest.raises(ValueError, match="Unsupported provider"):
        create_llm(provider="unknown_provider", api_key="dummy")


@pytest.mark.unit
def test_create_llm_raises_on_missing_openrouter_key(monkeypatch):
    """When provider is OpenRouter, missing API key must raise ValueError or ValidationError."""
    from pydantic import ValidationError

    from adaptive_rag.config.settings import get_settings
    from adaptive_rag.core.model_factory import create_llm

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")

    with pytest.raises((ValueError, ValidationError), match="API key|OPENROUTER_API_KEY"):
        create_llm(provider="openrouter", api_key="")


@pytest.mark.unit
def test_create_llm_returns_chat_model_with_dummy_key(monkeypatch):
    """With a non-empty API key, create_llm returns a LangChain chat model (no invoke)."""
    from langchain_core.language_models import BaseChatModel

    from adaptive_rag.config.settings import get_settings
    from adaptive_rag.core.model_factory import create_llm

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-dummy-for-test")
    # Avoid loading default provider from .env which might fail validation
    llm = create_llm(provider="openrouter", model_id="google/gemini-2.0-flash-exp", api_key="sk-dummy")
    assert isinstance(llm, BaseChatModel)
    assert llm.model == "google/gemini-2.0-flash-exp"
    # LangChain may wrap API key in SecretStr
    key_val = (
        llm.openai_api_key.get_secret_value()
        if hasattr(llm.openai_api_key, "get_secret_value")
        else llm.openai_api_key
    )
    assert key_val == "sk-dummy"
    assert llm.openai_api_base == "https://openrouter.ai/api/v1"


@pytest.mark.smoke
@pytest.mark.skipif(not _has_openrouter_key(), reason="OPENROUTER_API_KEY not set; skip live API call")
def test_create_llm_invoke_smoke():
    """
    Smoke test: create LLM from env, invoke once, assert non-empty content.

    Run with: pytest tests/test_model_factory.py -m smoke -v
    """
    from langchain_core.messages import HumanMessage

    from adaptive_rag.config.settings import get_settings
    from adaptive_rag.core.model_factory import create_llm

    get_settings.cache_clear()
    llm = create_llm()
    response = llm.invoke([HumanMessage(content="Say hello in one word.")])
    content = response.content if hasattr(response, "content") else str(response)
    assert content is not None
    assert len(content.strip()) > 0
