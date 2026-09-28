from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    triage_provider: str = "rules"
    triage_timeout_seconds: float = 10.0
    triage_llm_base_url: str = "https://api.groq.com/openai/v1"
    triage_llm_model: str = "llama-3.1-8b-instant"
    triage_llm_api_key: str | None = None
    triage_ollama_base_url: str = "http://localhost:11434"
    triage_ollama_model: str = "llama3.2:1b"
    database_url: str = Field(
        default="postgresql+asyncpg://civicpulse:replace-with-a-local-password@localhost:5432/civicpulse"
    )
    redis_url: str = "redis://localhost:6379/0"
    stats_cache_ttl_seconds: int = 30
    complaint_rate_limit: int = 10
    complaint_rate_window_seconds: int = 60
    triage_cache_ttl_seconds: int = 86400


@lru_cache
def get_settings() -> Settings:
    return Settings()
