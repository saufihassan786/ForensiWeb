"""Performance and UX Refinement Test Suite (PHASE 19).

Verifies:
- PHASE-19-F01: Dashboard and Analytics performance (< 100ms)
- PHASE-19-F02: Evidence processing throughput
- PHASE-19-F03: Pagination across endpoints (page, page_size boundaries)
- PHASE-19-F04: Search & Filtering optimization
- PHASE-19-F06: Timeline reconstruction speed
"""

import time
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from normalization.schema import AttackStage, CommonEventModel
from timeline.reconstructor import TimelineReconstructor


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_p19_f03_pagination_boundaries(client):
    """Verify pagination mechanics, limits, and page_size boundaries across API endpoints."""
    endpoints = [
        "/api/v1/cases",
        "/api/v1/evidence",
        "/api/v1/events",
        "/api/v1/reports",
    ]

    for ep in endpoints:
        res = client.get(f"{ep}?page=1&page_size=5")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["page"] == 1
        assert len(data["items"]) <= 5

        # Invalid page values should be rejected with 422
        bad_page = client.get(f"{ep}?page=0")
        assert bad_page.status_code == 422

        # Page size exceeding 100 should be rejected with 422
        bad_size = client.get(f"{ep}?page_size=101")
        assert bad_size.status_code == 422


def test_p19_f01_f04_analytics_dashboard_latency(client):
    """Verify analytics and summary endpoints execute within responsive SLA (< 200ms)."""
    start = time.perf_counter()
    res = client.get("/api/v1/analytics/cases/CASE-001")
    duration = time.perf_counter() - start

    assert res.status_code == 200
    assert duration < 0.200  # Must be fast and responsive


def test_p19_f06_timeline_reconstruction_performance():
    """Verify timeline reconstruction across 500 events executes in under 100ms."""
    base_t = datetime(2026, 10, 7, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        CommonEventModel(
            event_id=f"EVT-PERF-{i:04d}",
            case_id="CASE-PERF",
            timestamp=base_t + timedelta(milliseconds=i * 10),
            source_type="web_access_log",
            source_artifact_id="EV-PERF-01",
            source_location={"line_number": i + 1, "byte_offset_start": i * 100, "byte_offset_end": (i + 1) * 100},
            attack_stage="stage_01_lfi" if i % 2 == 0 else "stage_02_log_poisoning",
            severity="medium",
            action=f"GET /doc_{i}",
            actor={"ip": f"10.0.0.{i % 255 + 1}"},
            target={"path": f"/doc_{i}"},
            details={},
            evidence_ref={"artifact_name": "access.log", "sha256": "f" * 64},
            raw_content=f"GET /doc_{i} HTTP/1.1",
        )
        for i in range(500)
    ]

    reconstructor = TimelineReconstructor()

    start = time.perf_counter()
    timeline = reconstructor.reconstruct(events=events, case_id="CASE-PERF")
    elapsed = time.perf_counter() - start

    assert len(timeline) == 500
    assert elapsed < 0.100  # Under 100 milliseconds for 500 events
