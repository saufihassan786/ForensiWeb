"""
Test Foundation Verification (PHASE-01-F08) for ForensiWeb.

Executes the Phase 1 Foundation Verification Protocol via pytest, asserting
that all acceptance criteria across the 8 features of Phase 1 pass cleanly.
"""

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.verify_foundation import (
    verify_f01_repository_structure,
    verify_f02_documentation_structure,
    verify_f03_environment_configuration,
    verify_f04_git_hygiene,
    verify_f05_development_tooling,
    verify_f06_test_foundation,
    verify_f07_docker_foundation,
    verify_f08_scope_and_premature_implementation_guard,
)


@pytest.mark.unit
def test_f01_repository_structure():
    assert verify_f01_repository_structure(), "F01 Repository Structure check failed"


@pytest.mark.unit
def test_f02_documentation_structure():
    assert verify_f02_documentation_structure(), "F02 Documentation Structure check failed"


@pytest.mark.unit
def test_f03_environment_configuration():
    assert verify_f03_environment_configuration(), "F03 Environment Configuration check failed"


@pytest.mark.unit
def test_f04_git_hygiene():
    assert verify_f04_git_hygiene(), "F04 Git Hygiene check failed"


@pytest.mark.unit
def test_f05_development_tooling():
    assert verify_f05_development_tooling(), "F05 Development Tooling check failed"


@pytest.mark.unit
def test_f06_test_foundation():
    assert verify_f06_test_foundation(), "F06 Test Foundation check failed"


@pytest.mark.unit
def test_f07_docker_foundation():
    assert verify_f07_docker_foundation(), "F07 Docker Foundation check failed"


@pytest.mark.unit
def test_f08_premature_implementation_guard():
    assert verify_f08_scope_and_premature_implementation_guard(), "F08 Premature Implementation Guard failed"
