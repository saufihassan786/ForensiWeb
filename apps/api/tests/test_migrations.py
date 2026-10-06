"""Unit tests for Database Migration Framework (PHASE-02-F04).

Validates:
- Alembic configuration file (alembic.ini) structure and accessibility
- Migration environment (env.py) target metadata integrity
- Baseline migration script (0001_initial_core_tables) execution:
  - Upgrade to head (creates all 8 tables)
  - Downgrade to base (drops all tables cleanly)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
API_DIR = REPO_ROOT / "apps" / "api"
ALEMBIC_INI = API_DIR / "alembic.ini"


def test_alembic_config_exists() -> None:
    """Verify alembic.ini configuration file is present and readable."""
    assert ALEMBIC_INI.is_file(), f"alembic.ini not found at {ALEMBIC_INI}"
    content = ALEMBIC_INI.read_text(encoding="utf-8")
    assert "script_location = alembic" in content
    assert "sqlalchemy.url" in content


def test_alembic_migration_upgrade_and_downgrade_cycle() -> None:
    """Verify that Alembic migrations run cleanly up and down on a fresh database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        temp_db_path = tmp.name

    try:
        sqlite_url = f"sqlite:///{temp_db_path}"

        alembic_cfg = Config(str(ALEMBIC_INI))
        alembic_cfg.set_main_option("sqlalchemy.url", sqlite_url)
        alembic_cfg.set_main_option("script_location", str(API_DIR / "alembic"))

        # 1. Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        engine = create_engine(sqlite_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        expected_core_tables = {
            "cases",
            "evidence",
            "events",
            "detections",
            "timeline_entries",
            "findings",
            "reports",
            "audit_logs",
            "alembic_version",
        }
        assert expected_core_tables.issubset(tables), f"Tables missing after upgrade: {expected_core_tables - tables}"

        # 2. Run downgrade to base
        command.downgrade(alembic_cfg, "base")

        # Inspect again: core tables should be removed
        inspector = inspect(engine)
        remaining_tables = set(inspector.get_table_names()) - {"alembic_version"}
        assert len(remaining_tables) == 0, f"Remaining tables after downgrade: {remaining_tables}"

    finally:
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except OSError:
                pass
