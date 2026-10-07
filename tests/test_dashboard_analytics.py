"""Unit and Integration Tests for Phase 13: Dashboard & Analytics."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.analytics_service import AnalyticsService
from app.services.case_service import CaseService
from app.services.finding_service import FindingService
from app.services.timeline_service import TimelineService
from evidence.storage import EvidenceStorage
from normalization.schema import AttackStage, CommonEventModel
from normalization.store import NormalizedEventStore


@pytest.fixture
def analytics_test_env(tmp_path: Path):
    storage = EvidenceStorage(root_dir=tmp_path / "evidence")
    event_store = NormalizedEventStore(storage=storage)
    case_service = CaseService()
    finding_service = FindingService()
    timeline_service = TimelineService(event_store=event_store)

    service = AnalyticsService(
        case_service=case_service,
        finding_service=finding_service,
        timeline_service=timeline_service,
        storage=storage,
        event_store=event_store,
    )
    return {
        "service": service,
        "storage": storage,
        "event_store": event_store,
        "case_service": case_service,
        "finding_service": finding_service,
        "timeline_service": timeline_service,
        "tmp_path": tmp_path,
    }


def test_p13_f01_f05_metric_aggregation_accuracy(analytics_test_env):
    """Verify accuracy of case overview, evidence, event, detection, and finding metrics."""
    service: AnalyticsService = analytics_test_env["service"]
    import asyncio

    analytics = asyncio.run(service.compute_dashboard_analytics("CASE-001"))

    # Case overview
    assert analytics.case_overview.case_id == "CASE-001"
    assert analytics.case_overview.status in ["open", "investigating"]

    # Evidence metrics
    assert analytics.evidence_metrics.total_artifacts >= 1
    assert analytics.evidence_metrics.verified_hashes >= 1
    assert analytics.evidence_metrics.tampered_count == 0

    # Event metrics
    assert analytics.event_metrics.total_events >= 1
    assert len(analytics.event_metrics.by_source_type) >= 1

    # Detection metrics
    assert analytics.detection_metrics.total_alerts >= 1
    assert "critical" in analytics.detection_metrics.by_severity

    # Finding metrics
    assert analytics.finding_metrics.total_findings >= 1
    assert "critical" in analytics.finding_metrics.by_severity


def test_p13_f06_event_trends_temporal_bucketing(analytics_test_env):
    """Verify temporal event trend histogram grouping."""
    service: AnalyticsService = analytics_test_env["service"]
    event_store: NormalizedEventStore = analytics_test_env["event_store"]
    import asyncio

    case_id = "CASE-TRENDS"
    base_t = datetime(2026, 10, 7, 10, 0, 0, tzinfo=timezone.utc)

    # Ingest 3 events across 2 different hours
    ev1 = CommonEventModel(
        event_id="EVT-T1", case_id=case_id, timestamp=base_t,
        source_type="web_access_log", source_artifact_id="EV-1",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 50},
        attack_stage="stage_01_lfi", severity="high", action="GET /",
        actor={}, target={}, details={}, evidence_ref={"artifact_name": "access.log", "sha256": "0" * 64},
        raw_content="GET /",
    )
    ev2 = CommonEventModel(
        event_id="EVT-T2", case_id=case_id, timestamp=base_t + timedelta(minutes=15),
        source_type="web_access_log", source_artifact_id="EV-1",
        source_location={"line_number": 2, "byte_offset_start": 51, "byte_offset_end": 100},
        attack_stage="stage_01_lfi", severity="high", action="GET /view",
        actor={}, target={}, details={}, evidence_ref={"artifact_name": "access.log", "sha256": "0" * 64},
        raw_content="GET /view",
    )
    ev3 = CommonEventModel(
        event_id="EVT-T3", case_id=case_id, timestamp=base_t + timedelta(hours=2),
        source_type="web_access_log", source_artifact_id="EV-1",
        source_location={"line_number": 3, "byte_offset_start": 101, "byte_offset_end": 150},
        attack_stage="stage_03_rce", severity="critical", action="GET /cmd",
        actor={}, target={}, details={}, evidence_ref={"artifact_name": "access.log", "sha256": "0" * 64},
        raw_content="GET /cmd",
    )
    event_store.save_events(case_id, [ev1, ev2, ev3])

    analytics = asyncio.run(service.compute_dashboard_analytics(case_id))
    assert len(analytics.event_trends) == 2
    assert analytics.event_trends[0].count == 2
    assert analytics.event_trends[1].count == 1


def test_p13_f07_f08_severity_distribution_and_stage_analytics(analytics_test_env):
    """Verify percentage calculations and attack stage progression."""
    service: AnalyticsService = analytics_test_env["service"]
    import asyncio

    analytics = asyncio.run(service.compute_dashboard_analytics("CASE-001"))

    # Severity distribution
    percentages = analytics.severity_distribution.percentages
    assert "critical" in percentages
    assert "high" in percentages
    assert sum(percentages.values()) >= 99.0  # ~100% rounding check

    # Stage analytics
    stage_info = analytics.attack_stage_analytics
    assert len(stage_info.stages_detected) >= 1
    assert stage_info.sequence_completion_percent > 0.0


def test_p13_f10_explainable_risk_score_calculation(analytics_test_env):
    """Verify deterministic explainable risk summary and scoring factors."""
    service: AnalyticsService = analytics_test_env["service"]

    # 1. High risk scenario (Privilege escalation + critical detections)
    risk_high = service.calculate_explainable_risk(
        case_id="CASE-HIGH",
        highest_stage="PRIVILEGE_ESCALATION",
        critical_detections=2,
        high_detections=1,
        unmitigated_findings=1,
        has_tampering=False,
    )
    assert risk_high.risk_score >= 80
    assert risk_high.risk_level == "CRITICAL"
    factor_names = [f.factor for f in risk_high.explanation_factors]
    assert "ATTACK_STAGE_PROGRESSION" in factor_names
    assert "CRITICAL_DETECTIONS" in factor_names

    # 2. Minimal risk scenario (Recon only, no criticals)
    risk_low = service.calculate_explainable_risk(
        case_id="CASE-LOW",
        highest_stage="RECON",
        critical_detections=0,
        high_detections=0,
        unmitigated_findings=0,
        has_tampering=False,
    )
    assert risk_low.risk_score <= 20
    assert risk_low.risk_level in ["LOW", "MINIMAL"]


def test_p13_api_analytics_endpoints():
    """Verify API integration for dashboard analytics and risk summary."""
    app = create_app()
    client = TestClient(app)

    # 1. Full Dashboard Analytics
    resp = client.get("/api/v1/analytics/cases/CASE-001")
    assert resp.status_code == 200
    data = resp.json()
    assert "case_overview" in data
    assert "evidence_metrics" in data
    assert "event_metrics" in data
    assert "detection_metrics" in data
    assert "finding_metrics" in data
    assert "risk_summary" in data

    # 2. Dedicated Risk Summary endpoint
    resp_risk = client.get("/api/v1/analytics/cases/CASE-001/risk-summary")
    assert resp_risk.status_code == 200
    risk_data = resp_risk.json()
    assert risk_data["case_id"] == "CASE-001"
    assert "risk_score" in risk_data
    assert "risk_level" in risk_data
    assert len(risk_data["explanation_factors"]) >= 1
