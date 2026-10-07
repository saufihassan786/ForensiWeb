"""Findings API v1 endpoints (PHASE-12)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.common import PaginatedResponse
from app.schemas.finding import (
    FindingCreate,
    FindingRead,
    FindingUpdate,
    TraceabilityReportRead,
)
from app.services.finding_service import FindingService
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/findings", tags=["Findings"])

_finding_service = FindingService()
_investigation_service = InvestigationService(finding_service=_finding_service)


def get_finding_service() -> FindingService:
    return _finding_service


def get_investigation_service() -> InvestigationService:
    return _investigation_service


@router.get("", response_model=PaginatedResponse[FindingRead], summary="List Findings")
async def list_findings(
    case_id: Optional[str] = Query(None, description="Filter findings by case ID"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    attack_stage: Optional[str] = Query(None, description="Filter by attack stage"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: FindingService = Depends(get_finding_service),
) -> PaginatedResponse[FindingRead]:
    """Retrieve paginated forensic findings and remediation recommendations."""
    skip = (page - 1) * page_size
    items, total = await service.list_findings(
        case_id=case_id,
        severity=severity,
        attack_stage=attack_stage,
        skip=skip,
        limit=page_size,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.post("", response_model=FindingRead, status_code=status.HTTP_201_CREATED, summary="Create Finding")
async def create_finding(
    finding_in: FindingCreate,
    service: FindingService = Depends(get_finding_service),
) -> FindingRead:
    """Record a forensic finding with analysis and mitigation recommendations."""
    return await service.create_finding(finding_in)


@router.get("/{finding_id}", response_model=FindingRead, summary="Get Finding Details")
async def get_finding(
    finding_id: str,
    service: FindingService = Depends(get_finding_service),
) -> FindingRead:
    """Retrieve details for a specific forensic finding."""
    finding = await service.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail=f"Finding '{finding_id}' not found")
    return finding


@router.patch("/{finding_id}", response_model=FindingRead, summary="Update Finding")
async def update_finding(
    finding_id: str,
    finding_in: FindingUpdate,
    service: FindingService = Depends(get_finding_service),
) -> FindingRead:
    """Update finding fields, mitigation notes, or evidence links."""
    updated = await service.update_finding(finding_id, finding_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Finding '{finding_id}' not found")
    return updated


@router.get("/{finding_id}/traceability", response_model=TraceabilityReportRead, summary="Verify Finding Traceability")
async def verify_finding_traceability(
    finding_id: str,
    case_id: str = Query("CASE-001", description="Associated case ID"),
    inv_service: InvestigationService = Depends(get_investigation_service),
) -> TraceabilityReportRead:
    """Verify complete evidence-to-finding traceability:

    Finding -> Detection -> Event -> Evidence -> Original Artifact
    """
    report = await inv_service.verify_finding_traceability(case_id=case_id, finding_id=finding_id)
    return report
