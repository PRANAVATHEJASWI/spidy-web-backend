"""
Centralized settings. All configuration comes from environment variables —
nothing is hardcoded here. Required fields will raise a validation error at
startup if missing, so misconfiguration fails loudly instead of silently
falling back to an insecure default (e.g. open CORS, no auth).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Firebase ---
    # Paste the full service account JSON as a single env var value on Render.
    # Do NOT commit a credentials file or reference a local path in production.
    FIREBASE_CREDENTIALS_JSON: str | None = None

    # --- Auth tokens ---
    # Required: without this, all write endpoints reject every request.
    EDITOR_ACCESS_TOKEN: str
    # Optional: if unset, there is simply no readonly tier (only editor / none).
    READONLY_ACCESS_TOKEN: str | None = None

    # --- CORS ---
    # Required, comma-separated, e.g.:
    # "https://pranavathejaswi.dev,http://localhost:5173"
    # No wildcard default — an empty/misconfigured value should be caught
    # immediately, not silently opened to "*".
    ALLOWED_ORIGINS: str

    ENVIRONMENT: str = "production"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
