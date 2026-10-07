"""Verification Test Suite for PHASE 15 — Mitigation & Verification.

Verifies:
- PHASE-15-F01: Mitigation Recommendations
- PHASE-15-F02: Secure Configuration State
- PHASE-15-F03: Before-State Capture
- PHASE-15-F04: Controlled Scenario Reproduction
- PHASE-15-F05: Mitigation Application
- PHASE-15-F06: After-State Capture
- PHASE-15-F07: Before/After Comparison
- PHASE-15-F08: Verification Evidence
"""

import json
import pytest
from fastapi.testclient import TestClient
from flask.testing import FlaskClient

from app.main import create_app as create_api_app
import vuln_app.main as vuln_main
from vuln_app.config import LabConfig


@pytest.fixture
def api_client():
    app = create_api_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def lab_app(tmp_path):
    cfg = LabConfig(log_dir=tmp_path / "logs")
    app = vuln_main.create_app(cfg)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def lab_client(lab_app):
    return lab_app.test_client()


def test_p15_f01_mitigation_recommendations(api_client):
    """Verify retrieval of structured mitigation recommendations."""
    res = api_client.get("/api/v1/mitigation/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5

    stages = [m["stage"] for m in data]
    assert "stage_01_lfi" in stages
    assert "stage_02_log_poisoning" in stages
    assert "stage_03_rce" in stages
    assert "stage_04_web_shell" in stages
    assert "stage_06_priv_esc" in stages

    # Check stage filtering
    filter_res = api_client.get("/api/v1/mitigation/recommendations?stage=stage_01_lfi")
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert len(filtered) == 1
    assert "verification_criteria" in filtered[0]


def test_p15_f02_to_f06_before_and_after_telemetry(lab_client):
    """Verify baseline attack execution vs mitigated blocked execution."""
    # 1. Baseline Run (Without Mitigations)
    lab_client.post("/api/reset")
    lfi_res = lab_client.get("/document?file=../../logs/access.log")
    assert lfi_res.status_code == 200

    shell_res = lab_client.get("/shell?cmd=whoami")
    assert shell_res.status_code == 200
    assert shell_res.get_json()["user"] == "labuser"

    privesc_res = lab_client.post("/privesc/run-backup")
    assert privesc_res.status_code == 200
    assert privesc_res.get_json()["effective_uid"] == 0  # Elevated root

    # 2. Apply Mitigation (PHASE-15-F05)
    enable_res = lab_client.post("/api/mitigation/enable")
    assert enable_res.status_code == 200
    assert enable_res.get_json()["is_mitigated"] is True

    status_res = lab_client.get("/api/mitigation/status")
    assert status_res.status_code == 200
    assert "path_whitelist_validation" in status_res.get_json()["active_controls"]

    # 3. Repeat Scenario in Mitigated State (PHASE-15-F06)
    lfi_mit = lab_client.get("/document?file=../../logs/access.log")
    assert lfi_mit.status_code == 403
    assert b"SECURITY_MITIGATION_ACTIVE" in lfi_mit.data

    shell_mit = lab_client.get("/shell?cmd=whoami")
    assert shell_mit.status_code == 403
    assert shell_mit.get_json()["status"] == "blocked"

    beacon_mit = lab_client.post("/post-exploitation/meterpreter")
    assert beacon_mit.status_code == 403
    assert beacon_mit.get_json()["status"] == "blocked"

    privesc_mit = lab_client.post("/privesc/run-backup")
    assert privesc_mit.status_code == 200
    assert privesc_mit.get_json()["effective_uid"] == 1000  # Non-root user!
    assert privesc_mit.get_json()["status"] == "mitigated"


def test_p15_f07_f08_comparison_and_verification_evidence(api_client):
    """Verify quantitative before/after comparison and verification evidence artifact."""
    payload = {
        "case_id": "CASE-001",
        "baseline_run": {
            "completed_stages": ["S1", "S2", "S3", "S4", "S5"],
            "critical_detections_count": 4,
            "root_privilege_achieved": True,
            "lfi_status": 200,
            "web_shell_accessible": True,
            "privesc_effective_uid": 0,
        },
        "mitigated_run": {
            "completed_stages": [],
            "critical_detections_count": 0,
            "root_privilege_achieved": False,
            "lfi_status": 403,
            "web_shell_accessible": False,
            "privesc_effective_uid": 1000,
        },
    }

    comp_res = api_client.post("/api/v1/mitigation/compare", json=payload)
    assert comp_res.status_code == 200
    comparison = comp_res.json()
    assert comparison["efficacy_percentage"] == 100.0
    assert comparison["root_compromise_prevented"] is True
    assert "attack_chain_broken_at" in comparison
    assert len(comparison["blocked_attack_vectors"]) >= 4

    # Generate Verification Evidence Artifact (PHASE-15-F08)
    verif_res = api_client.post("/api/v1/mitigation/verify", json=payload)
    assert verif_res.status_code == 201
    verif_data = verif_res.json()
    assert verif_data["verification_id"].startswith("VERIF-CASE-001-")
    assert verif_data["status"] == "VERIFIED_REMEDIATED"
    assert len(verif_data["sha256"]) == 64
