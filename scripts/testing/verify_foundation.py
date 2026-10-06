#!/usr/bin/env python3
"""
ForensiWeb Phase 1 Foundation Verification Protocol.

Executes a comprehensive, unified verification across all 8 features of PHASE-01:
- F01: Repository Structure
- F02: Documentation Structure
- F03: Environment Configuration
- F04: Git Hygiene and Ignore Rules
- F05: Development Tooling
- F06: Test Foundation
- F07: Docker Foundation
- F08: Premature Implementation Guard & Quality Gate

Returns exit code 0 if all Phase 1 acceptance criteria are strictly satisfied.
"""

from __future__ import annotations
from pathlib import Path
import subprocess
import sys
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    msg = f"[{status}] {name}"
    if detail and not passed:
        msg += f" - Reason: {detail}"
    print(msg)
    return passed


def verify_f01_repository_structure() -> bool:
    """Verify repository directories and markers."""
    required = [
        "docs", "apps/frontend", "apps/api", "apps/vulnerable-web-app",
        "packages/forensic-engine", "packages/detection-engine", "packages/report-engine",
        "lab/docker", "lab/scenarios", "lab/fixtures", "lab/sample-evidence",
        "data/evidence/original", "data/evidence/working", "data/evidence/derived", "data/reports",
        "tests/integration", "tests/e2e", "tests/fixtures", "tests/regression",
        "scripts/setup", "scripts/development", "scripts/testing", "scripts/deployment"
    ]
    missing = [d for d in required if not (REPO_ROOT / d).is_dir()]
    return check("F01: Repository Structure", len(missing) == 0, f"Missing directories: {missing}")


def verify_f02_documentation_structure() -> bool:
    """Verify documentation catalog and authority files."""
    docs = [
        "README.md", "PRD.md", "architecture.md", "rules.md", "design.md",
        "task.md", "threat-model.md", "forensic-model.md", "implementation-plan.md",
        "testing-strategy.md", "adr/README.md"
    ]
    missing = [doc for doc in docs if not (REPO_ROOT / "docs" / doc).is_file()]
    return check("F02: Documentation Structure", len(missing) == 0, f"Missing docs: {missing}")


def verify_f03_environment_configuration() -> bool:
    """Verify .env.example and validation script."""
    example = REPO_ROOT / ".env.example"
    validator = REPO_ROOT / "scripts" / "setup" / "validate_env.py"
    if not (example.is_file() and validator.is_file()):
        return check("F03: Environment Configuration", False, "Missing .env.example or validate_env.py")

    res = subprocess.run([sys.executable, str(validator), "--check-example"], capture_output=True, text=True)
    return check("F03: Environment Configuration", res.returncode == 0, res.stderr.strip())


def verify_f04_git_hygiene() -> bool:
    """Verify .gitignore, .gitattributes, and hygiene checks."""
    hygiene_script = REPO_ROOT / "scripts" / "testing" / "check_git_hygiene.py"
    if not hygiene_script.is_file():
        return check("F04: Git Hygiene & Ignore Rules", False, "Missing check_git_hygiene.py")

    res = subprocess.run([sys.executable, str(hygiene_script)], capture_output=True, text=True)
    return check("F04: Git Hygiene & Ignore Rules", res.returncode == 0, res.stderr.strip())


def verify_f05_development_tooling() -> bool:
    """Verify Makefile, pyproject.toml, LICENSE, and dev.py CLI."""
    files = ["Makefile", "pyproject.toml", "LICENSE", "scripts/development/dev.py", "scripts/setup/init_env.py"]
    missing = [f for f in files if not (REPO_ROOT / f).is_file()]
    if missing:
        return check("F05: Development Tooling", False, f"Missing tooling files: {missing}")

    dev_cli = REPO_ROOT / "scripts" / "development" / "dev.py"
    res = subprocess.run([sys.executable, str(dev_cli), "--help"], capture_output=True, text=True)
    return check("F05: Development Tooling", res.returncode == 0, "dev.py failed to execute")


def verify_f06_test_foundation() -> bool:
    """Verify conftest.py, fixtures, and run_tests.py."""
    files = [
        "conftest.py",
        "scripts/testing/run_tests.py",
        "tests/fixtures/__init__.py",
        "tests/fixtures/sample_access.log",
        "tests/fixtures/sample_error.log",
        "tests/fixtures/sample_auditd.log",
    ]
    missing = [f for f in files if not (REPO_ROOT / f).is_file()]
    return check("F06: Test Foundation", len(missing) == 0, f"Missing test foundation files: {missing}")


def verify_f07_docker_foundation() -> bool:
    """Verify docker-compose.yml, Dockerfiles, and .dockerignore files."""
    files = [
        "docker-compose.yml",
        ".dockerignore",
        "apps/api/Dockerfile",
        "apps/api/.dockerignore",
        "apps/frontend/Dockerfile",
        "apps/frontend/.dockerignore",
        "apps/vulnerable-web-app/Dockerfile",
        "apps/vulnerable-web-app/.dockerignore",
        "lab/docker/README.md",
    ]
    missing = [f for f in files if not (REPO_ROOT / f).is_file()]
    if missing:
        return check("F07: Docker Foundation", False, f"Missing Docker files: {missing}")

    # Check if docker CLI is available to validate compose config
    import shutil
    if shutil.which("docker"):
        res = subprocess.run(["docker", "compose", "config", "-q"], capture_output=True, text=True, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            return check("F07: Docker Foundation", False, f"docker compose config error: {res.stderr.strip()}")

    return check("F07: Docker Foundation", True)


def verify_f08_scope_and_premature_implementation_guard() -> bool:
    """
    Verify that no business logic or subsequent phase functionality has been
    prematurely implemented during Phase 1.
    """
    prohibited_premature_files = [
        # Phase 2 (Backend logic)
        "apps/api/app/api/routes/cases.py",
        "apps/api/app/services/evidence.py",
        # Phase 4 (Vulnerable app routes)
        "apps/vulnerable-web-app/app/routes/lfi.py",
        # Phase 9 (Detection rules)
        "packages/detection-engine/rules/lfi_rule.py",
        # Phase 14 (Reports)
        "packages/report-engine/generators/pdf_generator.py",
    ]
    premature_existing = [f for f in prohibited_premature_files if (REPO_ROOT / f).is_file()]
    return check("F08: Scope & Premature Implementation Guard", len(premature_existing) == 0, f"Premature files found: {premature_existing}")


def main() -> int:
    print("=================================================================")
    print("ForensiWeb — PHASE 01: Project Foundation Verification Protocol")
    print("=================================================================\n")

    checks = [
        verify_f01_repository_structure,
        verify_f02_documentation_structure,
        verify_f03_environment_configuration,
        verify_f04_git_hygiene,
        verify_f05_development_tooling,
        verify_f06_test_foundation,
        verify_f07_docker_foundation,
        verify_f08_scope_and_premature_implementation_guard,
    ]

    all_passed = True
    for c in checks:
        if not c():
            all_passed = False

    print("\n-----------------------------------------------------------------")
    if all_passed:
        print("PHASE 01 VERIFICATION RESULT: ALL ACCEPTANCE CRITERIA PASSED.")
        print("Phase 01 is eligible for completion sign-off.")
        print("-----------------------------------------------------------------")
        return 0
    else:
        print("PHASE 01 VERIFICATION RESULT: FAILED.")
        print("Resolve outstanding issues before declaring Phase 01 complete.")
        print("-----------------------------------------------------------------")
        return 1


if __name__ == "__main__":
    sys.exit(main())
