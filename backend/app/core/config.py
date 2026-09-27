from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+asyncpg://civicpulse:replace-with-a-local-password@localhost:5432/civicpulse"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
