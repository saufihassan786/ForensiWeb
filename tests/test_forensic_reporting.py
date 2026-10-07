"""Integration and verification test suite for PHASE 14 — Forensic Reporting.

Verifies:
- PHASE-14-F01: Report Data Model
- PHASE-14-F02: Report Assembly
- PHASE-14-F03: Evidence References
- PHASE-14-F04: Timeline Section
- PHASE-14-F05: Findings Section
- PHASE-14-F06: Mitigation Section
- PHASE-14-F07: Limitations Section
- PHASE-14-F08: Report Preview
- PHASE-14-F09: Report Export & Cryptographic Integrity
"""

import hashlib
import json
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.report_service import ReportService


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_p14_f01_f02_report_assembly_and_model(client):
    """Verify report data model and assembly across all required sections."""
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    report = data["items"][0]

    assert "id" in report
    assert "case_id" in report
    assert "sha256" in report
    assert len(report["sha256"]) == 64
    assert report["format"] in ["markdown", "html", "json", "pdf"]


def test_p14_f03_to_f07_report_generation_with_sections(client):
    """Verify generation of report with evidence references, timeline, findings, mitigations, limitations."""
    payload = {
        "case_id": "CASE-TEST-14",
        "case_title": "Academic Forensic Test Case",
        "report_type": "technical",
        "format": "markdown",
        "title": "Incident Investigation Report #14",
        "evidence": [
            {
                "id": "EV-TEST-01",
                "source_path": "/var/log/access.log",
                "collected_at": "2026-10-06T10:00:00Z",
                "size_bytes": 1024,
                "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
                "status": "VERIFIED",
            }
        ],
        "timeline": [
            {
                "timestamp": "2026-10-06T10:01:00Z",
                "stage": "stage_01_lfi",
                "severity": "medium",
                "description": "Path traversal targeting system log files",
                "source_ref": "access.log:L10",
            }
        ],
        "detections": [
            {
                "rule_id": "RULE-001",
                "rule_name": "LFI Traversal Detection",
                "mitre_id": "T1059.004",
                "severity": "medium",
                "confidence": 0.95,
                "artifact_id": "EV-TEST-01",
            }
        ],
        "findings": [
            {
                "id": "FIND-TEST-01",
                "title": "Unauthenticated Directory Traversal",
                "severity": "medium",
                "stage": "stage_01_lfi",
                "status": "CONFIRMED",
                "description": "Application permits arbitrary path traversing via file query parameter.",
                "evidence_references": [
                    {
                        "artifact_name": "access.log",
                        "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
                        "line_number": 10,
                        "byte_offset_start": 200,
                        "byte_offset_end": 280,
                        "snippet": "GET /document?file=../../logs/access.log",
                    }
                ],
            }
        ],
    }

    res = client.post("/api/v1/reports/generate", json=payload)
    assert res.status_code == 201
    created = res.json()
    report_id = created["id"]
    assert report_id.startswith("RPT-")
    assert created["sha256"] is not None

    # Verify Preview (PHASE-14-F08)
    preview_res = client.get(f"/api/v1/reports/{report_id}/preview")
    assert preview_res.status_code == 200
    preview_text = preview_res.text
    assert "## 1. Executive Summary" in preview_text
    assert "## 3. Evidence Inventory & Cryptographic Integrity" in preview_text
    assert "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945" in preview_text
    assert "## 4. Chronological Incident Timeline" in preview_text
    assert "## 6. Detailed Forensic Findings" in preview_text
    assert "FIND-TEST-01" in preview_text
    assert "## 7. Security Remediation & Mitigation Recommendations" in preview_text
    assert "## 8. Analytical Limitations & Forensic Uncertainty Statement" in preview_text

    # Verify Download & Cryptographic Integrity (PHASE-14-F09)
    download_res = client.get(f"/api/v1/reports/{report_id}/download")
    assert download_res.status_code == 200
    file_bytes = download_res.content
    assert hashlib.sha256(file_bytes).hexdigest() == created["sha256"]
