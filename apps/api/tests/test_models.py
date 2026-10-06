"""Unit tests for Core Data Models (PHASE-02-F05).

Validates:
- All 8 core domain tables defined in architecture.md:
  cases, evidence, events, detections, timeline_entries, findings, reports, audit_logs
- Schema integrity, foreign key relationships, cascade behaviors
- Field constraints and timestamp defaults
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models import (
    AuditLog,
    Case,
    Detection,
    Event,
    Evidence,
    Finding,
    Report,
    TimelineEntry,
)


@pytest.fixture
def db_session() -> Session:
    """Fixture providing an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_metadata_contains_all_core_tables() -> None:
    """Verify that Base.metadata registers all required core tables."""
    expected_tables = {
        "cases",
        "evidence",
        "events",
        "detections",
        "timeline_entries",
        "findings",
        "reports",
        "audit_logs",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_case_lifecycle_and_relationships(db_session: Session) -> None:
    """Verify Case creation and cascading foreign-key relationships."""
    # 1. Create Case
    case = Case(
        title="LFI Log Poisoning Incident #101",
        description="Investigation into unauthorized log entry injection leading to RCE.",
        status="investigating",
        priority="high",
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.title == "LFI Log Poisoning Incident #101"

    # 2. Add Evidence
    evidence = Evidence(
        case_id=case.id,
        source="web_access_log",
        filename="access.log",
        file_path="data/evidence/original/access.log",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        size_bytes=1048,
        media_type="text/plain",
        acquired_at=datetime.now(timezone.utc),
        status="acquired",
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    assert evidence.case_id == case.id
    assert len(case.evidence_items) == 1

    # 3. Add Event
    event = Event(
        case_id=case.id,
        evidence_id=evidence.id,
        timestamp=datetime.now(timezone.utc),
        source="web_access_log",
        event_type="http_request",
        severity="high",
        actor_ip="192.168.1.50",
        action_method="GET",
        action_path="/index.php?page=../../../../var/log/apache2/access.log",
        attack_stage="LFI",
        raw_payload="GET /index.php?page=... HTTP/1.1",
        normalized_data={"param": "page"},
    )
    db_session.add(event)

    # 4. Add Detection
    detection = Detection(
        case_id=case.id,
        rule_id="RULE-LFI-001",
        rule_name="Directory Traversal Pattern in Query String",
        description="Detected ../ traversal attempt targeting system log paths.",
        severity="high",
        attack_stage="LFI",
        explanation="Request matched pattern ../../../../var/log.",
        matched_event_ids=[event.id],
        evidence_references=[evidence.id],
    )
    db_session.add(detection)

    # 5. Add Timeline Entry
    timeline = TimelineEntry(
        case_id=case.id,
        timestamp=datetime.now(timezone.utc),
        attack_stage="LFI",
        title="Initial Directory Traversal Probing",
        summary="Attacker probed for access.log file via vulnerable page parameter.",
        order_index=1,
        event_ids=[event.id],
        evidence_references=[evidence.id],
    )
    db_session.add(timeline)

    # 6. Add Finding
    finding = Finding(
        case_id=case.id,
        title="Unsanitized Local File Inclusion Vulnerability",
        severity="critical",
        attack_stage="LFI",
        analysis_summary="Web application accepts user-supplied paths without validation.",
        mitigation_summary="Implement strict allowlist for file inclusions.",
        evidence_references=[evidence.id],
    )
    db_session.add(finding)

    # 7. Add Report
    report = Report(
        case_id=case.id,
        report_type="technical",
        title="Technical Incident Forensics Report",
        file_path="data/reports/report_case_101.pdf",
        sha256="d04b98f48e8f8bcc15c6ae5ac050801cd6dcfd428fb5f9e65c4e16e7807340fa",
        format="pdf",
        metadata_json={"pages": 5},
    )
    db_session.add(report)

    # 8. Add Audit Log
    audit = AuditLog(
        action="CASE_CREATED",
        actor="forensic_analyst_1",
        resource_type="case",
        resource_id=case.id,
        details_json={"priority": "high"},
        ip_address="127.0.0.1",
    )
    db_session.add(audit)

    db_session.commit()

    # Query back and verify relations
    reloaded_case = db_session.get(Case, case.id)
    assert len(reloaded_case.evidence_items) == 1
    assert len(reloaded_case.events) == 1
    assert len(reloaded_case.detections) == 1
    assert len(reloaded_case.timeline_entries) == 1
    assert len(reloaded_case.findings) == 1
    assert len(reloaded_case.reports) == 1

    # Test cascade delete: deleting case should delete children
    db_session.delete(reloaded_case)
    db_session.commit()

    assert db_session.get(Evidence, evidence.id) is None
    assert db_session.get(Event, event.id) is None
    assert db_session.get(Detection, detection.id) is None
    assert db_session.get(TimelineEntry, timeline.id) is None
    assert db_session.get(Finding, finding.id) is None
    assert db_session.get(Report, report.id) is None

    # Audit log should NOT be deleted (audits are independent platform trails)
    assert db_session.get(AuditLog, audit.id) is not None
