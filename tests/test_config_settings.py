"""
Unit tests for application settings.

Validates env loading, defaults, and validation rules without touching external services.
"""

import pytest


@pytest.mark.unit
def test_get_settings_returns_settings_instance(monkeypatch):
    """get_settings() returns a Settings instance with expected attributes."""
    from adaptive_rag.config.settings import Settings, get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-dummy")
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert hasattr(settings, "openrouter_api_key")
    assert hasattr(settings, "default_model")
    assert hasattr(settings, "retrieval_strategy")
    assert settings.retrieval_strategy in ("vector", "hybrid", "adaptive")
    assert settings.vector_store_path


@pytest.mark.unit
def test_settings_validation_fails_when_openrouter_key_empty_and_default_openrouter(monkeypatch):
    """When DEFAULT_PROVIDER is openrouter, empty OPENROUTER_API_KEY must raise."""
    from pydantic import ValidationError

    from adaptive_rag.config.settings import Settings, get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")

    with pytest.raises(ValidationError, match="OPENROUTER_API_KEY"):
        Settings()


@pytest.mark.unit
def test_settings_loads_with_dummy_key(monkeypatch):
    """Settings load successfully when OPENROUTER_API_KEY is non-empty."""
    from adaptive_rag.config.settings import Settings, get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("DEFAULT_PROVIDER", "openrouter")
    settings = get_settings()
    assert settings.openrouter_api_key == "sk-test"
    assert settings.default_provider == "openrouter"
