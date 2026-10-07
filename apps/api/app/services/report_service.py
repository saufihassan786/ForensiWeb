"""Forensic Report Application Service (PHASE-14)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from generators.report_generator import ForensicReportGenerator, ReportDocument
from app.schemas.report import ReportCreate, ReportRead


class ReportService:
    """Orchestrates forensic report generation and export across cases."""

    def __init__(self, reports_dir: str = "data/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.generator = ForensicReportGenerator(default_output_dir=str(self.reports_dir))
        self._reports_store: Dict[str, Dict[str, Any]] = {}

    def generate_case_report(
        self,
        case_id: str,
        case_title: str,
        evidence_items: List[Dict[str, Any]],
        timeline_events: List[Dict[str, Any]],
        detections: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        report_format: str = "markdown",
        report_type: str = "technical",
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a complete forensic report document and persist file."""
        case_data = {
            "id": case_id,
            "title": case_title,
            "status": "investigation_complete",
        }

        report_doc = self.generator.generate_report(
            case=case_data,
            evidence=evidence_items,
            timeline=timeline_events,
            detections=detections,
            findings=findings,
            report_format=report_format,
            report_type=report_type,
            title=title,
        )

        # Write to file
        file_path = self.generator.export_to_file(report_doc, output_dir=self.reports_dir)

        record = {
            "id": report_doc.id,
            "case_id": case_id,
            "report_type": report_type,
            "title": report_doc.title,
            "file_path": str(file_path),
            "sha256": report_doc.sha256,
            "format": report_doc.format,
            "metadata_json": report_doc.metadata,
            "content": report_doc.content,
            "created_at": datetime.now(timezone.utc),
        }
        self._reports_store[report_doc.id] = record
        return record

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        return self._reports_store.get(report_id)

    def list_reports(self, case_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if case_id:
            return [r for r in self._reports_store.values() if r["case_id"] == case_id]
        return list(self._reports_store.values())

    def get_report_content(self, report_id: str) -> Optional[str]:
        record = self._reports_store.get(report_id)
        if not record:
            return None
        if "content" in record:
            return record["content"]
        path = Path(record["file_path"])
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None
