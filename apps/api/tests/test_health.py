"""Unit tests for Health and Readiness Observability Endpoints (PHASE-02-F07).

Validates:
- Liveness probe (/health/live and /api/v1/health/live) returns 200 OK
- Readiness probe (/health/ready) returns correct status code and dependency checks
- Overall system health summary (/health)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Fixture providing TestClient for health testing."""
    test_app = create_app()
    with TestClient(test_app) as c:
        yield c


def test_liveness_endpoints(client: TestClient) -> None:
    """Verify liveness probe returns alive status."""
    resp1 = client.get("/health/live")
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "alive"

    resp2 = client.get("/api/v1/health/live")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "alive"


def test_readiness_healthy_state(client: TestClient) -> None:
    """Verify readiness returns 200 when database and storage checks succeed."""
    with patch("app.api.v1.endpoints.health.check_database_health", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = True

        resp = client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"


def test_readiness_unhealthy_state(client: TestClient) -> None:
    """Verify readiness returns 503 Service Unavailable when database check fails."""
    with patch("app.api.v1.endpoints.health.check_database_health", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = False

        resp = client.get("/health/ready")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "unready"
        assert data["database"] == "disconnected"


def test_system_health_summary(client: TestClient) -> None:
    """Verify overall system health report returns operational structure."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "subsystems" in data
    assert "api" in data["subsystems"]
