"""Evidence API v1 endpoints (PHASE-06).

Provides RESTful operations for evidence ingestion, metadata registration,
artifact retrieval, and cryptographic chain-of-custody verification.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status

from app.schemas.common import PaginatedResponse
from app.schemas.evidence import EvidenceCreate, EvidenceRead
from app.services.evidence_service import EvidenceService
from evidence.exceptions import (
    DuplicateEvidenceError,
    EvidenceIntegrityError,
    EvidenceNotFoundError,
    EvidenceValidationError,
)

router = APIRouter(prefix="/evidence", tags=["Evidence"])

# Service singleton
_evidence_service = EvidenceService()

# In-memory inventory for fast inspection and testing environments
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


def get_evidence_service() -> EvidenceService:
    """Dependency provider for EvidenceService."""
    return _evidence_service


@router.get("", response_model=PaginatedResponse[EvidenceRead], summary="List Evidence")
async def list_evidence(
    case_id: Optional[str] = Query(None, description="Filter by case ID"),
    source: Optional[str] = Query(None, description="Filter by source system"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: EvidenceService = Depends(get_evidence_service),
) -> PaginatedResponse[EvidenceRead]:
    """Retrieve paginated inventory of preserved forensic evidence artifacts."""
    filtered = [
        e for e in _SAMPLE_EVIDENCE
        if (case_id is None or e.case_id == case_id)
        and (source is None or e.source == source)
        and (status_filter is None or e.status == status_filter)
    ]
    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED, summary="Register Evidence Metadata")
async def register_evidence(
    evidence_in: EvidenceCreate,
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    """Register metadata or simulated evidence artifact into the forensic repository."""
    try:
        now = datetime.now(timezone.utc)
        ev_id = f"EV-{uuid.uuid4().hex[:8].upper()}"

        # If pointing to an existing file on disk, perform full physical ingestion
        candidate_path = Path(evidence_in.file_path)
        if candidate_path.is_file():
            meta = service.ingestion_service.ingest(
                case_id=evidence_in.case_id,
                source=evidence_in.source,
                filename=evidence_in.filename,
                content=candidate_path,
                expected_sha256=evidence_in.sha256 if len(evidence_in.sha256) == 64 else None,
                declared_media_type=evidence_in.media_type,
            )
            ev_id = meta.evidence_id
            status_val = meta.status
            sha256_val = meta.sha256
            size_val = meta.size_bytes
        else:
            status_val = evidence_in.status
            sha256_val = evidence_in.sha256.lower()
            size_val = evidence_in.size_bytes

        new_ev = EvidenceRead(
            id=ev_id,
            case_id=evidence_in.case_id,
            source=evidence_in.source,
            filename=evidence_in.filename,
            file_path=evidence_in.file_path,
            sha256=sha256_val,
            size_bytes=size_val,
            media_type=evidence_in.media_type,
            acquired_at=evidence_in.acquired_at,
            status=status_val,
            created_at=now,
            updated_at=now,
        )
        _SAMPLE_EVIDENCE.append(new_ev)
        return new_ev
    except DuplicateEvidenceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EvidenceValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/upload", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED, summary="Upload Evidence Artifact")
async def upload_evidence(
    case_id: str = Form(..., description="Target investigation case ID"),
    source: str = Form(..., description="Evidence origin system/log source"),
    expected_sha256: Optional[str] = Form(None, description="Optional pre-calculated SHA-256"),
    file: UploadFile = File(..., description="Raw evidence file to preserve"),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    """Upload and preserve an authentic evidence file into the immutable store."""
    try:
        content = await file.read()
        meta = service.ingestion_service.ingest(
            case_id=case_id,
            source=source,
            filename=file.filename or "evidence.bin",
            content=content,
            expected_sha256=expected_sha256,
            declared_media_type=file.content_type,
        )
        now = datetime.now(timezone.utc)
        new_ev = EvidenceRead(
            id=meta.evidence_id,
            case_id=meta.case_id,
            source=meta.source,
            filename=meta.filename,
            file_path=str(service.storage.get_original_path(case_id, meta.evidence_id, meta.filename)),
            sha256=meta.sha256,
            size_bytes=meta.size_bytes,
            media_type=meta.media_type,
            acquired_at=datetime.fromisoformat(meta.acquired_at),
            status=meta.status,
            created_at=now,
            updated_at=now,
        )
        _SAMPLE_EVIDENCE.append(new_ev)
        return new_ev
    except DuplicateEvidenceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EvidenceValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _validate_safe_id(identifier: str) -> None:
    if ".." in identifier or "/" in identifier or "\\" in identifier or "\0" in identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security violation: Invalid identifier containing path traversal characters",
        )


@router.get("/{evidence_id}", response_model=EvidenceRead, summary="Get Evidence Details")
async def get_evidence(
    evidence_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceRead:
    """Retrieve metadata for a specific evidence item."""
    _validate_safe_id(evidence_id)
    for e in _SAMPLE_EVIDENCE:
        if e.id == evidence_id:
            return e
    raise HTTPException(status_code=404, detail=f"Evidence item '{evidence_id}' not found")


@router.get("/{evidence_id}/verify", summary="Verify Single Evidence Integrity")
async def verify_evidence(
    evidence_id: str,
    case_id: str = Query(..., description="Associated case ID"),
    service: EvidenceService = Depends(get_evidence_service),
):
    """Audit cryptographic integrity and immutability of a specific evidence artifact."""
    _validate_safe_id(evidence_id)
    _validate_safe_id(case_id)
    result = service.verify_single_evidence(case_id=case_id, evidence_id=evidence_id)
    return {
        "evidence_id": result.evidence_id,
        "filename": result.filename,
        "is_valid": result.is_valid,
        "manifest_sha256": result.manifest_sha256,
        "disk_sha256": result.disk_sha256,
        "is_read_only": result.is_read_only,
        "discrepancies": result.discrepancies,
    }


@router.get("/{evidence_id}/download", summary="Download Evidence Content")
async def download_evidence(
    evidence_id: str,
    case_id: str = Query(..., description="Associated case ID"),
    service: EvidenceService = Depends(get_evidence_service),
):
    """Safely retrieve pristine evidence bytes after verifying cryptographic integrity."""
    _validate_safe_id(evidence_id)
    _validate_safe_id(case_id)
    try:
        ev = next((e for e in _SAMPLE_EVIDENCE if e.id == evidence_id), None)
        filename = ev.filename if ev else f"{evidence_id}.bin"
        media_type = ev.media_type if ev else "application/octet-stream"

        data = service.get_original_content(case_id=case_id, evidence_id=evidence_id)
        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except EvidenceIntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (EvidenceNotFoundError, FileNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/cases/{case_id}/verify-chain", summary="Audit Case Evidence Chain")
async def verify_case_chain(
    case_id: str,
    service: EvidenceService = Depends(get_evidence_service),
):
    """Perform end-to-end audit of all evidence artifacts for a given case."""
    report = service.verify_case_chain(case_id)
    return report.to_dict()
