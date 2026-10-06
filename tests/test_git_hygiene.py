"""
Test Git Hygiene and Ignore Rules for ForensiWeb.

Validates PHASE-01-F04: Git Hygiene and Ignore Rules.
Verifies:
- .gitignore and .gitattributes exist at the repository root.
- Sensitive files, caches, virtual environments, and temporary artifacts are ignored.
- Critical files (.env.example, .gitkeep, documentation) remain tracked.
- Git ignore engine operates correctly against test sample paths.
- Current repository workspace contains no unignored secrets or temporary cache files.
"""

from pathlib import Path
import subprocess
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.check_git_hygiene import (
    verify_gitignore_content,
    verify_git_ignore_behavior,
    MUST_IGNORE_SAMPLES,
    MUST_NOT_IGNORE_SAMPLES,
    is_ignored_by_git,
)

GITIGNORE_PATH = REPO_ROOT / ".gitignore"
GITATTRIBUTES_PATH = REPO_ROOT / ".gitattributes"


def test_gitignore_exists_and_non_empty():
    """Verify that root .gitignore exists and is populated."""
    assert GITIGNORE_PATH.is_file(), ".gitignore is missing at repository root"
    content = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert len(content.strip()) > 200, ".gitignore is empty or too short"


def test_gitattributes_exists_and_non_empty():
    """Verify that root .gitattributes exists and enforces LF line endings."""
    assert GITATTRIBUTES_PATH.is_file(), ".gitattributes is missing at repository root"
    content = GITATTRIBUTES_PATH.read_text(encoding="utf-8")
    assert "text=auto eol=lf" in content, ".gitattributes does not configure LF line endings"
    assert "*.py text eol=lf" in content
    assert "*.sh text eol=lf" in content


def test_gitignore_contains_required_directives():
    """Verify that .gitignore contains all critical security and cache directives."""
    ok, errors = verify_gitignore_content()
    assert ok, f".gitignore content check failed: {errors}"


@pytest.mark.parametrize("sample_path", MUST_IGNORE_SAMPLES)
def test_git_ignores_sensitive_and_temporary_artifacts(sample_path):
    """Verify git check-ignore returns True for sensitive files and runtime caches."""
    assert is_ignored_by_git(sample_path), f"Git failed to ignore path: '{sample_path}'"


@pytest.mark.parametrize("sample_path", MUST_NOT_IGNORE_SAMPLES)
def test_git_does_not_ignore_required_assets(sample_path):
    """Verify git check-ignore returns False for tracked assets (.env.example, .gitkeep)."""
    assert not is_ignored_by_git(sample_path), f"Git incorrectly ignored required asset: '{sample_path}'"


def test_no_unignored_secrets_in_workspace():
    """Verify no untracked secret files (.env, *.pem, *.key) currently exist in workspace."""
    forbidden_extensions = {".pem", ".key", ".pfx", ".p12"}
    for path in REPO_ROOT.rglob("*"):
        if path.is_file():
            # Check for forbidden secret extensions
            assert path.suffix not in forbidden_extensions, f"Prohibited secret file found: {path}"
            # Check that any .env file in workspace is only .env.example
            if path.name.startswith(".env") and path.name != ".env.example":
                pytest.fail(f"Actual .env file found in workspace: {path}")
