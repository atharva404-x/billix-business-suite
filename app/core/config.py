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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
