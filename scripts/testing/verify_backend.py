"""ForensiWeb — Phase 02 Backend Verification Protocol.

Validates that all 8 features of Phase 2 are implemented according to
architecture.md and rules.md before Phase 2 completion sign-off:
- F01: Backend Application Bootstrap
- F02: Configuration System
- F03: Database Connection
- F04: Migration Framework
- F05: Core Data Models
- F06: API Versioning and Routing
- F07: Health and Readiness Checks
- F08: Error Handling
- F09: Scope and Premature Implementation Guard
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    msg = f"[{status}] {name}"
    if details and not condition:
        msg += f" -> {details}"
    print(msg)
    return condition


def verify_f01_bootstrap() -> bool:
    try:
        from app.main import app, create_app, lifespan
        inst = create_app()
        return check("F01: Backend Application Bootstrap", inst is not None and app.title == "ForensiWeb API")
    except Exception as exc:
        return check("F01: Backend Application Bootstrap", False, str(exc))


def verify_f02_configuration() -> bool:
    try:
        from app.core.config import Settings, get_settings
        cfg = get_settings()
        masked = cfg.masked_dict()
        is_masked = masked.get("SECRET_KEY") == "******" and "***:***@" in masked.get("DATABASE_URL", "")
        return check("F02: Configuration System", is_masked and cfg.API_PORT == 8000)
    except Exception as exc:
        return check("F02: Configuration System", False, str(exc))


def verify_f03_database_connection() -> bool:
    try:
        from app.core.database import Base, check_database_health, get_sync_engine
        engine = get_sync_engine("sqlite:///:memory:")
        return check("F03: Database Connection", engine is not None and Base.metadata.naming_convention is not None)
    except Exception as exc:
        return check("F03: Database Connection", False, str(exc))


def verify_f04_migration_framework() -> bool:
    alembic_ini = REPO_ROOT / "apps" / "api" / "alembic.ini"
    alembic_env = REPO_ROOT / "apps" / "api" / "alembic" / "env.py"
    versions_dir = REPO_ROOT / "apps" / "api" / "alembic" / "versions"
    rev_files = list(versions_dir.glob("*.py")) if versions_dir.is_dir() else []
    return check(
        "F04: Migration Framework",
        alembic_ini.is_file() and alembic_env.is_file() and len(rev_files) >= 1,
        f"Alembic setup missing: ini={alembic_ini.is_file()}, env={alembic_env.is_file()}, revs={len(rev_files)}",
    )


def verify_f05_core_data_models() -> bool:
    try:
        from app.core.database import Base
        import app.models  # noqa: F401
        expected_tables = {
            "cases",
            "evidence",
            "events",
            "detections",
            "timeline_entries",
            "findings",
            "reports",
            "audit_logs",
        }
        present_tables = set(Base.metadata.tables.keys())
        missing = expected_tables - present_tables
        return check("F05: Core Data Models", len(missing) == 0, f"Missing tables: {missing}")
    except Exception as exc:
        return check("F05: Core Data Models", False, str(exc))


def verify_f06_api_versioning_and_routing() -> bool:
    try:
        from app.main import create_app
        app_inst = create_app()
        paths = list(app_inst.openapi().get("paths", {}).keys())
        expected_route_prefixes = [
            "/api/v1/cases",
            "/api/v1/evidence",
            "/api/v1/events",
            "/api/v1/detections",
            "/api/v1/timeline",
            "/api/v1/findings",
            "/api/v1/reports",
        ]
        has_all = all(any(p.startswith(prefix) for p in paths) for prefix in expected_route_prefixes)
        return check("F06: API Versioning and Routing", has_all, f"Available OpenAPI paths: {paths}")
    except Exception as exc:
        return check("F06: API Versioning and Routing", False, str(exc))


def verify_f07_health_checks() -> bool:
    try:
        from app.main import create_app
        from fastapi.testclient import TestClient
        client = TestClient(create_app())
        live_resp = client.get("/health/live")
        health_resp = client.get("/health")
        return check(
            "F07: Health and Readiness Checks",
            live_resp.status_code == 200 and health_resp.status_code == 200,
        )
    except Exception as exc:
        return check("F07: Health and Readiness Checks", False, str(exc))


def verify_f08_error_handling() -> bool:
    try:
        from app.main import create_app
        from fastapi.testclient import TestClient
        client = TestClient(create_app())
        resp = client.get("/api/v1/cases/non-existent-case-uuid")
        data = resp.json()
        has_format = "error" in data and "code" in data["error"] and "request_id" in data["error"]
        has_header = "X-Request-ID" in resp.headers
        return check("F08: Error Handling", resp.status_code == 404 and has_format and has_header)
    except Exception as exc:
        return check("F08: Error Handling", False, str(exc))


def verify_scope_and_premature_guard() -> bool:
    # Phase 2 must not implement future phase logic
    prohibited_files = [
        # Phase 4 (Vulnerable web application routes)
        "apps/vulnerable-web-app/app/routes/lfi.py",
        # Phase 5 (Evidence collection scripts)
        "lab/scripts/collect_evidence.py",
        # Phase 9 (Detection rules)
        "packages/detection-engine/rules/lfi_rule.py",
        # Phase 14 (PDF report compilation)
        "packages/report-engine/generators/pdf_generator.py",
    ]
    premature_existing = [f for f in prohibited_files if (REPO_ROOT / f).is_file()]
    return check("F09: Premature Implementation Guard", len(premature_existing) == 0, f"Found: {premature_existing}")


def main() -> int:
    print("=================================================================")
    print("ForensiWeb — PHASE 02: Backend Foundation Verification Protocol")
    print("=================================================================\n")

    checks = [
        verify_f01_bootstrap,
        verify_f02_configuration,
        verify_f03_database_connection,
        verify_f04_migration_framework,
        verify_f05_core_data_models,
        verify_f06_api_versioning_and_routing,
        verify_f07_health_checks,
        verify_f08_error_handling,
        verify_scope_and_premature_guard,
    ]

    all_passed = True
    for c in checks:
        if not c():
            all_passed = False

    print("\n-----------------------------------------------------------------")
    if all_passed:
        print("PHASE 02 VERIFICATION RESULT: ALL ACCEPTANCE CRITERIA PASSED.")
        print("Phase 02 is eligible for completion sign-off.")
        print("-----------------------------------------------------------------")
        return 0
    else:
        print("PHASE 02 VERIFICATION RESULT: FAILED.")
        print("-----------------------------------------------------------------")
        return 1


if __name__ == "__main__":
    sys.exit(main())
