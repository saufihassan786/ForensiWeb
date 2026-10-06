"""
Test Development Tooling for ForensiWeb.

Validates PHASE-01-F05: Development Tooling.
Verifies:
- Makefile exists and defines standard developer targets.
- pyproject.toml exists and configures pytest and build settings.
- LICENSE exists and contains MIT license.
- Unified developer CLI (scripts/development/dev.py) executes and exposes expected commands.
- scripts/setup/init_env.py provides safe environment initialization.
"""

from pathlib import Path
import subprocess
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

MAKEFILE_PATH = REPO_ROOT / "Makefile"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
LICENSE_PATH = REPO_ROOT / "LICENSE"
DEV_CLI_PATH = REPO_ROOT / "scripts" / "development" / "dev.py"
INIT_ENV_PATH = REPO_ROOT / "scripts" / "setup" / "init_env.py"


def test_makefile_exists_and_contains_standard_targets():
    """Verify root Makefile exists and defines standard lifecycle targets."""
    assert MAKEFILE_PATH.is_file(), "Makefile is missing from repository root"
    content = MAKEFILE_PATH.read_text(encoding="utf-8")
    
    expected_targets = [
        "help:",
        "setup:",
        "validate-env:",
        "test:",
        "test-unit:",
        "test-integration:",
        "test-hygiene:",
        "clean:",
        "lab-up:",
        "lab-down:",
        "lab-reset:",
    ]
    for target in expected_targets:
        assert target in content, f"Makefile is missing target: '{target}'"


def test_pyproject_toml_exists_and_configures_pytest():
    """Verify pyproject.toml exists and configures project metadata and pytest."""
    assert PYPROJECT_PATH.is_file(), "pyproject.toml is missing from repository root"
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    
    assert "[project]" in content
    assert 'name = "forensiweb"' in content
    assert "[tool.pytest.ini_options]" in content
    assert 'testpaths = ["tests", "apps", "packages"]' in content
    assert "markers = [" in content


def test_license_exists_and_valid():
    """Verify LICENSE file exists and contains MIT license header."""
    assert LICENSE_PATH.is_file(), "LICENSE file is missing from repository root"
    content = LICENSE_PATH.read_text(encoding="utf-8")
    assert "MIT License" in content
    assert "ForensiWeb" in content


def test_dev_cli_script_exists():
    """Verify scripts/development/dev.py exists."""
    assert DEV_CLI_PATH.is_file(), "scripts/development/dev.py is missing"


def test_dev_cli_help_command():
    """Verify dev.py runs --help cleanly and advertises core subcommands."""
    result = subprocess.run(
        [sys.executable, str(DEV_CLI_PATH), "--help"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    assert result.returncode == 0
    stdout = result.stdout
    for cmd in ["setup", "validate-env", "test", "hygiene", "clean", "lab-reset"]:
        assert cmd in stdout, f"dev.py help output missing subcommand '{cmd}'"


def test_dev_cli_validate_env_command():
    """Verify dev.py validate-env --check-example executes cleanly."""
    result = subprocess.run(
        [sys.executable, str(DEV_CLI_PATH), "validate-env", "--check-example"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout


def test_dev_cli_hygiene_command():
    """Verify dev.py hygiene executes cleanly."""
    result = subprocess.run(
        [sys.executable, str(DEV_CLI_PATH), "hygiene"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout


def test_init_env_script_exists():
    """Verify scripts/setup/init_env.py exists."""
    assert INIT_ENV_PATH.is_file(), "scripts/setup/init_env.py is missing"
