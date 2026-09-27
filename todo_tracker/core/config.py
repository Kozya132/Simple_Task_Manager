from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="TODO_TRACKER_",
        extra="ignore",
    )

    DATABASE_URL: PostgresDsn
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 30


settings = Settings()
