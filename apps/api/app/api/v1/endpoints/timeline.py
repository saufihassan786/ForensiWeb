"""Timeline API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.timeline import TimelineEntryCreate, TimelineEntryRead

router = APIRouter(prefix="/timeline", tags=["Timeline"])

_SAMPLE_TIMELINE: List[TimelineEntryRead] = [
    TimelineEntryRead(
        id="TL-001",
        case_id="CASE-001",
        timestamp=datetime.now(timezone.utc),
        attack_stage="LFI",
        title="Initial Directory Traversal Probing",
        summary="Attacker probed for system logs through path traversal in page query parameter.",
        order_index=1,
        event_ids=["EVT-001"],
        evidence_references=["EV-001"],
        created_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[TimelineEntryRead], summary="List Timeline Entries")
async def list_timeline(
    case_id: str = Query(None, description="Filter timeline by case ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> PaginatedResponse[TimelineEntryRead]:
    """Retrieve chronological attack timeline entries."""
    filtered = [t for t in _SAMPLE_TIMELINE if case_id is None or t.case_id == case_id]
    sorted_items = sorted(filtered, key=lambda x: (x.order_index, x.timestamp))
    total = len(sorted_items)
    return PaginatedResponse(
        items=sorted_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.get("/{case_id}", response_model=List[TimelineEntryRead], summary="Get Case Attack Timeline")
async def get_case_timeline(case_id: str) -> List[TimelineEntryRead]:
    """Retrieve the sorted attack timeline sequence for an investigation case."""
    case_entries = [t for t in _SAMPLE_TIMELINE if t.case_id == case_id]
    return sorted(case_entries, key=lambda x: (x.order_index, x.timestamp))


@router.post("", response_model=TimelineEntryRead, status_code=status.HTTP_201_CREATED, summary="Add Timeline Milestone")
async def create_timeline_entry(entry_in: TimelineEntryCreate) -> TimelineEntryRead:
    """Record an attack timeline milestone."""
    new_entry = TimelineEntryRead(
        id=f"TL-{uuid.uuid4().hex[:6].upper()}",
        case_id=entry_in.case_id,
        timestamp=entry_in.timestamp,
        attack_stage=entry_in.attack_stage,
        title=entry_in.title,
        summary=entry_in.summary,
        order_index=entry_in.order_index,
        event_ids=entry_in.event_ids,
        evidence_references=entry_in.evidence_references,
        created_at=datetime.now(timezone.utc),
    )
    _SAMPLE_TIMELINE.append(new_entry)
    return new_entry
