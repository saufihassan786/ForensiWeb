"""Unit and Integration Tests for Phase 11: Timeline & Attack Chain Reconstruction."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Union
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from models.rule import DetectionAlert
from correlation.models import CorrelationEdge, CorrelationGraph
from normalization.schema import AttackStage, CommonEventModel
from timeline.filter import TimelineFilter
from timeline.models import (
    AttackChainRelation,
    TimelineClassification,
    TimelineEntry,
)
from timeline.reconstructor import TimelineReconstructor


def _create_mock_cem(
    event_id: str,
    timestamp: datetime,
    stage: Union[AttackStage, str],
    source_type: str = "web_access_log",
    method: str = "GET",
    path: str = "/index.php",
    ip: str = "192.168.1.100",
    byte_start: int = 0,
    byte_end: int = 100,
    evidence_id: str = "EV-001",
    case_id: str = "CASE-001",
) -> CommonEventModel:
    stage_val = stage.value if isinstance(stage, AttackStage) else stage
    return CommonEventModel(
        event_id=event_id,
        case_id=case_id,
        timestamp=timestamp,
        source_type=source_type,
        source_artifact_id=evidence_id,
        source_location={"line_number": 1, "byte_offset_start": byte_start, "byte_offset_end": byte_end},
        attack_stage=stage_val,
        severity="medium",
        action=f"{method} {path}",
        actor={"ip": ip},
        target={"service_name": "apache2", "path": path},
        details={},
        evidence_ref={"artifact_name": "access.log", "sha256": "a" * 64},
        raw_content=f"{method} {path} HTTP/1.1",
    )


def test_p11_f01_f02_chronological_ordering_and_precision():
    """Verify strictly chronological sequencing with microsecond precision."""
    base_t = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)
    t1 = base_t + timedelta(microseconds=100)
    t2 = base_t + timedelta(microseconds=500)
    t3 = base_t + timedelta(seconds=2)

    # Ingest out of order
    ev2 = _create_mock_cem("EV-2", t2, AttackStage.STAGE_02_LOG_POISONING)
    ev3 = _create_mock_cem("EV-3", t3, AttackStage.STAGE_04_WEB_SHELL)
    ev1 = _create_mock_cem("EV-1", t1, AttackStage.STAGE_01_LFI)

    reconstructor = TimelineReconstructor()
    entries = reconstructor.reconstruct(events=[ev3, ev1, ev2], case_id="CASE-P11-TEST")

    assert len(entries) == 3
    assert entries[0].id == "TL-001"
    assert entries[0].event_ids == ["EV-1"]
    assert entries[1].id == "TL-002"
    assert entries[1].event_ids == ["EV-2"]
    assert entries[2].id == "TL-003"
    assert entries[2].event_ids == ["EV-3"]

    for i in range(len(entries) - 1):
        assert entries[i].timestamp <= entries[i + 1].timestamp
        assert entries[i].order_index < entries[i + 1].order_index


def test_p11_f03_attack_stage_mapping_across_controlled_scenarios():
    """Verify multi-stage scenario progression taxonomy mapping."""
    base_t = datetime(2026, 10, 7, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        _create_mock_cem("EV-1", base_t + timedelta(seconds=1), AttackStage.STAGE_01_LFI, path="/index.php?page=view"),
        _create_mock_cem("EV-2", base_t + timedelta(seconds=2), AttackStage.STAGE_02_LOG_POISONING, path="/index.php?page=../../access.log"),
        _create_mock_cem("EV-3", base_t + timedelta(seconds=3), AttackStage.STAGE_03_RCE, path="/index.php?cmd=id"),
        _create_mock_cem("EV-4", base_t + timedelta(seconds=4), AttackStage.STAGE_04_WEB_SHELL, path="/shell.php?cmd=whoami"),
        _create_mock_cem("EV-5", base_t + timedelta(seconds=5), AttackStage.STAGE_06_PRIV_ESC, path="/privesc"),
    ]

    reconstructor = TimelineReconstructor()
    entries = reconstructor.reconstruct(events=events, case_id="CASE-SCENARIO")

    stages = [e.attack_stage for e in entries]
    assert "LFI" in stages[0]
    assert "LOG_POISONING" in stages[1]
    assert "PRIVILEGE_ESCALATION" in stages[-1]


def test_p11_f04_gap_analysis_and_clock_skew_detection():
    """Verify detection of temporal gaps and backwards clock skew."""
    base_t = datetime(2026, 10, 7, 8, 0, 0, tzinfo=timezone.utc)
    reconstructor = TimelineReconstructor(max_gap_threshold_seconds=1800.0)

    # Normal entries
    entry1 = TimelineEntry(
        id="TL-1", case_id="C1", timestamp=base_t, attack_stage="RECON",
        title="Probe", summary="Scanning", order_index=1,
    )
    # 2 hours later -> Inactivity gap
    entry2 = TimelineEntry(
        id="TL-2", case_id="C1", timestamp=base_t + timedelta(hours=2), attack_stage="LFI",
        title="LFI", summary="Exploitation", order_index=2,
    )
    # Skewed backwards entry
    entry3 = TimelineEntry(
        id="TL-3", case_id="C1", timestamp=base_t + timedelta(hours=1), attack_stage="RCE",
        title="RCE", summary="Execution", order_index=3,
    )

    anomalies = reconstructor.perform_gap_analysis([entry1, entry2, entry3])
    assert len(anomalies) == 2
    types = {a["type"] for a in anomalies}
    assert "INACTIVITY_GAP" in types
    assert "CLOCK_SKEW_REVERSAL" in types


def test_p11_f05_timeline_filtering_and_drilldown():
    """Verify filtering by stage, classification, keywords, and event drilldown."""
    base_t = datetime(2026, 10, 7, 9, 0, 0, tzinfo=timezone.utc)
    ev1 = _create_mock_cem("EV-001", base_t, AttackStage.STAGE_01_LFI, ip="10.0.0.5")
    ev2 = _create_mock_cem("EV-002", base_t + timedelta(seconds=10), AttackStage.STAGE_03_RCE, ip="10.0.0.5")

    reconstructor = TimelineReconstructor()
    entries = reconstructor.reconstruct(events=[ev1, ev2], case_id="CASE-DRILL")

    # Filtering by stage
    lfi_entries = TimelineFilter.filter_entries(entries, stages=["LFI"])
    assert len(lfi_entries) == 1
    assert lfi_entries[0].event_ids == ["EV-001"]

    # Filtering by query
    query_entries = TimelineFilter.filter_entries(entries, query="web_access_log")
    assert len(query_entries) >= 1

    # Drilldown
    drill = TimelineFilter.drill_down(entries[0], events=[ev1, ev2])
    assert drill["milestone_id"] == "TL-001"
    assert drill["supporting_events_count"] == 1
    assert drill["events"][0]["event_id"] == "EV-001"
    assert drill["events"][0]["source_location"]["byte_offset_start"] == 0


def test_p11_f07_attack_chain_graph_synthesis():
    """Verify directed causal graph synthesis with root causes and impacts."""
    base_t = datetime(2026, 10, 7, 11, 0, 0, tzinfo=timezone.utc)
    ev_lfi = _create_mock_cem("EV-LFI", base_t, AttackStage.STAGE_01_LFI, path="/index.php?page=../../var/log/apache2/access.log")
    ev_rce = _create_mock_cem("EV-RCE", base_t + timedelta(seconds=30), AttackStage.STAGE_03_RCE, path="/index.php?cmd=id")
    ev_priv = _create_mock_cem("EV-PRIV", base_t + timedelta(seconds=60), AttackStage.STAGE_06_PRIV_ESC, path="/opt/check_update")

    reconstructor = TimelineReconstructor()
    entries = reconstructor.reconstruct(events=[ev_lfi, ev_rce, ev_priv], case_id="CASE-GRAPH")

    graph = reconstructor.build_attack_chain(entries, case_id="CASE-GRAPH")

    assert graph.case_id == "CASE-GRAPH"
    assert len(graph.nodes) >= 2
    assert len(graph.edges) >= 1
    assert len(graph.root_causes) == 1
    assert len(graph.terminal_impacts) == 1
    assert graph.overall_confidence > 0.0

    # Ensure edge connects valid source and target nodes
    node_ids = {n.id for n in graph.nodes}
    for edge in graph.edges:
        assert edge.source_id in node_ids
        assert edge.target_id in node_ids
        assert edge.relation_type in [
            AttackChainRelation.CAUSES,
            AttackChainRelation.TRIGGERS,
            AttackChainRelation.ESCALATES_TO,
            AttackChainRelation.OBSERVED_PRIOR_TO,
            AttackChainRelation.CORRELATED_WITH,
        ]


def test_p11_api_timeline_endpoints():
    """Verify timeline API endpoints: list, get, graph, drilldown, and creation."""
    app = create_app()
    client = TestClient(app)

    # 1. List timeline entries
    resp = client.get("/api/v1/timeline?case_id=CASE-001")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 1
    first_id = data["items"][0]["id"]

    # 2. Case specific timeline
    resp_case = client.get("/api/v1/timeline/CASE-001")
    assert resp_case.status_code == 200
    assert len(resp_case.json()) >= 1

    # 3. Attack Chain Graph
    resp_graph = client.get("/api/v1/timeline/CASE-001/graph")
    assert resp_graph.status_code == 200
    graph_data = resp_graph.json()
    assert graph_data["case_id"] == "CASE-001"
    assert "nodes" in graph_data
    assert "edges" in graph_data

    # 4. Drill down
    resp_drill = client.get(f"/api/v1/timeline/CASE-001/drilldown/{first_id}")
    assert resp_drill.status_code == 200
    drill_data = resp_drill.json()
    assert drill_data["milestone_id"] == first_id

    # 5. Create timeline milestone
    create_payload = {
        "case_id": "CASE-TEST-CREATE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attack_stage": "RCE",
        "title": "Remote Code Execution via Apache Log",
        "summary": "Successful code execution triggered via inclusion of poisoned log.",
        "order_index": 2,
        "event_ids": ["EVT-999"],
        "evidence_references": ["EV-001"],
        "classification": "Likely",
        "confidence": 0.95,
        "metadata": {"command": "id", "uid": "33(www-data)"},
    }
    resp_create = client.post("/api/v1/timeline", json=create_payload)
    assert resp_create.status_code == 201
    created_entry = resp_create.json()
    assert created_entry["title"] == create_payload["title"]
    assert created_entry["attack_stage"] == "RCE"
    assert created_entry["classification"] == "Likely"
