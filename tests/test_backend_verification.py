"""Backend Verification Tests (PHASE-02-F09) for ForensiWeb.

Executes the Phase 2 Backend Foundation Verification Protocol via pytest,
verifying that all acceptance criteria across the 9 features of Phase 2 pass cleanly.
"""

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from scripts.testing.verify_backend import (
    verify_f01_bootstrap,
    verify_f02_configuration,
    verify_f03_database_connection,
    verify_f04_migration_framework,
    verify_f05_core_data_models,
    verify_f06_api_versioning_and_routing,
    verify_f07_health_checks,
    verify_f08_error_handling,
    verify_scope_and_premature_guard,
)


@pytest.mark.unit
def test_f01_backend_bootstrap():
    assert verify_f01_bootstrap(), "F01 Backend Application Bootstrap check failed"


@pytest.mark.unit
def test_f02_configuration():
    assert verify_f02_configuration(), "F02 Configuration System check failed"


@pytest.mark.unit
def test_f03_database_connection():
    assert verify_f03_database_connection(), "F03 Database Connection check failed"


@pytest.mark.unit
def test_f04_migration_framework():
    assert verify_f04_migration_framework(), "F04 Migration Framework check failed"


@pytest.mark.unit
def test_f05_core_data_models():
    assert verify_f05_core_data_models(), "F05 Core Data Models check failed"


@pytest.mark.unit
def test_f06_api_versioning_and_routing():
    assert verify_f06_api_versioning_and_routing(), "F06 API Versioning and Routing check failed"


@pytest.mark.unit
def test_f07_health_checks():
    assert verify_f07_health_checks(), "F07 Health and Readiness Checks check failed"


@pytest.mark.unit
def test_f08_error_handling():
    assert verify_f08_error_handling(), "F08 Error Handling check failed"


@pytest.mark.unit
def test_f09_premature_guard():
    assert verify_scope_and_premature_guard(), "F09 Premature Implementation Guard failed"
