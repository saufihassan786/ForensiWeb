"""Cases API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.case import CaseCreate, CaseRead
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

# In-memory store placeholder for foundation phase before full repository wiring in later phase
_SAMPLE_CASES: List[CaseRead] = [
    CaseRead(
        id="CASE-001",
        title="Sample LFI to PrivEsc Investigation",
        description="Controlled forensic investigation baseline case.",
        status="investigating",
        priority="high",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[CaseRead], summary="List Cases")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[CaseRead]:
    """Retrieve paginated list of forensic investigation cases."""
    total = len(_SAMPLE_CASES)
    return PaginatedResponse(
        items=_SAMPLE_CASES,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED, summary="Create Case")
async def create_case(case_in: CaseCreate) -> CaseRead:
    """Register a new investigation case."""
    now = datetime.now(timezone.utc)
    new_case = CaseRead(
        id=f"CASE-{uuid.uuid4().hex[:6].upper()}",
        title=case_in.title,
        description=case_in.description,
        status=case_in.status,
        priority=case_in.priority,
        created_at=now,
        updated_at=now,
    )
    _SAMPLE_CASES.append(new_case)
    return new_case


@router.get("/{case_id}", response_model=CaseRead, summary="Get Case Details")
async def get_case(case_id: str) -> CaseRead:
    """Retrieve details for a specific investigation case."""
    for c in _SAMPLE_CASES:
        if c.id == case_id:
            return c
    raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
