"""Unit tests for Forensic Report Generator (PHASE-14)."""

import hashlib
import json
import pytest
from pathlib import Path

from generators.report_generator import (
    ForensicReportGenerator,
    ReportDocument,
)


@pytest.fixture
def sample_case():
    return {
        "id": "CASE-2026-001",
        "title": "Incident Investigation: LFI to PrivEsc in Target App",
        "scenario_id": "WEB-CHAIN-001",
        "status": "closed",
    }


@pytest.fixture
def sample_evidence():
    return [
        {
            "id": "EV-001",
            "source_path": "/var/log/nginx/access.log",
            "collected_at": "2026-10-06T12:00:00Z",
            "size_bytes": 4096,
            "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            "status": "VERIFIED",
        },
        {
            "id": "EV-002",
            "source_path": "/var/log/audit/audit.log",
            "collected_at": "2026-10-06T12:05:00Z",
            "size_bytes": 8192,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "status": "VERIFIED",
        },
    ]


@pytest.fixture
def sample_timeline():
    return [
        {
            "timestamp": "2026-10-06T12:00:10.123456Z",
            "stage": "stage_01_lfi",
            "severity": "medium",
            "description": "Path traversal probing targeting access.log",
            "source_ref": "access.log:L12",
        },
        {
            "timestamp": "2026-10-06T12:00:15.543210Z",
            "stage": "stage_02_log_poisoning",
            "severity": "high",
            "description": "User-Agent header contains executable payload",
            "source_ref": "access.log:L15",
        },
        {
            "timestamp": "2026-10-06T12:01:00.000000Z",
            "stage": "stage_06_priv_esc",
            "severity": "critical",
            "description": "Elevated process execution via manipulated PATH",
            "source_ref": "audit.log:L45",
        },
    ]


@pytest.fixture
def sample_detections():
    return [
        {
            "rule_id": "RULE-001",
            "rule_name": "LFI Traversal Detection",
            "mitre_id": "T1059.004",
            "severity": "medium",
            "confidence": 0.95,
            "artifact_id": "EV-001",
        },
        {
            "rule_id": "RULE-002",
            "rule_name": "Log Poisoning Attack",
            "mitre_id": "T1059",
            "severity": "high",
            "confidence": 0.90,
            "artifact_id": "EV-001",
        },
        {
            "rule_id": "RULE-006",
            "rule_name": "Privilege Escalation via PATH Hijack",
            "mitre_id": "T1574.007",
            "severity": "critical",
            "confidence": 0.98,
            "artifact_id": "EV-002",
        },
    ]


@pytest.fixture
def sample_findings():
    return [
        {
            "id": "FIND-01",
            "title": "Unauthenticated Path Traversal to Web Server Logs",
            "severity": "medium",
            "stage": "stage_01_lfi",
            "status": "CONFIRMED",
            "description": "Target application allows unauthenticated file inclusion via /document?file= parameter.",
            "evidence_references": [
                {
                    "artifact_name": "access.log",
                    "evidence_id": "EV-001",
                    "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
                    "line_number": 12,
                    "byte_offset_start": 450,
                    "byte_offset_end": 520,
                    "snippet": "GET /document?file=../../logs/access.log HTTP/1.1",
                }
            ],
        },
        {
            "id": "FIND-02",
            "title": "Root Privilege Escalation via Insecure Script PATH",
            "severity": "critical",
            "stage": "stage_06_priv_esc",
            "status": "CONFIRMED",
            "description": "Privileged backup job invoked binary from world-writable /tmp/bin directory.",
            "evidence_references": [
                {
                    "artifact_name": "audit.log",
                    "evidence_id": "EV-002",
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "line_number": 45,
                    "byte_offset_start": 1200,
                    "byte_offset_end": 1340,
                    "snippet": "type=EXECVE comm=\"backup_tool\" uid=0 euid=0",
                }
            ],
        },
    ]


def test_markdown_report_generation(sample_case, sample_evidence, sample_timeline, sample_detections, sample_findings):
    generator = ForensicReportGenerator()
    report = generator.generate_report(
        case=sample_case,
        evidence=sample_evidence,
        timeline=sample_timeline,
        detections=sample_detections,
        findings=sample_findings,
        report_format="markdown",
        report_type="technical",
    )

    assert isinstance(report, ReportDocument)
    assert report.format == "markdown"
    assert report.case_id == "CASE-2026-001"
    assert "## 1. Executive Summary" in report.content
    assert "## 3. Evidence Inventory & Cryptographic Integrity" in report.content
    assert "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945" in report.content
    assert "## 4. Chronological Incident Timeline" in report.content
    assert "## 6. Detailed Forensic Findings" in report.content
    assert "FIND-01" in report.content
    assert "Line 12, Offset: [450:520]" in report.content
    assert "## 8. Analytical Limitations & Forensic Uncertainty Statement" in report.content
    assert len(report.sha256) == 64


def test_html_report_generation(sample_case, sample_evidence, sample_timeline, sample_detections, sample_findings):
    generator = ForensicReportGenerator()
    report = generator.generate_report(
        case=sample_case,
        evidence=sample_evidence,
        timeline=sample_timeline,
        detections=sample_detections,
        findings=sample_findings,
        report_format="html",
        report_type="technical",
    )

    assert report.format == "html"
    assert "<!DOCTYPE html>" in report.content
    assert "CASE-2026-001" in report.content
    assert "badge badge-critical" in report.content
    assert "mono-hash" in report.content


def test_json_report_generation(sample_case, sample_evidence, sample_timeline, sample_detections, sample_findings):
    generator = ForensicReportGenerator()
    report = generator.generate_report(
        case=sample_case,
        evidence=sample_evidence,
        timeline=sample_timeline,
        detections=sample_detections,
        findings=sample_findings,
        report_format="json",
        report_type="technical",
    )

    assert report.format == "json"
    parsed = json.loads(report.content)
    assert parsed["case"]["id"] == "CASE-2026-001"
    assert len(parsed["evidence"]) == 2
    assert len(parsed["findings"]) == 2
    assert parsed["metadata"]["total_detections"] == 3


def test_export_to_file(tmp_path, sample_case, sample_evidence, sample_timeline, sample_detections, sample_findings):
    generator = ForensicReportGenerator(default_output_dir=str(tmp_path))
    report = generator.generate_report(
        case=sample_case,
        evidence=sample_evidence,
        timeline=sample_timeline,
        detections=sample_detections,
        findings=sample_findings,
        report_format="markdown",
    )

    out_file = generator.export_to_file(report, output_dir=tmp_path)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert hashlib.sha256(content.encode("utf-8")).hexdigest() == report.sha256
    assert report.file_path == str(out_file)


def test_evidence_traceability_verification(sample_case, sample_timeline, sample_detections):
    generator = ForensicReportGenerator()
    evidence = [
        {
            "id": "EV-REAL",
            "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        }
    ]
    findings = [
        {
            "id": "FIND-REAL",
            "title": "Real finding",
            "evidence_references": [{"sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}],
        },
        {
            "id": "FIND-ORPHAN",
            "title": "Orphan finding",
            "evidence_references": [{"sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}],
        },
    ]

    assembled = generator.assemble_report_data(
        case=sample_case,
        evidence=evidence,
        timeline=sample_timeline,
        detections=sample_detections,
        findings=findings,
    )

    assert assembled["findings"][0]["evidence_references"][0]["verified_in_inventory"] is True
    assert assembled["findings"][1]["evidence_references"][0]["verified_in_inventory"] is False
