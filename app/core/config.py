from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Spider Portfolio Builder"
    firebase_credentials_path: str = Field(default="firebase.json")
    firebase_project_id: str | None = None
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def firebase_credentials_file(self) -> Path:
        return Path(__file__).resolve().parents[2] / self.firebase_credentials_path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
