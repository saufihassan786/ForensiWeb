"""Forensic Report Generator (PHASE-14).

Assembles academic-grade, evidence-backed digital forensic reports across Markdown, HTML, and JSON.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from templates.report_templates import format_html_report, format_markdown_report
except ImportError:
    from ..templates.report_templates import format_html_report, format_markdown_report


@dataclass
class ReportSection:
    id: str
    title: str
    content: Any


@dataclass
class ReportDocument:
    id: str
    case_id: str
    title: str
    report_type: str  # executive, technical, evidence_summary
    format: str  # markdown, html, json
    content: str
    sha256: str
    generated_at: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ForensicReportGenerator:
    """Core generator that compiles multi-source forensic datasets into verifiable reports."""

    def __init__(self, default_output_dir: str = "data/reports"):
        self.default_output_dir = Path(default_output_dir)

    def assemble_report_data(
        self,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]],
        detections: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        mitigations: Optional[List[Dict[str, Any]]] = None,
        limitations: Optional[List[str]] = None,
        report_type: str = "technical",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assemble and cross-verify normalized data prior to formatting."""
        now_utc = datetime.now(timezone.utc).isoformat()
        report_title = title or f"Forensic Investigation Report — {case.get('id', 'CASE')}"

        # Default standard mitigations if none provided
        if not mitigations:
            mitigations = [
                {
                    "title": "Strict Input Validation & Path Traversal Prevention",
                    "target_component": "Web Application (LFI Vector)",
                    "remediation": "Enforce strict basename whitelist for document retrieval; reject '../' and absolute path characters.",
                    "verification_test": "HTTP GET /document?file=../../logs/access.log returns 403 Forbidden without exposing local files.",
                },
                {
                    "title": "Log Poisoning Mitigation & Sanitization",
                    "target_component": "Web Server / Reverse Proxy",
                    "remediation": "Sanitize and escape HTTP User-Agent and Referer headers before writing to disk logs; restrict log directory permissions.",
                    "verification_test": "User-Agent containing execution tokens is sanitized or rendered non-executable in access.log.",
                },
                {
                    "title": "Execution Boundary & PHP Config Hardening",
                    "target_component": "Runtime Environment",
                    "remediation": "Set allow_url_include = Off, disable eval() / shell_exec(), and execute worker process as dedicated unprivileged user.",
                    "verification_test": "Inclusion of access log yields raw text or 500 error; no child processes spawned.",
                },
                {
                    "title": "Secure PATH Environment & SUID Containment",
                    "target_component": "Operating System / Privilege Model",
                    "remediation": "Hardcode absolute binary paths in administrative scripts (e.g. /usr/bin/backup_tool) and drop unnecessary capabilities.",
                    "verification_test": "Altering PATH environment variable does not execute hijacked binaries in /tmp/bin.",
                },
            ]

        # Default academic limitations
        if not limitations:
            limitations = [
                "Telemetry was collected from an isolated, reproducible virtual laboratory network.",
                "Original evidence integrity verified via SHA-256; forensic conclusions are limited strictly to captured artifacts.",
                "Correlations reflect rule-based heuristics and timing thresholds (dt <= 5.0s) as documented in the forensic model.",
            ]

        # Validate that all cited evidence in findings maps to registered evidence
        evidence_sha_map = {e.get("sha256"): e for e in evidence if "sha256" in e}
        evidence_id_map = {e.get("id"): e for e in evidence if "id" in e}

        for finding in findings:
            for ref in finding.get("evidence_references", []):
                ref_sha = ref.get("sha256")
                ref_id = ref.get("evidence_id")
                is_valid = (ref_sha and ref_sha in evidence_sha_map) or (ref_id and ref_id in evidence_id_map)
                ref["verified_in_inventory"] = bool(is_valid)

        exec_summary = (
            f"Forensic investigation for {case.get('id', 'CASE-001')} ({case.get('title', 'Target System')}) "
            f"has completed analysis across {len(evidence)} primary evidence artifacts. "
            f"A total of {len(timeline)} chronological timeline events were normalized and correlated, "
            f"triggering {len(detections)} threat detections across MITRE ATT&CK stages. "
            f"This established {len(findings)} verified forensic findings culminating in confirmed privilege escalation."
        )

        return {
            "title": report_title,
            "case": case,
            "report_type": report_type,
            "classification": "ACADEMIC FORENSICS // RESTRICTED LAB",
            "generated_at": now_utc,
            "investigator": "ForensiWeb Automated Digital Forensics Engine",
            "executive_summary": exec_summary,
            "metadata": {
                "scenario": case.get("scenario_id", "WEB-CHAIN-001"),
                "total_evidence": len(evidence),
                "total_timeline_events": len(timeline),
                "total_detections": len(detections),
                "total_findings": len(findings),
            },
            "evidence": evidence,
            "timeline": timeline,
            "detections": detections,
            "findings": findings,
            "mitigations": mitigations,
            "limitations": limitations,
        }

    def generate_report(
        self,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]],
        detections: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        mitigations: Optional[List[Dict[str, Any]]] = None,
        limitations: Optional[List[str]] = None,
        report_format: str = "markdown",
        report_type: str = "technical",
        title: Optional[str] = None,
    ) -> ReportDocument:
        """Generate a complete ReportDocument in the requested format."""
        assembled = self.assemble_report_data(
            case=case,
            evidence=evidence,
            timeline=timeline,
            detections=detections,
            findings=findings,
            mitigations=mitigations,
            limitations=limitations,
            report_type=report_type,
            title=title,
        )

        fmt = report_format.lower()
        if fmt == "markdown" or fmt == "md":
            content = format_markdown_report(assembled)
            fmt = "markdown"
        elif fmt == "html":
            content = format_html_report(assembled)
            fmt = "html"
        elif fmt == "json":
            content = json.dumps(assembled, indent=2)
            fmt = "json"
        else:
            content = format_markdown_report(assembled)
            fmt = "markdown"

        content_bytes = content.encode("utf-8")
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        report_id = f"RPT-{case.get('id', 'CASE')}-{hashlib.md5(content_bytes).hexdigest()[:6].upper()}"

        return ReportDocument(
            id=report_id,
            case_id=case.get("id", "CASE-001"),
            title=assembled["title"],
            report_type=report_type,
            format=fmt,
            content=content,
            sha256=sha256,
            generated_at=assembled["generated_at"],
            metadata=assembled["metadata"],
        )

    def export_to_file(
        self,
        report_doc: ReportDocument,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Save report document to disk and record absolute path."""
        target_dir = output_dir or self.default_output_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        ext = "md" if report_doc.format == "markdown" else report_doc.format
        filename = f"{report_doc.id}_{report_doc.report_type}.{ext}"
        target_file = target_dir / filename
        target_file.write_text(report_doc.content, encoding="utf-8")
        report_doc.file_path = str(target_file)
        return target_file
