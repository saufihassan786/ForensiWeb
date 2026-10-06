"""ForensiWeb Database Connection and ORM Foundation (PHASE-02-F03).

Provides:
- SQLAlchemy 2.0 Declarative Base with consistent naming conventions
- Async and Synchronous engine and session factories
- Dependency injection helpers for FastAPI route handlers
- Database connectivity health check utility
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator, Generator, Optional
from datetime import datetime, timezone

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger("forensiweb.database")

# Consistent constraint naming convention across migrations and engines
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative Base class for all ForensiWeb domain and persistence entities."""

    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


# Engine and Session instances
_async_engine: Optional[AsyncEngine] = None
_sync_engine = None
_async_session_factory = None
_sync_session_factory = None


def get_async_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """Obtain or initialize the global AsyncEngine."""
    global _async_engine
    if _async_engine is None or database_url is not None:
        cfg = get_settings()
        url = database_url or cfg.DATABASE_URL
        # SQLite async requires aiosqlite, PostgreSQL requires asyncpg
        engine_kwargs = {"echo": cfg.DB_ECHO}
        if "sqlite" not in url:
            engine_kwargs.update({
                "pool_size": cfg.DB_POOL_SIZE,
                "max_overflow": cfg.DB_MAX_OVERFLOW,
                "pool_pre_ping": True,
            })
        _async_engine = create_async_engine(url, **engine_kwargs)
    return _async_engine


def get_sync_engine(database_url_sync: Optional[str] = None):
    """Obtain or initialize the synchronous engine (used for migrations and sync scripts)."""
    global _sync_engine
    if _sync_engine is None or database_url_sync is not None:
        cfg = get_settings()
        url = database_url_sync or cfg.DATABASE_URL_SYNC
        engine_kwargs = {"echo": cfg.DB_ECHO}
        if "sqlite" not in url:
            engine_kwargs.update({
                "pool_size": cfg.DB_POOL_SIZE,
                "max_overflow": cfg.DB_MAX_OVERFLOW,
                "pool_pre_ping": True,
            })
        _sync_engine = create_engine(url, **engine_kwargs)
    return _sync_engine


def get_async_session_factory(engine: Optional[AsyncEngine] = None) -> async_sessionmaker[AsyncSession]:
    """Obtain the async session factory."""
    active_engine = engine or get_async_engine()
    return async_sessionmaker(
        bind=active_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


def get_sync_session_factory(engine=None) -> sessionmaker[Session]:
    """Obtain the sync session factory."""
    active_engine = engine or get_sync_engine()
    return sessionmaker(
        bind=active_engine,
        class_=Session,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session with automatic commit/rollback."""
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db_session() -> Generator[Session, None, None]:
    """FastAPI or worker dependency yielding a sync database session."""
    session_factory = get_sync_session_factory()
    with session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


async def check_database_health(engine: Optional[AsyncEngine] = None) -> bool:
    """Execute a lightweight SQL query to verify database connectivity.

    Returns:
        bool: True if connection is responsive, False otherwise.
    """
    try:
        active_engine = engine or get_async_engine()
        async with active_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False
