"""Unit and Integration Tests for Phase 12: Investigation Workspace & Traceability."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.case import CaseCreate, CaseUpdate
from app.schemas.finding import FindingCreate, FindingUpdate
from app.services.case_service import CaseService
from app.services.finding_service import FindingService
from app.services.investigation_service import InvestigationService
from evidence.hasher import StreamHasher
from evidence.storage import EvidenceStorage


@pytest.fixture
def test_investigation_env(tmp_path: Path):
    storage = EvidenceStorage(root_dir=tmp_path / "evidence")
    case_service = CaseService()
    finding_service = FindingService()
    inv_service = InvestigationService(
        case_service=case_service,
        finding_service=finding_service,
        storage=storage,
    )
    return {
        "storage": storage,
        "case_service": case_service,
        "finding_service": finding_service,
        "inv_service": inv_service,
        "tmp_path": tmp_path,
    }


def test_p12_f01_case_lifecycle_management(test_investigation_env):
    """Verify Case creation, retrieval, and status update lifecycle."""
    case_service: CaseService = test_investigation_env["case_service"]

    # 1. Create
    case_in = CaseCreate(
        title="APT Incident Simulation - Web Vector",
        description="Investigation into Apache log poisoning and privilege escalation",
        status="open",
        priority="critical",
    )
    import asyncio
    created = asyncio.run(case_service.create_case(case_in))
    assert created.id.startswith("CASE-")
    assert created.status == "open"
    assert created.priority == "critical"

    # 2. Retrieve
    retrieved = asyncio.run(case_service.get_case(created.id))
    assert retrieved is not None
    assert retrieved.title == case_in.title

    # 3. Update status
    updated = asyncio.run(
        case_service.update_case(created.id, CaseUpdate(status="investigating"))
    )
    assert updated.status == "investigating"


def test_p12_f05_finding_management_and_severity_filtering(test_investigation_env):
    """Verify Finding creation, updating, and querying."""
    finding_service: FindingService = test_investigation_env["finding_service"]
    import asyncio

    finding_in = FindingCreate(
        case_id="CASE-P12-FIND",
        title="Insecure Sudo Configuration on Update Helper",
        severity="critical",
        attack_stage="PRIVILEGE_ESCALATION",
        analysis_summary="Sudoers entry allows www-data to execute /opt/check_update without password.",
        mitigation_summary="Revoke NOPASSWD flag and enforce strict PATH sanitation.",
        evidence_references=["EV-SUDO-001"],
        detection_ids=["DET-PRIV-001"],
        event_ids=["EVT-PRIV-001"],
    )

    created = asyncio.run(finding_service.create_finding(finding_in))
    assert created.id.startswith("FND-")
    assert created.severity == "critical"
    assert created.attack_stage == "PRIVILEGE_ESCALATION"

    # Query by severity
    crit_findings, count = asyncio.run(
        finding_service.list_findings(case_id="CASE-P12-FIND", severity="critical")
    )
    assert count == 1
    assert crit_findings[0].id == created.id

    # Update finding
    updated = asyncio.run(
        finding_service.update_finding(created.id, FindingUpdate(mitigation_summary="Implemented PATH wrapper"))
    )
    assert updated.mitigation_summary == "Implemented PATH wrapper"


def test_p12_f06_evidence_to_finding_complete_traceability(test_investigation_env):
    """Verify full 5-hop traceability chain:
    Finding -> Detection -> Event -> Evidence -> Original Artifact
    """
    inv_service: InvestigationService = test_investigation_env["inv_service"]
    finding_service: FindingService = test_investigation_env["finding_service"]
    storage: EvidenceStorage = test_investigation_env["storage"]
    import asyncio

    case_id = "CASE-TRACE-001"

    # Create dummy original evidence file in storage
    orig_dir = storage.get_case_original_dir(case_id)
    orig_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = orig_dir / "access.log"
    evidence_file.write_text("192.168.1.100 - - [07/Oct/2026:10:00:00 +0000] 'GET /index.php?page=../../etc/passwd HTTP/1.1' 200 120\n")
    sha256 = StreamHasher.compute_file_sha256(evidence_file)

    # Create finding referencing evidence
    finding_in = FindingCreate(
        case_id=case_id,
        title="Path Traversal in Web Access Log",
        severity="high",
        attack_stage="LFI",
        analysis_summary="Observed path traversal request in web access log",
        mitigation_summary="Sanitize inputs",
        evidence_references=["access.log"],
        detection_ids=["DET-001"],
        event_ids=["EVT-001"],
    )
    created_finding = asyncio.run(finding_service.create_finding(finding_in))

    # Verify Traceability
    report = asyncio.run(inv_service.verify_finding_traceability(case_id, created_finding.id))

    assert report.finding_id == created_finding.id
    assert report.is_fully_traceable is True
    assert report.chain_depth >= 4
    assert len(report.unresolved_links) == 0
    assert report.verified_sha256 == sha256
    layer_names = [h.layer for h in report.hops]
    assert "finding" in layer_names
    assert "detection" in layer_names
    assert "event" in layer_names
    assert "evidence" in layer_names
    assert "artifact" in layer_names


def test_p12_f06_missing_reference_traceability_resilience(test_investigation_env):
    """Verify that incomplete or missing evidence links are properly identified without crashing."""
    inv_service: InvestigationService = test_investigation_env["inv_service"]
    finding_service: FindingService = test_investigation_env["finding_service"]
    import asyncio

    # Create unlinked finding with no evidence
    finding_in = FindingCreate(
        case_id="CASE-BROKEN",
        title="Theoretical Attack Finding",
        severity="low",
        attack_stage="RECON",
        analysis_summary="Heuristic inference without direct evidence file",
        mitigation_summary=None,
        evidence_references=[],
        detection_ids=[],
        event_ids=[],
    )
    created = asyncio.run(finding_service.create_finding(finding_in))

    report = asyncio.run(inv_service.verify_finding_traceability("CASE-BROKEN", created.id))
    assert report.is_fully_traceable is False
    assert len(report.unresolved_links) >= 1


def test_p12_f07_investigation_workspace_summary(test_investigation_env):
    """Verify case workspace summary aggregation."""
    inv_service: InvestigationService = test_investigation_env["inv_service"]
    import asyncio

    summary = asyncio.run(inv_service.get_workspace_summary("CASE-001"))
    assert summary["case_id"] == "CASE-001"
    assert "case" in summary
    assert "evidence_count" in summary
    assert "event_count" in summary
    assert "finding_count" in summary


def test_p12_api_workspace_endpoints():
    """Verify FastAPI integration for cases, findings, and traceability verification."""
    app = create_app()
    client = TestClient(app)

    # 1. List cases
    resp_cases = client.get("/api/v1/cases")
    assert resp_cases.status_code == 200
    assert resp_cases.json()["total"] >= 1

    # 2. Case workspace summary
    resp_ws = client.get("/api/v1/cases/CASE-001/workspace")
    assert resp_ws.status_code == 200
    assert resp_ws.json()["case_id"] == "CASE-001"

    # 3. List findings
    resp_fnd = client.get("/api/v1/findings?case_id=CASE-001")
    assert resp_fnd.status_code == 200
    findings = resp_fnd.json()["items"]
    assert len(findings) >= 1
    fnd_id = findings[0]["id"]

    # 4. Verify Finding Traceability API
    resp_trace = client.get(f"/api/v1/findings/{fnd_id}/traceability?case_id=CASE-001")
    assert resp_trace.status_code == 200
    trace_data = resp_trace.json()
    assert trace_data["finding_id"] == fnd_id
    assert "hops" in trace_data
    assert len(trace_data["hops"]) >= 3
