
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Billix"
    ENV: str = "development"

    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///:memory:", validation_alias="DATABASE_URL")

    # Clerk Configuration
    CLERK_PUBLISHABLE_KEY: str = Field(default="", validation_alias="CLERK_PUBLISHABLE_KEY")
    CLERK_SECRET_KEY: str = Field(default="", validation_alias="CLERK_SECRET_KEY")
    CLERK_JWKS_URL: str = Field(default="", validation_alias="CLERK_JWKS_URL")
    CLERK_API_URL: str = Field(default="https://api.clerk.com/v1", validation_alias="CLERK_API_URL")
    CLERK_JWT_AUDIENCE: str = Field(default="", validation_alias="CLERK_JWT_AUDIENCE")

    # Logging & Observability Configuration
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT") # Options: json, text
    SENTRY_DSN: str = Field(default="", validation_alias="SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, validation_alias="SENTRY_TRACES_SAMPLE_RATE")

    # Security & Protection Configuration
    ALLOWED_HOSTS: list[str] = Field(default_factory=lambda: ["*"], validation_alias="ALLOWED_HOSTS")
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000", "http://localhost:80"],
        validation_alias="CORS_ORIGINS"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, validation_alias="RATE_LIMIT_PER_MINUTE")
    MAX_REQUEST_SIZE_BYTES: int = Field(default=10485760, validation_alias="MAX_REQUEST_SIZE_BYTES") # Default 10 MB

    # Database Pool Optimization Configuration
    DB_POOL_SIZE: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    DB_POOL_RECYCLE: int = Field(default=1800, validation_alias="DB_POOL_RECYCLE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
