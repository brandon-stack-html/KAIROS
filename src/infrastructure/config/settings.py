from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "boiler-plate-saas"
    debug: bool = False
    # Set to "production" to enforce security validations at startup.
    # Generate a secret with: openssl rand -hex 32
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # CORS — comma-separated list or JSON array in env var ALLOWED_ORIGINS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # JWT
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30  # short-lived; rely on refresh tokens for longer sessions
    refresh_token_ttl_days: int = 30  # configurable via REFRESH_TOKEN_TTL_DAYS env var

    # Email
    email_provider: Literal["resend", "console"] = "console"
    resend_api_key: str | None = None
    email_from: str = "noreply@example.com"

    # Frontend (used to build links in emails)
    frontend_url: str = "http://localhost:3000"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.environment == "production":
            if self.secret_key == "change-me-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed from the default. "
                    "Generate one with: openssl rand -hex 32"
                )
            if len(self.secret_key) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long")
        return self


settings = Settings()
