"""Evidence Application Service (PHASE-06).

Coordinates forensic evidence ingestion, storage, integrity verification,
and relational metadata persistence between FastAPI endpoints and the forensic engine.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.evidence import Evidence
from app.repositories.evidence import EvidenceRepository
from app.schemas.evidence import EvidenceCreate, EvidenceRead
from evidence.chain import EvidenceChainReport, EvidenceChainVerifier
from evidence.exceptions import (
    DuplicateEvidenceError,
    EvidenceIntegrityError,
    EvidenceNotFoundError,
    EvidenceValidationError,
)
from evidence.ingestion import EvidenceIngestionService
from evidence.manifest import EvidenceMetadata
from evidence.retrieval import EvidenceRetrievalService
from evidence.storage import EvidenceStorage
from evidence.validation import EvidenceValidator

logger = logging.getLogger("forensiweb.services.evidence")


class EvidenceService:
    """Application service for evidence ingestion, verification, and retrieval."""

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        cfg = get_settings()
        self.root_dir = root_dir or cfg.EVIDENCE_ROOT_DIR
        self.storage = EvidenceStorage(root_dir=self.root_dir)
        self.validator = EvidenceValidator(
            allowed_types=cfg.EVIDENCE_ALLOWED_TYPES,
            max_file_size_bytes=cfg.EVIDENCE_MAX_FILE_SIZE_MB * 1024 * 1024,
        )
        self.ingestion_service = EvidenceIngestionService(
            storage=self.storage,
            validator=self.validator,
        )
        self.retrieval_service = EvidenceRetrievalService(storage=self.storage)
        self.chain_verifier = EvidenceChainVerifier(storage=self.storage)

    async def ingest_evidence(
        self,
        session: AsyncSession,
        case_id: str,
        source: str,
        filename: str,
        content: Union[bytes, str, Path],
        expected_sha256: Optional[str] = None,
        declared_media_type: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceRead:
        """Ingest artifact into immutable store and persist metadata in database."""
        # 1. Ingest into immutable storage via Forensic Engine
        meta: EvidenceMetadata = self.ingestion_service.ingest(
            case_id=case_id,
            source=source,
            filename=filename,
            content=content,
            expected_sha256=expected_sha256,
            declared_media_type=declared_media_type,
            custom_metadata=custom_metadata,
        )

        # 2. Check if DB record already exists
        existing_db = await EvidenceRepository.get_by_id(session, meta.evidence_id)
        if existing_db:
            return EvidenceRead.model_validate(existing_db)

        # 3. Persist into PostgreSQL / SQLite database
        now = datetime.now(timezone.utc)
        evidence_entity = Evidence(
            id=meta.evidence_id,
            case_id=meta.case_id,
            source=meta.source,
            filename=meta.filename,
            file_path=str(self.storage.get_original_path(meta.case_id, meta.evidence_id, meta.filename)),
            sha256=meta.sha256,
            size_bytes=meta.size_bytes,
            media_type=meta.media_type,
            acquired_at=datetime.fromisoformat(meta.acquired_at),
            status=meta.status,
            created_at=now,
            updated_at=now,
        )
        await EvidenceRepository.create(session, evidence_entity)
        return EvidenceRead.model_validate(evidence_entity)

    async def get_evidence(self, session: AsyncSession, evidence_id: str) -> EvidenceRead:
        """Fetch evidence record by ID."""
        entity = await EvidenceRepository.get_by_id(session, evidence_id)
        if not entity:
            raise EvidenceNotFoundError(f"Evidence record '{evidence_id}' not found")
        return EvidenceRead.model_validate(entity)

    async def list_evidence(
        self,
        session: AsyncSession,
        case_id: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[EvidenceRead], int]:
        """List paginated evidence records."""
        items, total = await EvidenceRepository.list_by_case(
            session=session,
            case_id=case_id,
            source=source,
            status=status,
            skip=skip,
            limit=limit,
        )
        return [EvidenceRead.model_validate(i) for i in items], total

    def verify_case_chain(self, case_id: str) -> EvidenceChainReport:
        """Run cryptographic chain of custody audit on evidence files."""
        return self.chain_verifier.verify_case_chain(case_id)

    def verify_single_evidence(self, case_id: str, evidence_id: str):
        """Audit an individual evidence artifact."""
        return self.chain_verifier.verify_artifact(case_id, evidence_id)

    def get_original_content(self, case_id: str, evidence_id: str) -> bytes:
        """Safely read original evidence content with cryptographic verification."""
        return self.retrieval_service.read_original_bytes(case_id, evidence_id, verify_hash=True)
