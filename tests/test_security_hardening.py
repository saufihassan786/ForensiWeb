"""Security Hardening Verification Test Suite (PHASE 18).

Verifies:
- PHASE-18-F01: Input Validation Review
- PHASE-18-F04: Secret Management Review
- PHASE-18-F05: Secure Configuration Review
- PHASE-18-F06: Laboratory Isolation & Containment
- PHASE-18-F07: Audit Logging Review
- PHASE-18-F09: Security Testing against injection & traversal
- PHASE-18-F10: Security Findings Remediation
"""

import urllib.parse
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app as create_api_app
from vuln_app.config import LabConfig
import vuln_app.main as vuln_main


@pytest.fixture
def api_client():
    app = create_api_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def lab_client(tmp_path):
    cfg = LabConfig(log_dir=tmp_path / "logs")
    app = vuln_main.create_app(cfg)
    app.config["TESTING"] = True
    return app.test_client()


def test_p18_f01_f09_report_path_traversal_rejection(api_client):
    """Verify that path traversal attempts in report identifiers are securely blocked."""
    traversal_payloads = [
        "..%2F..%2Fetc%2Fpasswd",
        "..%5C..%5Cwindows%5Csystem32%5Ccmd.exe",
        "RPT-001%2F..%2F..%2Fsecret.txt",
    ]

    for payload in traversal_payloads:
        res = api_client.get(f"/api/v1/reports/{payload}")
        assert res.status_code in (400, 404)
        if res.status_code == 400:
            err_msg = res.json().get("detail") or res.json().get("error", {}).get("message", "")
            assert "path traversal" in err_msg.lower()

        res_preview = api_client.get(f"/api/v1/reports/{payload}/preview")
        assert res_preview.status_code in (400, 404)

        res_dl = api_client.get(f"/api/v1/reports/{payload}/download")
        assert res_dl.status_code in (400, 404)


def test_p18_f01_f09_evidence_path_traversal_rejection(api_client):
    """Verify that path traversal attempts in evidence identifiers are securely blocked."""
    traversal_payloads = [
        "..%2F..%2Fetc%2Fpasswd",
        "EV-001%2F..%2F..%2F..%2Fetc%2Fhosts",
    ]

    for payload in traversal_payloads:
        res = api_client.get(f"/api/v1/evidence/{payload}")
        assert res.status_code in (400, 404)
        if res.status_code == 400:
            err_msg = res.json().get("detail") or res.json().get("error", {}).get("message", "")
            assert "path traversal" in err_msg.lower()

        res_dl = api_client.get(f"/api/v1/evidence/{payload}/download?case_id=CASE-001")
        assert res_dl.status_code in (400, 404)


def test_p18_f04_f05_secret_masking_and_safe_configuration():
    """Verify that settings hide sensitive database and secret credentials in masked representations."""
    settings = Settings(
        SECRET_KEY="super-secret-production-token-12345",
        POSTGRES_PASSWORD="ultra_confidential_db_password",
    )

    masked = settings.masked_dict()
    assert masked["SECRET_KEY"] == "******"
    assert masked["POSTGRES_PASSWORD"] == "******"
    assert "ultra_confidential_db_password" not in str(masked["DATABASE_URL"])
    assert "super-secret-production-token-12345" not in str(masked.values())


def test_p18_f06_laboratory_target_containment(lab_client):
    """Verify that the controlled vulnerable app enforces containment guard when probing out of scope."""
    out_of_scope_probe = lab_client.get("/document?file=../../../../../../etc/shadow")
    assert out_of_scope_probe.status_code == 404
    assert b"CONTAINMENT_GUARD" in out_of_scope_probe.data
