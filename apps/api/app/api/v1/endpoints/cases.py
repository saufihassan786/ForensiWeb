"""Cases API v1 endpoints (PHASE-12)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate
from app.schemas.common import PaginatedResponse
from app.services.case_service import CaseService
from app.services.investigation_service import InvestigationService

router = APIRouter(prefix="/cases", tags=["Cases"])

_case_service = CaseService()
_investigation_service = InvestigationService(case_service=_case_service)


def get_case_service() -> CaseService:
    return _case_service


def get_investigation_service() -> InvestigationService:
    return _investigation_service


@router.get("", response_model=PaginatedResponse[CaseRead], summary="List Cases")
async def list_cases(
    status: Optional[str] = Query(None, description="Filter by case status: open, investigating, closed, archived"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, critical"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CaseService = Depends(get_case_service),
) -> PaginatedResponse[CaseRead]:
    """Retrieve paginated list of forensic investigation cases."""
    skip = (page - 1) * page_size
    items, total = await service.list_cases(status=status, priority=priority, skip=skip, limit=page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED, summary="Create Case")
async def create_case(
    case_in: CaseCreate,
    service: CaseService = Depends(get_case_service),
) -> CaseRead:
    """Register a new investigation case."""
    return await service.create_case(case_in)


@router.get("/{case_id}", response_model=CaseRead, summary="Get Case Details")
async def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
) -> CaseRead:
    """Retrieve details for a specific investigation case."""
    case = await service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return case


@router.patch("/{case_id}", response_model=CaseRead, summary="Update Case Details")
async def update_case(
    case_id: str,
    case_in: CaseUpdate,
    service: CaseService = Depends(get_case_service),
) -> CaseRead:
    """Update case status, title, description, or priority."""
    updated = await service.update_case(case_id, case_in)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return updated


@router.get("/{case_id}/workspace", summary="Get Investigation Workspace Summary")
async def get_case_workspace(
    case_id: str,
    inv_service: InvestigationService = Depends(get_investigation_service),
) -> Dict[str, Any]:
    """Retrieve unified investigation workspace state for the case."""
    return await inv_service.get_workspace_summary(case_id)
