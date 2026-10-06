"""
Test Repository Structure for ForensiWeb.

Validates that the repository structure adheres strictly to
the directory layout specified in `docs/architecture.md` (Section 27).
"""

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRECTORIES = [
    # docs
    "docs",
    # apps
    "apps/frontend/public",
    "apps/frontend/src/components",
    "apps/frontend/src/pages",
    "apps/frontend/src/layouts",
    "apps/frontend/src/hooks",
    "apps/frontend/src/services",
    "apps/frontend/src/types",
    "apps/frontend/src/utils",
    "apps/api/app/api/routes",
    "apps/api/app/core",
    "apps/api/app/models",
    "apps/api/app/schemas",
    "apps/api/app/services",
    "apps/api/app/repositories",
    "apps/api/tests",
    "apps/api/alembic",
    "apps/vulnerable-web-app/app/routes",
    "apps/vulnerable-web-app/app/services",
    "apps/vulnerable-web-app/app/templates",
    "apps/vulnerable-web-app/app/static",
    "apps/vulnerable-web-app/tests",
    # packages
    "packages/forensic-engine/parsers",
    "packages/forensic-engine/normalization",
    "packages/forensic-engine/correlation",
    "packages/forensic-engine/timeline",
    "packages/forensic-engine/evidence",
    "packages/forensic-engine/tests",
    "packages/detection-engine/rules",
    "packages/detection-engine/models",
    "packages/detection-engine/evaluator",
    "packages/detection-engine/tests",
    "packages/report-engine/templates",
    "packages/report-engine/generators",
    "packages/report-engine/tests",
    # lab
    "lab/docker",
    "lab/scenarios",
    "lab/fixtures",
    "lab/sample-evidence",
    "lab/scripts",
    "lab/reset",
    # data
    "data/evidence/original",
    "data/evidence/working",
    "data/evidence/derived",
    "data/reports",
    # tests
    "tests/integration",
    "tests/e2e",
    "tests/fixtures",
    "tests/regression",
    # scripts
    "scripts/setup",
    "scripts/development",
    "scripts/testing",
    "scripts/deployment",
]

EXPECTED_DOCUMENTS = [
    "docs/PRD.md",
    "docs/architecture.md",
    "docs/design.md",
    "docs/rules.md",
    "docs/task.md",
    "docs/README.md",
    "docs/threat-model.md",
    "docs/forensic-model.md",
    "docs/implementation-plan.md",
    "docs/testing-strategy.md",
]


def test_required_directories_exist():
    """Verify all directories defined in architecture.md section 27 exist."""
    missing_dirs = []
    for dir_rel_path in REQUIRED_DIRECTORIES:
        full_path = REPO_ROOT / dir_rel_path
        if not full_path.is_dir():
            missing_dirs.append(dir_rel_path)
    assert not missing_dirs, f"Missing required directories: {missing_dirs}"


def test_core_docs_exist():
    """Verify all 5 core project documents exist in docs/."""
    missing_docs = []
    for doc_rel_path in EXPECTED_DOCUMENTS:
        full_path = REPO_ROOT / doc_rel_path
        if not full_path.is_file():
            missing_docs.append(doc_rel_path)
    assert not missing_docs, f"Missing core docs: {missing_docs}"


def test_readme_exists():
    """Verify root README.md exists and is not empty."""
    readme_path = REPO_ROOT / "README.md"
    assert readme_path.is_file(), "Root README.md is missing"
    assert readme_path.stat().st_size > 0, "Root README.md is empty"


def test_env_example_file_exists():
    """Verify root .env.example exists and is not empty."""
    env_example_path = REPO_ROOT / ".env.example"
    assert env_example_path.is_file(), "Root .env.example is missing"
    assert env_example_path.stat().st_size > 0, "Root .env.example is empty"


def test_gitignore_file_exists():
    """Verify root .gitignore exists and is not empty."""
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.is_file(), "Root .gitignore is missing"
    assert gitignore_path.stat().st_size > 0, "Root .gitignore is empty"


def test_license_file_exists():
    """Verify root LICENSE exists and is not empty."""
    license_path = REPO_ROOT / "LICENSE"
    assert license_path.is_file(), "Root LICENSE is missing"
    assert license_path.stat().st_size > 0, "Root LICENSE is empty"


def test_makefile_exists():
    """Verify root Makefile exists and is not empty."""
    makefile_path = REPO_ROOT / "Makefile"
    assert makefile_path.is_file(), "Root Makefile is missing"
    assert makefile_path.stat().st_size > 0, "Root Makefile is empty"


def test_pyproject_toml_exists():
    """Verify root pyproject.toml exists and is not empty."""
    pyproject_path = REPO_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "Root pyproject.toml is missing"
    assert pyproject_path.stat().st_size > 0, "Root pyproject.toml is empty"


def test_conftest_exists():
    """Verify root conftest.py exists and is not empty."""
    conftest_path = REPO_ROOT / "conftest.py"
    assert conftest_path.is_file(), "Root conftest.py is missing"
    assert conftest_path.stat().st_size > 0, "Root conftest.py is empty"


def test_docker_compose_exists():
    """Verify root docker-compose.yml exists and is not empty."""
    compose_path = REPO_ROOT / "docker-compose.yml"
    assert compose_path.is_file(), "Root docker-compose.yml is missing"
    assert compose_path.stat().st_size > 0, "Root docker-compose.yml is empty"


def test_dockerignore_exists():
    """Verify root .dockerignore exists and is not empty."""
    dockerignore_path = REPO_ROOT / ".dockerignore"
    assert dockerignore_path.is_file(), "Root .dockerignore is missing"
    assert dockerignore_path.stat().st_size > 0, "Root .dockerignore is empty"





