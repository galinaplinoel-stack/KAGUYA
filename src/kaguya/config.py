"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Global settings for KAGUYA. Loaded from env vars or .env file."""

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./kaguya.db",
        description="Async SQLAlchemy database URL",
    )

    # LLM integration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_api_base: str = Field(
        default="https://api.openai.com/v1", description="OpenAI-compatible API base URL"
    )
    default_model: str = Field(default="gpt-4", description="Default LLM model name")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    log_level: str = Field(default="info")

    # Personality defaults
    default_decay_rate: float = Field(default=0.05, description="Emotion decay per tick")
    default_learning_rate: float = Field(default=0.01, description="Evolution learning rate")
    max_interaction_history: int = Field(default=1000)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
