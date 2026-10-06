"""Findings API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.finding import FindingCreate, FindingRead

router = APIRouter(prefix="/findings", tags=["Findings"])

_SAMPLE_FINDINGS: List[FindingRead] = [
    FindingRead(
        id="FND-001",
        case_id="CASE-001",
        title="Unsanitized Local File Inclusion Vulnerability",
        severity="critical",
        attack_stage="LFI",
        analysis_summary="Vulnerability allows reading arbitrary local system files including web server logs.",
        mitigation_summary="Validate path inputs against an allowlist and disable direct log file readability.",
        evidence_references=["EV-001"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[FindingRead], summary="List Findings")
async def list_findings(
    case_id: str = Query(None, description="Filter findings by case ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[FindingRead]:
    """Retrieve paginated forensic findings and remediation recommendations."""
    filtered = [f for f in _SAMPLE_FINDINGS if case_id is None or f.case_id == case_id]
    total = len(filtered)
    return PaginatedResponse(
        items=filtered,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=FindingRead, status_code=status.HTTP_201_CREATED, summary="Create Finding")
async def create_finding(finding_in: FindingCreate) -> FindingRead:
    """Record a forensic finding with analysis and mitigation recommendations."""
    now = datetime.now(timezone.utc)
    new_finding = FindingRead(
        id=f"FND-{uuid.uuid4().hex[:6].upper()}",
        case_id=finding_in.case_id,
        title=finding_in.title,
        severity=finding_in.severity,
        attack_stage=finding_in.attack_stage,
        analysis_summary=finding_in.analysis_summary,
        mitigation_summary=finding_in.mitigation_summary,
        evidence_references=finding_in.evidence_references,
        created_at=now,
        updated_at=now,
    )
    _SAMPLE_FINDINGS.append(new_finding)
    return new_finding


@router.get("/{finding_id}", response_model=FindingRead, summary="Get Finding Details")
async def get_finding(finding_id: str) -> FindingRead:
    """Retrieve details for a specific forensic finding."""
    for f in _SAMPLE_FINDINGS:
        if f.id == finding_id:
            return f
    raise HTTPException(status_code=404, detail=f"Finding '{finding_id}' not found")
