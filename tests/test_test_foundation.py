"""
Test Foundation Verification for ForensiWeb.

Validates PHASE-01-F06: Test Foundation.
Verifies:
- conftest.py global fixtures operate correctly.
- tests/fixtures/ contains valid sample evidence files.
- Fixture loader utilities in tests.fixtures work cleanly.
- pytest discovery and execution operate as expected across test directories.
- scripts/testing/run_tests.py CLI executes and dispatches properly.
"""

from pathlib import Path
import subprocess
import sys
import pytest

from tests.fixtures import get_fixture_path, load_fixture_text


@pytest.mark.unit
def test_repo_root_fixture(repo_root: Path):
    """Verify repo_root fixture points to the valid repository root directory."""
    assert repo_root.is_dir()
    assert (repo_root / "pyproject.toml").is_file()
    assert (repo_root / "README.md").is_file()


@pytest.mark.unit
def test_fixtures_dir_fixture(fixtures_dir: Path):
    """Verify fixtures_dir fixture resolves correctly."""
    assert fixtures_dir.is_dir()
    assert (fixtures_dir / "__init__.py").is_file()


@pytest.mark.unit
def test_temp_evidence_env_fixture(temp_evidence_env):
    """Verify temp_evidence_env creates the full isolated directory structure."""
    assert "original" in temp_evidence_env
    assert "working" in temp_evidence_env
    assert "derived" in temp_evidence_env
    assert "reports" in temp_evidence_env

    for key, path in temp_evidence_env.items():
        assert path.is_dir(), f"Expected temporary directory for '{key}' does not exist: {path}"


@pytest.mark.unit
def test_isolated_env_fixture(isolated_env):
    """Verify isolated_env fixture provides access to mutable environment."""
    isolated_env["FORENSIWEB_TEST_VAR"] = "test_value_123"
    assert isolated_env.get("FORENSIWEB_TEST_VAR") == "test_value_123"


@pytest.mark.unit
def test_sample_raw_logs_fixture(sample_raw_logs):
    """Verify sample_raw_logs fixture supplies access, error, and auditd logs."""
    assert "access" in sample_raw_logs
    assert "error" in sample_raw_logs
    assert "auditd" in sample_raw_logs

    assert "GET /view?page=" in sample_raw_logs["access"]
    assert "Path traversal attempt" in sample_raw_logs["error"]
    assert "type=SYSCALL" in sample_raw_logs["auditd"]


@pytest.mark.unit
def test_fixture_loader_helpers():
    """Verify get_fixture_path and load_fixture_text utility functions."""
    path = get_fixture_path("sample_access.log")
    assert path.is_file()
    text = load_fixture_text("sample_access.log")
    assert len(text) > 0

    with pytest.raises(FileNotFoundError):
        get_fixture_path("non_existent_fixture.xyz")


@pytest.mark.unit
def test_run_tests_cli_help():
    """Verify scripts/testing/run_tests.py runs --help cleanly with expected flags."""
    run_tests_script = Path(__file__).resolve().parent.parent / "scripts" / "testing" / "run_tests.py"
    assert run_tests_script.is_file()

    result = subprocess.run(
        [sys.executable, str(run_tests_script), "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    stdout = result.stdout
    assert "--unit" in stdout
    assert "--integration" in stdout
    assert "--e2e" in stdout
    assert "--hygiene" in stdout


@pytest.mark.unit
def test_test_subdirectories_exist(repo_root: Path):
    """Verify integration, e2e, fixtures, and regression test directories exist."""
    expected_subdirs = ["integration", "e2e", "fixtures", "regression"]
    for subdir in expected_subdirs:
        dir_path = repo_root / "tests" / subdir
        assert dir_path.is_dir(), f"Expected test directory missing: tests/{subdir}"
