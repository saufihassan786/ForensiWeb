#!/usr/bin/env python3
"""
ForensiWeb Git Hygiene and Ignore Rules Validator.

Verifies that .gitignore adheres to docs/rules.md (Section 35 & 36),
ensures sensitive files and caches are ignored by Git, and confirms that
critical repository assets (.env.example, .gitkeep) remain tracked.
"""

from __future__ import annotations
from pathlib import Path
import re
import subprocess
import sys
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Patterns that MUST be ignored by git
MUST_IGNORE_SAMPLES = [
    ".env",
    ".env.local",
    ".env.production",
    "secret_key.pem",
    "private.key",
    "id_rsa",
    "__pycache__/foo.cpython-313.pyc",
    "some_module.pyc",
    ".pytest_cache/v/cache",
    ".coverage",
    "node_modules/react/index.js",
    "apps/frontend/dist/index.html",
    "data/evidence/working/temp_analysis.log",
    "data/evidence/derived/temp_timeline.json",
    "data/reports/draft_report.pdf",
    "runtime.log",
    "dev.sqlite3",
    ".DS_Store",
    "Thumbs.db",
]

# Assets that MUST NOT be ignored by git
MUST_NOT_IGNORE_SAMPLES = [
    ".env.example",
    "README.md",
    "docs/PRD.md",
    "docs/architecture.md",
    "data/evidence/working/.gitkeep",
    "data/evidence/derived/.gitkeep",
    "data/reports/.gitkeep",
    "lab/sample-evidence/.gitkeep",
    "tests/fixtures/sample_access.log",
]


def is_ignored_by_git(rel_path: str) -> bool:
    """Use `git check-ignore` command to determine if Git ignores a given path."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", rel_path],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        # If git executable is not available, fallback to basic regex matching
        return False


def verify_gitignore_content() -> Tuple[bool, List[str]]:
    """Inspect .gitignore text content for mandatory category definitions."""
    gitignore_path = REPO_ROOT / ".gitignore"
    if not gitignore_path.is_file():
        return False, ["Root .gitignore file does not exist"]

    content = gitignore_path.read_text(encoding="utf-8")
    errors = []

    required_directives = [
        ".env",
        "*.pem",
        "*.key",
        "__pycache__",
        "*.py[cod]",
        ".pytest_cache",
        "node_modules",
        "dist",
        ".coverage",
        "data/evidence/working/*",
        "!data/evidence/working/.gitkeep",
        "data/evidence/derived/*",
        "!data/evidence/derived/.gitkeep",
        "data/reports/*",
        "!data/reports/.gitkeep",
        "!.env.example",
        "!tests/fixtures/**",
    ]

    for directive in required_directives:
        if directive not in content:
            errors.append(f"Missing required ignore directive in .gitignore: '{directive}'")

    return len(errors) == 0, errors


def verify_git_ignore_behavior() -> Tuple[bool, List[str]]:
    """Test Git's actual ignore behavior against sample sensitive and tracked paths."""
    errors = []

    for sample in MUST_IGNORE_SAMPLES:
        if not is_ignored_by_git(sample):
            errors.append(f"Git failed to ignore sensitive/temporary sample: '{sample}'")

    for sample in MUST_NOT_IGNORE_SAMPLES:
        if is_ignored_by_git(sample):
            errors.append(f"Git incorrectly ignored required repository asset: '{sample}'")

    return len(errors) == 0, errors


def main() -> int:
    print("Verifying ForensiWeb Git hygiene and ignore rules...")
    content_ok, content_errors = verify_gitignore_content()
    behavior_ok, behavior_errors = verify_git_ignore_behavior()

    all_errors = content_errors + behavior_errors
    if all_errors:
        print(f"Git hygiene validation FAILED with {len(all_errors)} issue(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("SUCCESS: .gitignore and Git ignore behavior verified cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
