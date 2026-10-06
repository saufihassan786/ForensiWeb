"""Unit tests for Database Connection and Engine Foundation (PHASE-02-F03).

Validates:
- Declarative Base naming convention configuration
- Sync engine connection and session transactions
- Database health check responsiveness and failure tolerance
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import (
    Base,
    check_database_health,
    get_sync_engine,
    get_sync_session_factory,
)


def test_base_metadata_naming_conventions() -> None:
    """Verify that the declarative Base has the established PostgreSQL naming convention."""
    assert Base.metadata.naming_convention is not None
    assert "ix" in Base.metadata.naming_convention
    assert "fk" in Base.metadata.naming_convention
    assert "pk" in Base.metadata.naming_convention


def test_sync_engine_and_session() -> None:
    """Verify that a synchronous engine and session factory can perform basic transactions."""
    engine = get_sync_engine("sqlite:///:memory:")
    session_factory = get_sync_session_factory(engine)

    with session_factory() as session:
        result = session.execute(text("SELECT 42"))
        val = result.scalar()
        assert val == 42


@pytest.mark.anyio
async def test_check_database_health_failure_tolerance() -> None:
    """Verify check_database_health handles unreachable hosts gracefully by returning False."""
    from sqlalchemy.ext.asyncio import create_async_engine

    # Use a non-routable dummy address to simulate unavailable database
    dummy_engine = create_async_engine(
        "postgresql+asyncpg://dummy:dummy@127.0.0.1:59999/dummy",
        connect_args={"timeout": 0.5},
    )
    is_healthy = await check_database_health(dummy_engine)
    assert is_healthy is False
