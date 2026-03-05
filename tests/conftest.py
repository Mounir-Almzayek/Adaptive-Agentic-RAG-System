"""
Pytest configuration and shared fixtures.

Resets get_settings cache between tests that mutate env so each test
gets a clean config (when needed).
"""

import os

import pytest


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    """Clear settings cache after each test so env changes are visible in next test."""
    from adaptive_rag.config.settings import get_settings

    yield
    get_settings.cache_clear()
