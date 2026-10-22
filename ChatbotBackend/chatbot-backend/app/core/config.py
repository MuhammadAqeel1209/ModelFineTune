from functools import lru_cache
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env."""

    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings, with a clear error for missing configuration."""
    try:
        # BaseSettings loads these required values from environment variables/.env.
        # Pylance cannot infer that runtime behavior from the constructor signature.
        return Settings()  # pyright: ignore[reportCallIssue]
    except ValidationError as exc:
        missing = ", ".join(
            str(error["loc"][0]).upper()
            for error in exc.errors()
            if error["type"] == "missing"
        )
        detail = f"Missing required configuration: {missing}" if missing else "Invalid configuration"
        raise RuntimeError(detail) from exc
