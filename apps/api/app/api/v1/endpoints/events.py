"""Events API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.event import EventCreate, EventRead

router = APIRouter(prefix="/events", tags=["Events"])

_SAMPLE_EVENTS: List[EventRead] = [
    EventRead(
        id="EVT-001",
        case_id="CASE-001",
        evidence_id="EV-001",
        timestamp=datetime.now(timezone.utc),
        source="web_access_log",
        event_type="http_request",
        severity="medium",
        actor_ip="192.168.1.100",
        target_service="apache2",
        action_method="GET",
        action_path="/index.php?page=view",
        attack_stage="RECON",
        raw_payload="GET /index.php?page=view HTTP/1.1",
        normalized_data={"status_code": 200},
        created_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[EventRead], summary="Search Normalized Events")
async def list_events(
    case_id: Optional[str] = Query(None, description="Filter by case ID"),
    attack_stage: Optional[str] = Query(None, description="Filter by attack stage"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[EventRead]:
    """Retrieve paginated normalized forensic events."""
    filtered = [
        e for e in _SAMPLE_EVENTS
        if (case_id is None or e.case_id == case_id)
        and (attack_stage is None or e.attack_stage == attack_stage)
        and (severity is None or e.severity == severity)
    ]
    total = len(filtered)
    return PaginatedResponse(
        items=filtered,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED, summary="Ingest Event")
async def create_event(event_in: EventCreate) -> EventRead:
    """Ingest a normalized forensic event."""
    new_evt = EventRead(
        id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
        case_id=event_in.case_id,
        evidence_id=event_in.evidence_id,
        timestamp=event_in.timestamp,
        source=event_in.source,
        event_type=event_in.event_type,
        severity=event_in.severity,
        actor_ip=event_in.actor_ip,
        target_service=event_in.target_service,
        action_method=event_in.action_method,
        action_path=event_in.action_path,
        attack_stage=event_in.attack_stage,
        raw_payload=event_in.raw_payload,
        normalized_data=event_in.normalized_data,
        created_at=datetime.now(timezone.utc),
    )
    _SAMPLE_EVENTS.append(new_evt)
    return new_evt


@router.get("/{event_id}", response_model=EventRead, summary="Get Event Details")
async def get_event(event_id: str) -> EventRead:
    """Retrieve details of a normalized event."""
    for e in _SAMPLE_EVENTS:
        if e.id == event_id:
            return e
    raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
