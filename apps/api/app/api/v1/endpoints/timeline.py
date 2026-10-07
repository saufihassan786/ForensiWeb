"""Timeline API v1 endpoints (PHASE-11)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.common import PaginatedResponse
from app.schemas.timeline import (
    AttackChainGraphRead,
    TimelineDrillDownRead,
    TimelineEntryCreate,
    TimelineEntryRead,
)
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/timeline", tags=["Timeline"])

_timeline_service = TimelineService()


def get_timeline_service() -> TimelineService:
    """Dependency provider for TimelineService."""
    return _timeline_service


@router.get("", response_model=PaginatedResponse[TimelineEntryRead], summary="List Timeline Entries")
async def list_timeline(
    case_id: Optional[str] = Query(None, description="Filter timeline by case ID"),
    attack_stage: Optional[str] = Query(None, description="Filter by attack stage"),
    classification: Optional[str] = Query(None, description="Filter by classification (Observed, Likely, etc.)"),
    query: Optional[str] = Query(None, description="Keyword search in milestone content"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: TimelineService = Depends(get_timeline_service),
) -> PaginatedResponse[TimelineEntryRead]:
    """Retrieve chronological attack timeline entries with multi-attribute filtering."""
    skip = (page - 1) * page_size
    items, total = await service.list_timeline(
        case_id=case_id,
        attack_stage=attack_stage,
        classification=classification,
        query=query,
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


@router.get("/{case_id}", response_model=List[TimelineEntryRead], summary="Get Case Attack Timeline")
async def get_case_timeline(
    case_id: str,
    service: TimelineService = Depends(get_timeline_service),
) -> List[TimelineEntryRead]:
    """Retrieve the sorted attack timeline sequence for an investigation case."""
    items, _ = await service.list_timeline(case_id=case_id, limit=200)
    return items


@router.get("/{case_id}/graph", response_model=AttackChainGraphRead, summary="Get Attack Chain Graph")
async def get_attack_chain_graph(
    case_id: str,
    service: TimelineService = Depends(get_timeline_service),
) -> AttackChainGraphRead:
    """Retrieve the directed Attack Chain graph for visual sequence analysis."""
    return await service.get_attack_chain_graph(case_id=case_id)


@router.get("/{case_id}/drilldown/{entry_id}", response_model=TimelineDrillDownRead, summary="Drill Down Timeline Entry")
async def drill_down_entry(
    case_id: str,
    entry_id: str,
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineDrillDownRead:
    """Drill down into underlying normalized events and byte offsets for a timeline entry."""
    drill_down = await service.drill_down_entry(entry_id=entry_id, case_id=case_id)
    if not drill_down:
        raise HTTPException(status_code=404, detail=f"Timeline entry '{entry_id}' not found for case '{case_id}'")
    return drill_down


@router.post("", response_model=TimelineEntryRead, status_code=status.HTTP_201_CREATED, summary="Add Timeline Milestone")
async def create_timeline_entry(
    entry_in: TimelineEntryCreate,
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineEntryRead:
    """Record an attack timeline milestone."""
    now = datetime.now(timezone.utc)
    new_entry = TimelineEntryRead(
        id=f"TL-{uuid.uuid4().hex[:6].upper()}",
        case_id=entry_in.case_id,
        timestamp=entry_in.timestamp,
        attack_stage=entry_in.attack_stage,
        title=entry_in.title,
        summary=entry_in.summary,
        order_index=entry_in.order_index,
        event_ids=entry_in.event_ids,
        detection_ids=entry_in.detection_ids,
        evidence_references=entry_in.evidence_references,
        classification=entry_in.classification,
        confidence=entry_in.confidence,
        metadata=entry_in.metadata,
        created_at=now,
    )
    # Cache in service memory
    from timeline.models import TimelineClassification, TimelineEntry as EngineTimelineEntry
    try:
        engine_entry = EngineTimelineEntry(
            id=new_entry.id,
            case_id=new_entry.case_id,
            timestamp=new_entry.timestamp,
            attack_stage=new_entry.attack_stage,
            title=new_entry.title,
            summary=new_entry.summary,
            order_index=new_entry.order_index,
            event_ids=new_entry.event_ids,
            detection_ids=new_entry.detection_ids,
            evidence_references=new_entry.evidence_references,
            classification=TimelineClassification(new_entry.classification) if new_entry.classification in TimelineClassification.__members__.values() else TimelineClassification.OBSERVED,
            confidence=new_entry.confidence,
            metadata=new_entry.metadata,
            created_at=now,
        )
        service._memory_entries.setdefault(entry_in.case_id, []).append(engine_entry)
    except Exception:
        pass
    return new_entry
