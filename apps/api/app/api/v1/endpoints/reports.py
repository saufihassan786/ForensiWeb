"""Reports API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.report import ReportCreate, ReportRead

router = APIRouter(prefix="/reports", tags=["Reports"])

_SAMPLE_REPORTS: List[ReportRead] = [
    ReportRead(
        id="RPT-001",
        case_id="CASE-001",
        report_type="technical",
        title="Comprehensive Incident Report #001",
        file_path="data/reports/CASE-001-technical.pdf",
        sha256="4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        format="pdf",
        metadata_json={"sections": ["timeline", "evidence", "findings"]},
        created_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[ReportRead], summary="List Reports")
async def list_reports(
    case_id: str = Query(None, description="Filter reports by case ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[ReportRead]:
    """Retrieve paginated generated reports."""
    filtered = [r for r in _SAMPLE_REPORTS if case_id is None or r.case_id == case_id]
    total = len(filtered)
    return PaginatedResponse(
        items=filtered,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED, summary="Create Report Record")
async def create_report(report_in: ReportCreate) -> ReportRead:
    """Register metadata for a generated investigation report."""
    new_report = ReportRead(
        id=f"RPT-{uuid.uuid4().hex[:6].upper()}",
        case_id=report_in.case_id,
        report_type=report_in.report_type,
        title=report_in.title,
        file_path=report_in.file_path,
        sha256=report_in.sha256,
        format=report_in.format,
        metadata_json=report_in.metadata_json,
        created_at=datetime.now(timezone.utc),
    )
    _SAMPLE_REPORTS.append(new_report)
    return new_report


@router.get("/{report_id}", response_model=ReportRead, summary="Get Report Details")
async def get_report(report_id: str) -> ReportRead:
    """Retrieve metadata for a specific generated report."""
    for r in _SAMPLE_REPORTS:
        if r.id == report_id:
            return r
    raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
