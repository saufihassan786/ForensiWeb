"""Core application configuration, security, database, and lifecycle modules."""

from app.core.config import Settings, get_settings, settings
from app.core.database import (
    Base,
    check_database_health,
    get_async_engine,
    get_async_session_factory,
    get_db_session,
    get_sync_db_session,
    get_sync_engine,
)
from app.core.errors import (
    AppException,
    ConflictError,
    EvidenceIntegrityError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
    setup_error_handling,
)

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "Base",
    "get_async_engine",
    "get_sync_engine",
    "get_async_session_factory",
    "get_db_session",
    "get_sync_db_session",
    "check_database_health",
    "AppException",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "EvidenceIntegrityError",
    "ServiceUnavailableError",
    "setup_error_handling",
]
