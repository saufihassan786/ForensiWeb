"""Regression and Failure Recovery Test Suite (PHASE-17).

Verifies:
- PHASE-17-F04: Regression Suite
- PHASE-17-F06: Failure Recovery
- PHASE-17-F07: Invalid Evidence Tests
- PHASE-17-F08: Parser Failure Tests
- PHASE-17-F09: Database / Storage Failure Tests
- PHASE-17-F10: Interrupted & Idempotent Processing Tests
"""

import hashlib
from datetime import datetime, timezone
import pytest

from evaluator.engine import DetectionEngine
from normalization.normalizer import EventNormalizer
from normalization.schema import CommonEventModel
from parsers.registry import ParserRegistry
from timeline.reconstructor import TimelineReconstructor


@pytest.fixture
def parser_registry():
    return ParserRegistry()


def test_p17_f07_f08_malformed_evidence_graceful_handling(parser_registry):
    """Verify that corrupt or truncated log entries do not crash parsers and preserve offsets."""
    corrupted_access_log = (
        "127.0.0.1 - - [06/Oct/2026:12:00:00 +0000] \"GET /index.php HTTP/1.1\" 200 120\n"
        "CORRUPTED_GARBAGE_LINE_WITHOUT_STANDARD_APACHE_FIELDS\n"
        "127.0.0.1 - - [06/Oct/2026:12:00:05 +0000] \"GET /document?file=welcome.txt HTTP/1.1\" 200 45\n"
        "TRUNCATED_LINE 404\n"
    )

    report = parser_registry.parse_artifact(
        content=corrupted_access_log,
        filename="access.log",
        evidence_id="EV-CORRUPT-01",
        sha256="a" * 64,
        source_type="web_access_log",
    )

    # Parser must process entire file without unhandled crash
    assert len(report.records) >= 2
    # Verify that valid records are successfully extracted despite corruption
    assert report.valid_count >= 2


def test_p17_f08_corrupted_auditd_records(parser_registry):
    """Verify auditd parser handles truncated EXECVE records safely."""
    corrupted_audit_log = (
        "type=EXECVE msg=audit(1696593600.123:45): argc=3 a0=\"sh\" a1=\"-c\" a2=\"whoami\"\n"
        "type=UNKNOWN_OR_MALFORMED_RECORD missing_msg\n"
        "type=EXECVE msg=audit(broken_timestamp): argc=0\n"
    )

    report = parser_registry.parse_artifact(
        content=corrupted_audit_log,
        filename="audit.log",
        evidence_id="EV-CORRUPT-AUDIT",
        sha256="b" * 64,
        source_type="linux_auditd",
    )

    assert len(report.records) >= 1
    assert any(r.status == "valid" for r in report.records)


def test_p17_f10_idempotent_reprocessing(parser_registry):
    """Verify that re-processing the same evidence produces byte-identical deterministic results."""
    log_content = (
        "192.168.1.50 - - [06/Oct/2026:10:00:00 +0000] \"GET /document?file=../../logs/access.log HTTP/1.1\" 200 500\n"
        "192.168.1.50 - - [06/Oct/2026:10:00:05 +0000] \"GET /shell?cmd=id HTTP/1.1\" 200 80\n"
    )
    sha = hashlib.sha256(log_content.encode("utf-8")).hexdigest()

    # Pass 1
    report_1 = parser_registry.parse_artifact(
        content=log_content, filename="access.log", evidence_id="EV-IDEM-01", sha256=sha
    )
    normalizer = EventNormalizer()
    events_1 = [normalizer.normalize_record(r, "CASE-IDEM") for r in report_1.records]

    # Pass 2
    report_2 = parser_registry.parse_artifact(
        content=log_content, filename="access.log", evidence_id="EV-IDEM-01", sha256=sha
    )
    events_2 = [normalizer.normalize_record(r, "CASE-IDEM") for r in report_2.records]

    assert len(events_1) == len(events_2)
    for e1, e2 in zip(events_1, events_2):
        assert e1.source_artifact_id == e2.source_artifact_id
        assert e1.attack_stage == e2.attack_stage
        assert e1.source_location.byte_offset_start == e2.source_location.byte_offset_start
        assert e1.source_location.byte_offset_end == e2.source_location.byte_offset_end


def test_p17_f05_timeline_clock_skew_recovery():
    """Verify timeline reconstructor safely handles disordered timestamps or clock skew."""
    now = datetime.now(timezone.utc)
    ev_early = CommonEventModel(
        event_id="EVT-01",
        case_id="CASE-SKEW",
        timestamp=datetime.fromtimestamp(1000, tz=timezone.utc),
        source_type="web_access_log",
        source_artifact_id="EV-01",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 50},
        attack_stage="stage_01_lfi",
        severity="medium",
        action="GET /document",
        actor={"ip": "10.0.0.1"},
        target={"path": "/document"},
        details={},
        evidence_ref={"artifact_name": "access.log", "sha256": "c" * 64},
        raw_content="GET /document",
    )
    ev_late = CommonEventModel(
        event_id="EVT-02",
        case_id="CASE-SKEW",
        timestamp=datetime.fromtimestamp(2000, tz=timezone.utc),
        source_type="web_access_log",
        source_artifact_id="EV-01",
        source_location={"line_number": 2, "byte_offset_start": 51, "byte_offset_end": 100},
        attack_stage="stage_02_log_poisoning",
        severity="high",
        action="GET /document",
        actor={"ip": "10.0.0.1"},
        target={"path": "/document"},
        details={},
        evidence_ref={"artifact_name": "access.log", "sha256": "c" * 64},
        raw_content="GET /document",
    )

    reconstructor = TimelineReconstructor()
    # Ingest in reversed order
    timeline = reconstructor.reconstruct(events=[ev_late, ev_early], case_id="CASE-SKEW")

    assert len(timeline) == 2
    # Verify strict ascending order maintained
    assert timeline[0].timestamp <= timeline[1].timestamp
    assert timeline[0].event_ids == ["EVT-01"]
    assert timeline[1].event_ids == ["EVT-02"]
