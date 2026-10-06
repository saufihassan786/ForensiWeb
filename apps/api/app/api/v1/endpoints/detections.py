"""Detections API v1 endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.common import PaginatedResponse
from app.schemas.detection import DetectionCreate, DetectionRead

router = APIRouter(prefix="/detections", tags=["Detections"])

_SAMPLE_DETECTIONS: List[DetectionRead] = [
    DetectionRead(
        id="DET-001",
        case_id="CASE-001",
        rule_id="RULE-LFI-001",
        rule_name="Directory Traversal Pattern in HTTP Query",
        description="Detected ../ path traversal attempt targeting sensitive local resources.",
        severity="high",
        attack_stage="LFI",
        explanation="Matched directory traversal pattern '../' in HTTP GET request path.",
        matched_event_ids=["EVT-001"],
        evidence_references=["EV-001"],
        created_at=datetime.now(timezone.utc),
    )
]


@router.get("", response_model=PaginatedResponse[DetectionRead], summary="List Detections")
async def list_detections(
    case_id: Optional[str] = Query(None, description="Filter by case ID"),
    attack_stage: Optional[str] = Query(None, description="Filter by attack stage"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[DetectionRead]:
    """Retrieve paginated detection alerts."""
    filtered = [
        d for d in _SAMPLE_DETECTIONS
        if (case_id is None or d.case_id == case_id)
        and (attack_stage is None or d.attack_stage == attack_stage)
        and (severity is None or d.severity == severity)
    ]
    total = len(filtered)
    return PaginatedResponse(
        items=filtered,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=1 if total > 0 else 0,
    )


@router.post("", response_model=DetectionRead, status_code=status.HTTP_201_CREATED, summary="Create Detection")
async def create_detection(det_in: DetectionCreate) -> DetectionRead:
    """Record a detection finding."""
    new_det = DetectionRead(
        id=f"DET-{uuid.uuid4().hex[:6].upper()}",
        case_id=det_in.case_id,
        rule_id=det_in.rule_id,
        rule_name=det_in.rule_name,
        description=det_in.description,
        severity=det_in.severity,
        attack_stage=det_in.attack_stage,
        explanation=det_in.explanation,
        matched_event_ids=det_in.matched_event_ids,
        evidence_references=det_in.evidence_references,
        created_at=datetime.now(timezone.utc),
    )
    _SAMPLE_DETECTIONS.append(new_det)
    return new_det


@router.get("/{detection_id}", response_model=DetectionRead, summary="Get Detection Details")
async def get_detection(detection_id: str) -> DetectionRead:
    """Retrieve details for a specific detection rule outcome."""
    for d in _SAMPLE_DETECTIONS:
        if d.id == detection_id:
            return d
    raise HTTPException(status_code=404, detail=f"Detection '{detection_id}' not found")
