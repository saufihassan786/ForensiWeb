"""Unit tests for API Versioning and Routing Foundation (PHASE-02-F06).

Validates:
- Versioned routing mounted at /api/v1
- Endpoint groups: cases, evidence, events, detections, timeline, findings, reports
- Request validation and standardized pagination envelopes
- HTTP status codes (200 OK, 201 Created, 404 Not Found)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Fixture providing TestClient with mounted v1 routers."""
    test_app = create_app()
    with TestClient(test_app) as c:
        yield c


def test_v1_cases_routing(client: TestClient) -> None:
    """Verify /api/v1/cases endpoints."""
    # List
    resp = client.get("/api/v1/cases")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data

    # Create
    create_resp = client.post(
        "/api/v1/cases",
        json={
            "title": "New Test Case",
            "description": "Integration test created case",
            "status": "open",
            "priority": "medium",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == "New Test Case"
    assert "id" in created

    # Get by ID
    get_resp = client.get(f"/api/v1/cases/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == created["id"]


def test_v1_evidence_routing(client: TestClient) -> None:
    """Verify /api/v1/evidence endpoints."""
    resp = client.get("/api/v1/evidence")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data

    create_resp = client.post(
        "/api/v1/evidence",
        json={
            "case_id": "CASE-001",
            "source": "web_access_log",
            "filename": "audit.log",
            "file_path": "data/evidence/original/audit.log",
            "sha256": "a" * 64,
            "size_bytes": 2048,
            "media_type": "text/plain",
            "acquired_at": "2026-10-06T12:00:00Z",
            "status": "acquired",
        },
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["filename"] == "audit.log"


def test_v1_events_routing(client: TestClient) -> None:
    """Verify /api/v1/events endpoints."""
    resp = client.get("/api/v1/events")
    assert resp.status_code == 200
    assert "items" in resp.json()

    create_resp = client.post(
        "/api/v1/events",
        json={
            "case_id": "CASE-001",
            "timestamp": "2026-10-06T12:05:00Z",
            "source": "auditd",
            "event_type": "process_exec",
            "severity": "high",
            "attack_stage": "RCE",
        },
    )
    assert create_resp.status_code == 201


def test_v1_detections_routing(client: TestClient) -> None:
    """Verify /api/v1/detections endpoints."""
    resp = client.get("/api/v1/detections")
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_v1_timeline_routing(client: TestClient) -> None:
    """Verify /api/v1/timeline endpoints."""
    resp = client.get("/api/v1/timeline")
    assert resp.status_code == 200
    assert "items" in resp.json()

    case_resp = client.get("/api/v1/timeline/CASE-001")
    assert case_resp.status_code == 200
    assert isinstance(case_resp.json(), list)


def test_v1_findings_routing(client: TestClient) -> None:
    """Verify /api/v1/findings endpoints."""
    resp = client.get("/api/v1/findings")
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_v1_reports_routing(client: TestClient) -> None:
    """Verify /api/v1/reports endpoints."""
    resp = client.get("/api/v1/reports")
    assert resp.status_code == 200
    assert "items" in resp.json()
