"""
Application settings with env-based configuration and validation.

Uses pydantic-settings for loading from environment and .env file.
All secrets (e.g. API keys) must be supplied via env; never hardcoded.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


RetrievalStrategy = Literal["vector", "hybrid", "adaptive"]


class Settings(BaseSettings):
    """Validated application configuration loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM (OpenRouter as default gateway) ---
    openrouter_api_key: str = ""
    default_provider: str = "openrouter"
    default_model: str = "google/gemini-2.0-flash-exp"

    # --- RAG (Phase 2+) ---
    retrieval_strategy: RetrievalStrategy = "adaptive"
    vector_store_path: str = "./data/vector_store"
    default_embedding_model: str | None = None
    chunk_size: int = 1000
    chunk_overlap: int = 200
    adaptive_retrieval_min_docs: int = 3

    @field_validator("chunk_size", "chunk_overlap")
    @classmethod
    def positive_int(cls, v: int) -> int:
        if isinstance(v, int) and v > 0:
            return v
        raise ValueError("chunk_size and chunk_overlap must be positive")

    @field_validator("adaptive_retrieval_min_docs")
    @classmethod
    def non_negative_int(cls, v: int) -> int:
        if isinstance(v, int) and v >= 0:
            return v
        raise ValueError("adaptive_retrieval_min_docs must be non-negative")

    @field_validator("openrouter_api_key", mode="before")
    @classmethod
    def strip_api_key(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return ""

    @model_validator(mode="after")
    def require_openrouter_key_when_openrouter(self) -> "Settings":
        if self.default_provider.lower() == "openrouter" and not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY must be set when using OpenRouter as default provider. "
                "Set it in .env or export OPENROUTER_API_KEY."
            )
        return self

    @field_validator("retrieval_strategy", mode="before")
    @classmethod
    def normalize_retrieval_strategy(cls, v: str) -> RetrievalStrategy:
        if isinstance(v, str):
            v = v.strip().lower()
            if v in ("vector", "hybrid", "adaptive"):
                return v
        return "adaptive"

    @field_validator("vector_store_path", mode="before")
    @classmethod
    def normalize_vector_store_path(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().rstrip("/")
        return "./data/vector_store"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached application settings singleton.

    Loads from environment and .env once; subsequent calls return the same instance.
    """
    return Settings()
