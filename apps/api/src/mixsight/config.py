"""Application settings, loaded from environment.

See `.env.example` at the repo root for the full set of vars. Required vars
fail fast on app start; optional vars default to `None` and are checked at
the surface that needs them (e.g., Anthropic key not required until the LLM
client is wired in Week 4).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Path is config.py → mixsight/ → src/ → api/ → apps/ → repo root.
_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    DATABASE_URL: str  # asyncpg driver, also used by Alembic via run_sync

    REDIS_URL: str | None = None

    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: str | None = None
    CLERK_SECRET_KEY: str | None = None
    CLERK_WEBHOOK_SECRET: str | None = None

    ANTHROPIC_API_KEY: str | None = None

    MIXSIGHT_FERNET_KEY: str | None = None
    MIXSIGHT_FERNET_KEY_VERSION: int = 1
    ANONYMIZATION_SALT: str | None = None

    FRONTEND_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
