"""
ForensiWeb Root Pytest Configuration and Central Fixtures.

Defines global fixtures and test configuration for unit, integration,
and end-to-end tests across apps and packages.
"""

import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Dict, Generator, Any
import pytest

REPO_ROOT = Path(__file__).resolve().parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"

# Register vulnerable-web-app as `vuln_app` in sys.modules to prevent collision with apps/api/app
_vuln_app_dir = REPO_ROOT / "apps" / "vulnerable-web-app" / "app"
if _vuln_app_dir.is_dir() and "vuln_app" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "vuln_app",
        _vuln_app_dir / "__init__.py",
        submodule_search_locations=[str(_vuln_app_dir)],
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["vuln_app"] = mod
        spec.loader.exec_module(mod)



@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the absolute path to the ForensiWeb repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return the absolute path to the tests/fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def temp_evidence_env(tmp_path: Path) -> Generator[Dict[str, Path], None, None]:
    """
    Provide an isolated temporary evidence storage directory structure.
    Mimics data/evidence/ layout with original/, working/, derived/, and reports/ dirs.
    """
    evidence_root = tmp_path / "evidence"
    original_dir = evidence_root / "original"
    working_dir = evidence_root / "working"
    derived_dir = evidence_root / "derived"
    reports_dir = tmp_path / "reports"

    for d in (original_dir, working_dir, derived_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)

    yield {
        "root": evidence_root,
        "original": original_dir,
        "working": working_dir,
        "derived": derived_dir,
        "reports": reports_dir,
    }


@pytest.fixture
def isolated_env() -> Generator[Dict[str, str], None, None]:
    """
    Safely isolate os.environ modifications during a test.
    Restores the original environment upon test teardown.
    """
    original_environ = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original_environ)


@pytest.fixture(scope="session")
def sample_raw_logs() -> Dict[str, str]:
    """
    Provide sample synthetic log strings from tests/fixtures for parser tests.
    """
    logs = {}
    access_log = FIXTURES_DIR / "sample_access.log"
    if access_log.is_file():
        logs["access"] = access_log.read_text(encoding="utf-8")

    error_log = FIXTURES_DIR / "sample_error.log"
    if error_log.is_file():
        logs["error"] = error_log.read_text(encoding="utf-8")

    auditd_log = FIXTURES_DIR / "sample_auditd.log"
    if auditd_log.is_file():
        logs["auditd"] = auditd_log.read_text(encoding="utf-8")

    return logs
