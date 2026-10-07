"""Verification Test Suite for PHASE 10 — Event Correlation Engine.

Verifies:
- PHASE-10-F01: Correlation Model (CorrelationEdge, CorrelationGraph)
- PHASE-10-F02: Temporal Correlation (proximity calculation and boundaries)
- PHASE-10-F03: Source Correlation (actor IP and source continuity)
- PHASE-10-F04: Process/Lineage & Resource Correlation (PPID -> PID, resource continuity)
- PHASE-10-F05: Attack-Stage Correlation (causal chain sequencing)
- PHASE-10-F06: Confidence Model (Definitive, High, Probable, Low scoring tiers)
- PHASE-10-F07: Correlation Explanation (Explainable contributing evidence)
- Uncertainty Verification: Low-confidence events classified as Inferred
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import pytest

from correlation.engine import CorrelationEngine
from correlation.models import (
    ConfidenceLevel,
    EvidenceClassification,
)
from normalization.schema import AttackStage, CommonEventModel, SeverityLevel


@pytest.fixture
def correlation_engine() -> CorrelationEngine:
    return CorrelationEngine(max_temporal_window_seconds=60.0)


def create_event(
    event_id: str,
    timestamp: datetime,
    stage: AttackStage,
    ip: str = "172.28.0.5",
    action: str = "http_get",
    pid: int | None = None,
    ppid: int | None = None,
    comm: str | None = None,
    target_name: str | None = None,
) -> CommonEventModel:
    actor = {"ip": ip}
    if pid is not None:
        actor["pid"] = pid
    if ppid is not None:
        actor["ppid"] = ppid
    if comm is not None:
        actor["comm"] = comm

    target = {}
    if target_name is not None:
        target["target_name"] = target_name

    return CommonEventModel(
        event_id=event_id,
        case_id="CASE-CORR-01",
        timestamp=timestamp,
        source_type="web_access_log" if pid is None else "system_audit",
        source_artifact_id="EV-SRC",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 50},
        attack_stage=stage,
        severity=SeverityLevel.HIGH,
        action=action,
        actor=actor,
        target=target,
        details={},
        evidence_ref={"artifact_name": "log.txt", "sha256": "1" * 64},
        raw_content="sample raw log line",
    )


# ==============================================================================
# PHASE-10-F04: Process Lineage Correlation (Definitive 0.95 / Observed)
# ==============================================================================

def test_p10_f04_process_lineage_definitive(correlation_engine: CorrelationEngine):
    """Verify PID to PPID matching yields Definitive confidence and Observed classification."""
    t0 = datetime(2026, 10, 6, 14, 32, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=5.0)

    # Event 1: Web worker process with PID 1420
    ev1 = create_event("EVT-P1", t0, AttackStage.STAGE_03_RCE, pid=1420, comm="gunicorn")
    # Event 2: Spawned child shell with PPID 1420, PID 2105
    ev2 = create_event("EVT-P2", t1, AttackStage.STAGE_03_RCE, pid=2105, ppid=1420, comm="sh")

    edge = correlation_engine.evaluate_pair(ev1, ev2)
    assert edge is not None
    assert edge.correlation_type == "process_lineage"
    assert edge.confidence_score >= 0.90
    assert edge.confidence_level == ConfidenceLevel.DEFINITIVE
    assert edge.classification == EvidenceClassification.OBSERVED
    assert "Definitive process lineage" in edge.explanation
    assert edge.attributes_matched["parent_pid"] == 1420
    assert edge.attributes_matched["child_pid"] == 2105


# ==============================================================================
# PHASE-10-F04: Resource Continuity (High 0.88 / Correlated)
# ==============================================================================

def test_p10_f04_resource_continuity_high(correlation_engine: CorrelationEngine):
    """Verify Log Poisoning -> RCE on same resource from same IP yields High confidence."""
    t0 = datetime(2026, 10, 6, 14, 31, 35, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=2.0)

    ev_poison = create_event("EVT-POISON", t0, AttackStage.STAGE_02_LOG_POISONING, ip="172.28.0.5")
    ev_rce = create_event("EVT-RCE", t1, AttackStage.STAGE_03_RCE, ip="172.28.0.5")

    edge = correlation_engine.evaluate_pair(ev_poison, ev_rce)
    assert edge is not None
    assert edge.correlation_type == "resource_continuity"
    assert edge.confidence_score >= 0.75
    assert edge.confidence_level == ConfidenceLevel.HIGH
    assert edge.classification == EvidenceClassification.CORRELATED
    assert "High resource continuity" in edge.explanation
    assert len(edge.contributing_evidence) == 2


# ==============================================================================
# PHASE-10-F02 & F03: Temporal & Source IP Continuity
# ==============================================================================

def test_p10_f02_f03_temporal_and_source_correlation(correlation_engine: CorrelationEngine):
    """Verify same IP advancing across attack stages within 5 seconds."""
    t0 = datetime(2026, 10, 6, 14, 30, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=3.0)

    ev_lfi = create_event("EVT-LFI", t0, AttackStage.STAGE_01_LFI, ip="172.28.0.5")
    ev_poison = create_event("EVT-POISON2", t1, AttackStage.STAGE_02_LOG_POISONING, ip="172.28.0.5")

    edge = correlation_engine.evaluate_pair(ev_lfi, ev_poison)
    assert edge is not None
    assert edge.correlation_type == "attack_stage_sequence"
    assert edge.confidence_score >= 0.75
    assert edge.attributes_matched["actor_ip"] == "172.28.0.5"


def test_p10_f02_temporal_boundary_exceeded(correlation_engine: CorrelationEngine):
    """Verify events outside the temporal window (e.g., > 60s) are not correlated."""
    t0 = datetime(2026, 10, 6, 14, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=120.0)  # 2 minutes later

    ev1 = create_event("EVT-OLD", t0, AttackStage.STAGE_01_LFI, ip="172.28.0.5")
    ev2 = create_event("EVT-NEW", t1, AttackStage.STAGE_02_LOG_POISONING, ip="172.28.0.5")

    edge = correlation_engine.evaluate_pair(ev1, ev2)
    assert edge is None


# ==============================================================================
# PHASE-10-F06 & F07: Uncertainty Verification & Inferred Classification
# ==============================================================================

def test_p10_f06_f07_uncertainty_and_inferred_classification(correlation_engine: CorrelationEngine):
    """Verify weak correlation without common identity is explicitly classified as Inferred with Low confidence."""
    t0 = datetime(2026, 10, 6, 14, 30, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=1.5)

    # Different IPs, no common process or resource
    ev1 = create_event("EVT-DIFF-1", t0, AttackStage.STAGE_01_LFI, ip="192.168.1.50")
    ev2 = create_event("EVT-DIFF-2", t1, AttackStage.STAGE_03_RCE, ip="10.0.0.99")

    edge = correlation_engine.evaluate_pair(ev1, ev2)
    assert edge is not None
    assert edge.confidence_score < 0.50
    assert edge.confidence_level == ConfidenceLevel.LOW
    assert edge.classification == EvidenceClassification.INFERRED
    assert "Weak temporal proximity" in edge.explanation


# ==============================================================================
# Full Case Correlation Graph Synthesis
# ==============================================================================

def test_p10_correlate_events_full_graph(correlation_engine: CorrelationEngine):
    """Verify generating complete case CorrelationGraph with incident clusters."""
    t0 = datetime(2026, 10, 6, 14, 30, 0, tzinfo=timezone.utc)

    events = [
        create_event("EVT-1", t0 + timedelta(seconds=0), AttackStage.STAGE_01_LFI, ip="172.28.0.5"),
        create_event("EVT-2", t0 + timedelta(seconds=2), AttackStage.STAGE_02_LOG_POISONING, ip="172.28.0.5"),
        create_event("EVT-3", t0 + timedelta(seconds=4), AttackStage.STAGE_03_RCE, ip="172.28.0.5", pid=1420),
        create_event("EVT-4", t0 + timedelta(seconds=6), AttackStage.STAGE_03_RCE, ppid=1420, pid=2105, comm="sh"),
        create_event("EVT-5", t0 + timedelta(seconds=10), AttackStage.STAGE_05_ENV_MANIPULATION),
        create_event("EVT-6", t0 + timedelta(seconds=15), AttackStage.STAGE_06_PRIV_ESC, target_name="/tmp/bin/su"),
    ]

    graph = correlation_engine.correlate_events(events)
    assert graph.total_events == 6
    assert graph.total_edges > 0
    assert len(graph.clusters) >= 1
    assert "Controlled LFI-to-PrivEsc" in graph.clusters[0]["name"]

