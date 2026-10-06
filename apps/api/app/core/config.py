"""ForensiWeb Configuration Management System (PHASE-02-F02).

Provides strongly-typed, environment-aware configuration using Pydantic Settings.
Implements secret masking, category organization, path resolution, and cached instantiation.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration settings."""

    # 1. Application Settings
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = "development"
    DEBUG: bool = False
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "ForensiWeb API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = (
        "Academic Digital Forensics and Security Analysis Platform API — "
        "Log Poisoning & Privilege Escalation Investigation"
    )
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # 2. Database Settings
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "forensiweb"
    POSTGRES_USER: str = "forensiweb_user"
    POSTGRES_PASSWORD: str = "insecure_dev_password_change_in_prod"
    DATABASE_URL: Optional[str] = None
    DATABASE_URL_SYNC: Optional[str] = None
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # 3. Security Settings
    SECRET_KEY: str = "insecure_dev_secret_key_minimum_32_characters_for_hmac"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 4. Evidence Storage Settings
    EVIDENCE_ROOT_DIR: Path = Path("data/evidence")
    EVIDENCE_ORIGINAL_DIR: Path = Path("data/evidence/original")
    EVIDENCE_WORKING_DIR: Path = Path("data/evidence/working")
    EVIDENCE_DERIVED_DIR: Path = Path("data/evidence/derived")
    EVIDENCE_MAX_FILE_SIZE_MB: int = 100
    EVIDENCE_ALLOWED_TYPES: List[str] = [
        "text/plain",
        "application/json",
        "application/octet-stream",
        "text/x-log",
    ]

    # 5. Lab Environment Settings
    LAB_HOST: str = "127.0.0.1"
    LAB_PORT: int = 5000
    LAB_TIMEOUT_SECONDS: int = 15
    VULNERABLE_APP_URL: str = "http://127.0.0.1:5000"

    # 6. Logging Settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return []

    @field_validator("EVIDENCE_ALLOWED_TYPES", mode="before")
    @classmethod
    def parse_evidence_types(cls, value: Any) -> List[str]:
        if isinstance(value, str):
            return [t.strip() for t in value.split(",") if t.strip()]
        if isinstance(value, list):
            return value
        return []

    @model_validator(mode="after")
    def assemble_database_urls(self) -> Settings:
        """Derive async and sync PostgreSQL URLs if not explicitly configured."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        if not self.DATABASE_URL_SYNC:
            self.DATABASE_URL_SYNC = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    def masked_dict(self) -> Dict[str, Any]:
        """Return a representation of configuration with sensitive credentials masked."""
        raw = self.model_dump()
        sensitive_keys = {
            "SECRET_KEY",
            "POSTGRES_PASSWORD",
            "DATABASE_URL",
            "DATABASE_URL_SYNC",
        }
        masked = {}
        for k, v in raw.items():
            if k in sensitive_keys:
                if "DATABASE_URL" in k and isinstance(v, str) and "@" in v:
                    prefix, suffix = v.split("@", 1)
                    driver = prefix.split("://")[0] if "://" in prefix else ""
                    masked[k] = f"{driver}://***:***@{suffix}"
                else:
                    masked[k] = "******"
            elif isinstance(v, Path):
                masked[k] = str(v)
            else:
                masked[k] = v
        return masked


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Obtain cached Settings singleton."""
    return Settings()


# Module-level settings export
settings: Settings = get_settings()
