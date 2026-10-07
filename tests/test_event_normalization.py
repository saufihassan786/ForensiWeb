"""Verification Test Suite for PHASE 08 — Common Event Model & Normalization.

Verifies:
- PHASE-08-F01: Common Event Schema (Pydantic model validation and types)
- PHASE-08-F02: Event Validation (UTC timestamps, enums, required links)
- PHASE-08-F03: Normalization Pipeline (Web logs, App logs, Audit logs to CEM)
- PHASE-08-F04: Event Persistence (JSONL derived store)
- PHASE-08-F05: Event Search (multi-field keyword search)
- PHASE-08-F06: Event Filtering (severity, attack stage, timestamp range)
- PHASE-08-F07: Evidence Traceability (verifying byte slice fidelity back to original file)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import pytest

from evidence.ingestion import EvidenceIngestionService
from evidence.storage import EvidenceStorage
from normalization.normalizer import EventNormalizer
from normalization.schema import AttackStage, CommonEventModel, SeverityLevel
from normalization.store import NormalizedEventStore
from parsers.registry import ParserRegistry


@pytest.fixture
def normalization_env(tmp_path: Path):
    storage = EvidenceStorage(root_dir=tmp_path / "evidence")
    ingestion = EvidenceIngestionService(storage=storage)
    parser_registry = ParserRegistry()
    event_store = NormalizedEventStore(storage=storage)
    return {
        "storage": storage,
        "ingestion": ingestion,
        "parsers": parser_registry,
        "store": event_store,
        "tmp_path": tmp_path,
    }


# ==============================================================================
# PHASE-08-F01 & F02: Schema & Validation
# ==============================================================================

def test_p08_f01_f02_schema_validation():
    """Verify CommonEventModel schema integrity and UTC normalization."""
    now_naive = datetime(2026, 10, 6, 14, 30, 0)
    event = CommonEventModel(
        event_id="EVT-00000001",
        case_id="CASE-NORM-01",
        timestamp=now_naive,
        source_type="web_access_log",
        source_artifact_id="EV-100",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 50},
        attack_stage="stage_01_lfi",
        severity="high",
        action="http_lfi_probe",
        actor={"ip": "172.28.0.5"},
        target={"path": "/view"},
        details={},
        evidence_ref={"artifact_name": "access.log", "sha256": "a" * 64},
        raw_content="GET /view?page=../../etc/passwd",
    )

    assert event.event_id == "EVT-00000001"
    assert event.timestamp.tzinfo == timezone.utc
    assert event.attack_stage == AttackStage.STAGE_01_LFI
    assert event.severity == SeverityLevel.HIGH


# ==============================================================================
# PHASE-08-F03: Normalization Pipeline
# ==============================================================================

def test_p08_f03_normalization_across_sources(sample_raw_logs: dict, normalization_env: dict):
    """Verify end-to-end parsing and normalization across web, app, and audit logs."""
    parsers: ParserRegistry = normalization_env["parsers"]
    case_id = "CASE-MULTI-01"

    # 1. Normalize Web Access Log
    web_report = parsers.parse_artifact(
        content=sample_raw_logs["access"],
        filename="access.log",
        evidence_id="EV-WEB-99",
        sha256="1" * 64,
    )
    web_events = EventNormalizer.normalize_batch(web_report.records, case_id)
    assert len(web_events) >= 5

    stages = [e.attack_stage for e in web_events]
    assert AttackStage.STAGE_01_LFI in stages
    assert AttackStage.STAGE_02_LOG_POISONING in stages
    assert AttackStage.STAGE_03_RCE in stages

    # 2. Normalize Application Log
    app_report = parsers.parse_artifact(
        content=sample_raw_logs["error"],
        filename="app.log",
        evidence_id="EV-APP-99",
        sha256="2" * 64,
    )
    app_events = EventNormalizer.normalize_batch(app_report.records, case_id)
    assert len(app_events) >= 5
    app_stages = [e.attack_stage for e in app_events]
    assert AttackStage.STAGE_01_LFI in app_stages

    # 3. Normalize Audit Log
    audit_report = parsers.parse_artifact(
        content=sample_raw_logs["auditd"],
        filename="audit.log",
        evidence_id="EV-AUD-99",
        sha256="3" * 64,
    )
    audit_events = EventNormalizer.normalize_batch(audit_report.records, case_id)
    assert len(audit_events) >= 5
    audit_stages = [e.attack_stage for e in audit_events]
    assert AttackStage.STAGE_06_PRIV_ESC in audit_stages


# ==============================================================================
# PHASE-08-F04: Event Persistence (JSONL)
# ==============================================================================

def test_p08_f04_event_persistence(normalization_env: dict):
    """Verify persisting and reloading events from derived JSONL store."""
    store: NormalizedEventStore = normalization_env["store"]
    case_id = "CASE-PERSIST-01"

    event = CommonEventModel(
        event_id="EVT-PERSIST-01",
        case_id=case_id,
        timestamp=datetime.now(timezone.utc),
        source_type="web_access_log",
        source_artifact_id="EV-100",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 20},
        attack_stage="stage_01_lfi",
        severity="high",
        action="http_get",
        actor={"ip": "1.1.1.1"},
        target={"path": "/"},
        details={},
        evidence_ref={"artifact_name": "test.log", "sha256": "0" * 64},
        raw_content="raw test line",
    )

    saved_count = store.save_events(case_id, [event])
    assert saved_count == 1

    loaded = store.load_events(case_id)
    assert len(loaded) == 1
    assert loaded[0].event_id == "EVT-PERSIST-01"


# ==============================================================================
# PHASE-08-F05 & F06: Search & Filtering
# ==============================================================================

def test_p08_f05_f06_search_and_filter(sample_raw_logs: dict, normalization_env: dict):
    """Verify search by keyword and filtering by attack stage and severity."""
    parsers: ParserRegistry = normalization_env["parsers"]
    store: NormalizedEventStore = normalization_env["store"]
    case_id = "CASE-SEARCH-01"

    web_report = parsers.parse_artifact(
        content=sample_raw_logs["access"],
        filename="access.log",
        evidence_id="EV-WEB-SEARCH",
        sha256="4" * 64,
    )
    events = EventNormalizer.normalize_batch(web_report.records, case_id)
    store.save_events(case_id, events)

    # 1. Search keyword "passwd"
    search_results = store.search(case_id, "passwd")
    assert len(search_results) >= 1
    assert any("passwd" in e.raw_content for e in search_results)

    # 2. Filter by attack stage
    lfi_events = store.filter(case_id, attack_stage="stage_01_lfi")
    assert len(lfi_events) >= 1
    assert all(e.attack_stage == "stage_01_lfi" for e in lfi_events)

    # 3. Filter by severity
    high_events = store.filter(case_id, severity="high")
    assert len(high_events) >= 1
    assert all(e.severity == "high" for e in high_events)


# ==============================================================================
# PHASE-08-F07: Evidence Traceability
# ==============================================================================

def test_p08_f07_evidence_traceability_fidelity(normalization_env: dict):
    """Verify that normalized events can be verified directly against byte slices of original file."""
    ingestion: EvidenceIngestionService = normalization_env["ingestion"]
    parsers: ParserRegistry = normalization_env["parsers"]
    store: NormalizedEventStore = normalization_env["store"]
    case_id = "CASE-TRACE-01"
    raw_content = (
        '127.0.0.1 - - [06/Oct/2026:14:30:10 +0000] "GET /home HTTP/1.1" 200 100\n'
        '172.28.0.5 - - [06/Oct/2026:14:31:22 +0000] "GET /view?page=../../../../etc/passwd HTTP/1.1" 400 240\n'
    )

    # 1. Ingest original into immutable storage
    meta = ingestion.ingest(
        case_id=case_id,
        source="web_server",
        filename="access.log",
        content=raw_content.encode("utf-8"),
    )

    # 2. Parse and normalize
    report = parsers.parse_artifact(
        content=raw_content,
        filename="access.log",
        evidence_id=meta.evidence_id,
        sha256=meta.sha256,
        source_type="web_access_log",
    )
    events = EventNormalizer.normalize_batch(report.records, case_id)
    store.save_events(case_id, events)

    # 3. Verify cryptographic traceability for each event
    for ev in events:
        assert store.verify_event_traceability(ev) is True
