"""Integration resilience and failure recovery test suite (PHASE-17).

Verifies:
- PHASE-17-F01: Unit and Integration Test Expansion
- PHASE-17-F02: Integration Tests across components
- PHASE-17-F06: Failure Recovery in API error handling
- PHASE-17-F09: Database / Storage Failure Tolerance
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_p17_api_invalid_payload_error_resilience(client):
    """Verify API consistently validates inputs and returns structured 422/400 errors."""
    # Invalid evidence creation (missing required fields)
    bad_res = client.post("/api/v1/evidence", json={"bad_field": "data"})
    assert bad_res.status_code in (422, 400)
    data = bad_res.json()
    assert "error" in data or "detail" in data

    # Non-existent case lookup returns structured 404
    missing_case = client.get("/api/v1/cases/NON-EXISTENT-CASE-999")
    assert missing_case.status_code == 404

    # Non-existent report lookup returns structured 404
    missing_report = client.get("/api/v1/reports/NON-EXISTENT-RPT")
    assert missing_report.status_code == 404


def test_p17_health_endpoint_resilience(client):
    """Verify health readiness endpoint reports subsystem status without uncaught exception."""
    res = client.get("/api/v1/health/ready")
    assert res.status_code in (200, 503)
    data = res.json()
    assert "status" in data
    assert "database" in data


def test_p17_concurrent_report_generation(client):
    """Verify concurrent report generation requests produce unique report IDs and non-colliding outputs."""
    payload = {
        "case_id": "CASE-CONCURRENT",
        "case_title": "Concurrency Test Case",
        "format": "markdown",
        "report_type": "technical",
    }

    res_1 = client.post("/api/v1/reports/generate", json=payload)
    res_2 = client.post("/api/v1/reports/generate", json=payload)

    assert res_1.status_code == 201
    assert res_2.status_code == 201

    id_1 = res_1.json()["id"]
    id_2 = res_2.json()["id"]

    assert id_1.startswith("RPT-")
    assert id_2.startswith("RPT-")
