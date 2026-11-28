"""All settings come from environment variables; backend/.env is a local convenience."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: SecretStr = SecretStr("")
    db_name: str = "jugnu"
    # Empty locally. "require" for Neon and most hosted PostgreSQL.
    db_sslmode: Literal["", "disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = ""

    supabase_url: str = ""
    supabase_publishable_key: str = ""

    demo_login: bool = False
    demo_jwt_secret: SecretStr = SecretStr("")

    ai_mode: Literal["openrouter", "demo"] = "openrouter"
    openrouter_api_key: SecretStr = SecretStr("")
    intake_chat_model: str = "openrouter/free"
    intake_extract_model: str = "openrouter/free"

    @field_validator("supabase_url")
    @classmethod
    def _normalise_supabase_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if value and not value.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise ValueError("SUPABASE_URL must start with https://")
        return value

    @field_validator("supabase_publishable_key")
    @classmethod
    def _reject_secret_key(cls, value: str) -> str:
        # This value is sent to every browser by GET /api/config.
        value = value.strip()
        if value.startswith("sb_secret_"):
            raise ValueError("Use the sb_publishable_ key: this value is sent to the browser")
        return value

    @model_validator(mode="after")
    def _demo_secret_required(self) -> "Settings":
        if self.demo_login and len(self.demo_jwt_secret.get_secret_value()) < 32:
            raise ValueError("DEMO_LOGIN=true needs DEMO_JWT_SECRET with at least 32 characters")
        return self

    def database_url(self, database: str | None = None) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value() or None,
            host=self.db_host,
            port=self.db_port,
            database=database or self.db_name,
            query={"sslmode": self.db_sslmode} if self.db_sslmode else {},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
