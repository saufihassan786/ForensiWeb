"""
Test Documentation Structure for ForensiWeb.

Validates PHASE-01-F02: Documentation Structure.
Ensures all required documentation files defined in architecture.md,
rules.md, and task.md exist, are well-formed, and contain appropriate
authoritative guidance.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

REQUIRED_DOC_FILES = [
    "README.md",
    "PRD.md",
    "architecture.md",
    "rules.md",
    "design.md",
    "task.md",
    "threat-model.md",
    "forensic-model.md",
    "implementation-plan.md",
    "testing-strategy.md",
    "adr/README.md",
]


def test_docs_directory_exists():
    """Verify that the docs/ directory exists."""
    assert DOCS_DIR.is_dir(), "docs/ directory is missing"


@pytest.mark.parametrize("doc_rel_path", REQUIRED_DOC_FILES)
def test_required_doc_file_exists_and_non_empty(doc_rel_path):
    """Verify each required document exists, is a file, and has substantial content."""
    doc_path = DOCS_DIR / doc_rel_path
    assert doc_path.is_file(), f"Required documentation file is missing: docs/{doc_rel_path}"
    content = doc_path.read_text(encoding="utf-8")
    assert len(content.strip()) > 200, f"docs/{doc_rel_path} appears empty or trivial"
    # Ensure it starts with a markdown title
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert any(line.startswith("# ") for line in lines), f"docs/{doc_rel_path} lacks a top-level H1 header"


def test_docs_readme_authority_matrix():
    """Verify docs/README.md defines the document authority matrix."""
    readme_path = DOCS_DIR / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    assert "Authority Matrix" in content
    assert "threat-model.md" in content
    assert "forensic-model.md" in content
    assert "implementation-plan.md" in content
    assert "testing-strategy.md" in content


def test_threat_model_content():
    """Verify threat-model.md covers the attack chain, STRIDE, and isolation."""
    tm_path = DOCS_DIR / "threat-model.md"
    content = tm_path.read_text(encoding="utf-8")
    assert "STRIDE" in content
    assert "Log Poisoning" in content
    assert "Privilege Escalation" in content
    assert "Trust Boundaries" in content or "Trust Boundary" in content


def test_forensic_model_content():
    """Verify forensic-model.md covers the Common Event Model and integrity principles."""
    fm_path = DOCS_DIR / "forensic-model.md"
    content = fm_path.read_text(encoding="utf-8")
    assert "Common Event Model" in content
    assert "SHA-256" in content
    assert "Immutability" in content
    assert "Correlation" in content


def test_implementation_plan_content():
    """Verify implementation-plan.md covers the 20 phases and phase-gate model."""
    ip_path = DOCS_DIR / "implementation-plan.md"
    content = ip_path.read_text(encoding="utf-8")
    assert "Phase-Gate" in content
    assert "PHASE 01" in content
    assert "PHASE 20" in content


def test_testing_strategy_content():
    """Verify testing-strategy.md defines the test pyramid and tooling."""
    ts_path = DOCS_DIR / "testing-strategy.md"
    content = ts_path.read_text(encoding="utf-8")
    assert "Pyramid" in content
    assert "Unit Tests" in content
    assert "Integration Tests" in content
    assert "pytest" in content


def test_adr_directory_and_template():
    """Verify docs/adr/ exists with README and ADR template."""
    adr_readme = DOCS_DIR / "adr" / "README.md"
    assert adr_readme.is_file(), "docs/adr/README.md is missing"
    content = adr_readme.read_text(encoding="utf-8")
    assert "ADR-001" in content
    assert "Context & Problem Statement" in content
