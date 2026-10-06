"""Evidence API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.evidence import EvidenceCreate, EvidenceRead

router = APIRouter(prefix="/evidence", tags=["Evidence"])

_SAMPLE_EVIDENCE: List[EvidenceRead] = [
    EvidenceRead(
        id="EV-001",
        case_id="CASE-001",
        source="web_access_log",
        filename="access.log",
        file_path="data/evidence/original/access.log",
        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        size_bytes=1024,
        media_type="text/plain",
        acquired_at=datetime.now(timezone.utc),
        status="acquired",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[EvidenceRead], summary="List Evidence")
async def list_evidence(
    case_id: str = Query(None, description="Filter by case ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[EvidenceRead]:
    """Retrieve paginated inventory of preserved forensic evidence artifacts."""
    filtered = [e for e in _SAMPLE_EVIDENCE if case_id is None or e.case_id == case_id]
    total = len(filtered)
    return PaginatedResponse(
        items=filtered,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED, summary="Register Evidence")
async def register_evidence(evidence_in: EvidenceCreate) -> EvidenceRead:
    """Register metadata for a newly acquired evidence file."""
    now = datetime.now(timezone.utc)
    new_ev = EvidenceRead(
        id=f"EV-{uuid.uuid4().hex[:6].upper()}",
        case_id=evidence_in.case_id,
        source=evidence_in.source,
        filename=evidence_in.filename,
        file_path=evidence_in.file_path,
        sha256=evidence_in.sha256,
        size_bytes=evidence_in.size_bytes,
        media_type=evidence_in.media_type,
        acquired_at=evidence_in.acquired_at,
        status=evidence_in.status,
        created_at=now,
        updated_at=now,
    )
    _SAMPLE_EVIDENCE.append(new_ev)
    return new_ev


@router.get("/{evidence_id}", response_model=EvidenceRead, summary="Get Evidence Details")
async def get_evidence(evidence_id: str) -> EvidenceRead:
    """Retrieve metadata for a specific evidence item."""
    for e in _SAMPLE_EVIDENCE:
        if e.id == evidence_id:
            return e
    raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found")
