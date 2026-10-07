"""Reports API v1 endpoints (PHASE-14)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.common import PaginatedResponse
from app.schemas.report import ReportCreate, ReportRead
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])

report_service = ReportService()

# Seed default initial technical report for CASE-001
_initial_report = report_service.generate_case_report(
    case_id="CASE-001",
    case_title="Controlled LFI & Privilege Escalation Investigation",
    evidence_items=[
        {
            "id": "EV-001",
            "source_path": "lab/fixtures/logs/access.log",
            "collected_at": "2026-10-06T12:00:00Z",
            "size_bytes": 1024,
            "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            "status": "VERIFIED",
        },
        {
            "id": "EV-002",
            "source_path": "lab/fixtures/logs/audit.log",
            "collected_at": "2026-10-06T12:05:00Z",
            "size_bytes": 2048,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "status": "VERIFIED",
        },
    ],
    timeline_events=[
        {
            "timestamp": "2026-10-06T12:00:10.000Z",
            "stage": "stage_01_lfi",
            "severity": "medium",
            "description": "Path traversal targeting web access logs",
            "source_ref": "access.log:L10",
        },
        {
            "timestamp": "2026-10-06T12:01:00.000Z",
            "stage": "stage_06_priv_esc",
            "severity": "critical",
            "description": "Elevated backup script execution via hijacked PATH",
            "source_ref": "audit.log:L35",
        },
    ],
    detections=[
        {
            "rule_id": "RULE-001",
            "rule_name": "LFI Traversal Detection",
            "mitre_id": "T1059.004",
            "severity": "medium",
            "confidence": 0.95,
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
    ],
    findings=[
        {
            "id": "FIND-001",
            "title": "Local File Inclusion to Web Access Logs",
            "severity": "medium",
            "stage": "stage_01_lfi",
            "status": "CONFIRMED",
            "description": "Unsanitized file parameter in /document endpoint exposed web server access logs.",
            "evidence_references": [
                {
                    "artifact_name": "access.log",
                    "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
                    "line_number": 10,
                    "byte_offset_start": 350,
                    "byte_offset_end": 420,
                    "snippet": "GET /document?file=../../logs/access.log",
                }
            ],
        }
    ],
    report_format="markdown",
    report_type="technical",
    title="Comprehensive Incident Report #001",
)


class GenerateReportRequest(BaseModel):
    case_id: str
    case_title: Optional[str] = "Incident Investigation Case"
    report_type: str = Field(default="technical", description="technical | executive | evidence_summary")
    format: str = Field(default="markdown", description="markdown | html | json")
    title: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    detections: Optional[List[Dict[str, Any]]] = None
    findings: Optional[List[Dict[str, Any]]] = None


@router.get("", response_model=PaginatedResponse[ReportRead], summary="List Reports")
async def list_reports(
    case_id: Optional[str] = Query(None, description="Filter reports by case ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ReportRead]:
    """Retrieve paginated generated reports."""
    reports = report_service.list_reports(case_id=case_id)
    total = len(reports)
    items = [
        ReportRead(
            id=r["id"],
            case_id=r["case_id"],
            report_type=r["report_type"],
            title=r["title"],
            file_path=r["file_path"],
            sha256=r["sha256"],
            format=r["format"],
            metadata_json=r.get("metadata_json", {}),
            created_at=r["created_at"],
        )
        for r in reports
    ]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("/generate", response_model=ReportRead, status_code=status.HTTP_201_CREATED, summary="Generate Forensic Report")
async def generate_report(req: GenerateReportRequest) -> ReportRead:
    """Generate and compile a verifiable forensic report document."""
    evidence = req.evidence or _initial_report.get("metadata_json", {}).get("evidence", [])
    timeline = req.timeline or []
    detections = req.detections or []
    findings = req.findings or []

    res = report_service.generate_case_report(
        case_id=req.case_id,
        case_title=req.case_title or f"Case {req.case_id}",
        evidence_items=evidence,
        timeline_events=timeline,
        detections=detections,
        findings=findings,
        report_format=req.format,
        report_type=req.report_type,
        title=req.title,
    )

    return ReportRead(
        id=res["id"],
        case_id=res["case_id"],
        report_type=res["report_type"],
        title=res["title"],
        file_path=res["file_path"],
        sha256=res["sha256"],
        format=res["format"],
        metadata_json=res.get("metadata_json", {}),
        created_at=res["created_at"],
    )


def _validate_safe_id(identifier: str) -> None:
    if ".." in identifier or "/" in identifier or "\\" in identifier or "\0" in identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security violation: Invalid identifier containing path traversal characters",
        )


@router.get("/{report_id}", response_model=ReportRead, summary="Get Report Details")
async def get_report(report_id: str) -> ReportRead:
    """Retrieve metadata for a specific generated report."""
    _validate_safe_id(report_id)
    r = report_service.get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
    return ReportRead(
        id=r["id"],
        case_id=r["case_id"],
        report_type=r["report_type"],
        title=r["title"],
        file_path=r["file_path"],
        sha256=r["sha256"],
        format=r["format"],
        metadata_json=r.get("metadata_json", {}),
        created_at=r["created_at"],
    )


@router.get("/{report_id}/preview", summary="Preview Rendered Report")
async def preview_report(report_id: str) -> Response:
    """Preview report content with appropriate MIME type."""
    _validate_safe_id(report_id)
    r = report_service.get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

    content = report_service.get_report_content(report_id)
    if not content:
        raise HTTPException(status_code=404, detail="Report content not found")

    fmt = r.get("format", "markdown")
    if fmt == "html":
        media_type = "text/html"
    elif fmt == "json":
        media_type = "application/json"
    else:
        media_type = "text/markdown"

    return Response(content=content, media_type=media_type)


@router.get("/{report_id}/download", summary="Download Report File")
async def download_report(report_id: str) -> Response:
    """Download the forensic report with Content-Disposition headers."""
    _validate_safe_id(report_id)
    r = report_service.get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

    content = report_service.get_report_content(report_id)
    if not content:
        raise HTTPException(status_code=404, detail="Report content not found")

    ext = "html" if r.get("format") == "html" else ("json" if r.get("format") == "json" else "md")
    filename = f"{r['id']}.{ext}"

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
