"""Unit tests for Backend Configuration System (PHASE-02-F02).

Validates:
- Default settings initialization
- Environment variable overrides
- Derived sync and async PostgreSQL connection strings
- Masked dictionary masking of sensitive secrets
- Parsing of list-based settings (CORS origins, allowed evidence MIME types)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.core.config import Settings, get_settings


def test_default_settings() -> None:
    """Verify default configuration parameters match project defaults."""
    cfg = Settings()
    assert cfg.ENVIRONMENT in ("development", "testing")
    assert cfg.API_PORT == 8000
    assert cfg.API_PREFIX == "/api/v1"
    assert "postgresql+asyncpg" in cfg.DATABASE_URL
    assert "postgresql://" in cfg.DATABASE_URL_SYNC
    assert isinstance(cfg.EVIDENCE_ROOT_DIR, Path)


def test_database_url_assembly() -> None:
    """Verify database URLs are computed with custom credentials."""
    cfg = Settings(
        POSTGRES_USER="test_forensic_user",
        POSTGRES_PASSWORD="secure_password_xyz",
        POSTGRES_HOST="db.local",
        POSTGRES_PORT=5433,
        POSTGRES_DB="forensic_vault",
    )
    assert "test_forensic_user:secure_password_xyz@db.local:5433/forensic_vault" in cfg.DATABASE_URL
    assert "postgresql+asyncpg://" in cfg.DATABASE_URL
    assert "postgresql://" in cfg.DATABASE_URL_SYNC


def test_cors_origins_parsing() -> None:
    """Verify comma-separated string origins parse into clean list."""
    cfg = Settings(CORS_ORIGINS="http://localhost:3000, https://forensiweb.local")
    assert "http://localhost:3000" in cfg.CORS_ORIGINS
    assert "https://forensiweb.local" in cfg.CORS_ORIGINS


def test_evidence_allowed_types_parsing() -> None:
    """Verify comma-separated MIME types parse into a list."""
    cfg = Settings(EVIDENCE_ALLOWED_TYPES="text/plain, application/json")
    assert cfg.EVIDENCE_ALLOWED_TYPES == ["text/plain", "application/json"]


def test_secret_masking() -> None:
    """Verify masked_dict() hides secrets from serialized dicts."""
    cfg = Settings(
        SECRET_KEY="super_secret_signing_key_12345",
        POSTGRES_PASSWORD="ultra_secret_db_pass_999",
    )
    masked = cfg.masked_dict()

    # Raw secrets must NOT be present
    assert masked["SECRET_KEY"] == "******"
    assert masked["POSTGRES_PASSWORD"] == "******"
    assert "ultra_secret_db_pass_999" not in str(masked["DATABASE_URL"])
    assert "***:***@" in masked["DATABASE_URL"]


def test_get_settings_cache() -> None:
    """Verify get_settings returns the singleton cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
