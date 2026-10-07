"""Evidence Ingestion Pipeline (PHASE-06-F04 & PHASE-06-F06).

Coordinates validation, cryptographic verification, immutable preservation,
manifest registration, working-copy creation, and lifecycle status transitions.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import DuplicateEvidenceError, EvidenceError, EvidenceValidationError
from .manifest import EvidenceManifestManager, EvidenceMetadata
from .storage import EvidenceStorage
from .validation import EvidenceValidator

logger = logging.getLogger("forensiweb.evidence.ingestion")


class EvidenceIngestionService:
    """Orchestrates end-to-end evidence ingestion and preservation."""

    def __init__(
        self,
        storage: Optional[EvidenceStorage] = None,
        validator: Optional[EvidenceValidator] = None,
    ) -> None:
        self.storage = storage or EvidenceStorage()
        self.validator = validator or EvidenceValidator()

    @staticmethod
    def generate_evidence_id() -> str:
        """Generate canonical evidence identifier."""
        return f"EV-{uuid.uuid4().hex[:8].upper()}"

    def check_duplicate(self, case_id: str, sha256: str) -> Optional[EvidenceMetadata]:
        """Check if an identical evidence hash already exists for this case."""
        case_orig_dir = self.storage.get_case_original_dir(case_id)
        if not case_orig_dir.exists():
            return None

        # Check each evidence folder's manifest
        for ev_dir in case_orig_dir.iterdir():
            if ev_dir.is_dir():
                manifest_file = ev_dir / EvidenceManifestManager.MANIFEST_FILENAME
                if manifest_file.is_file():
                    try:
                        meta = EvidenceManifestManager.read_manifest(ev_dir)
                        if meta.sha256.lower() == sha256.lower():
                            return meta
                    except Exception:
                        pass
        return None

    def ingest(
        self,
        case_id: str,
        source: str,
        filename: str,
        content: Union[bytes, str, Path],
        expected_sha256: Optional[str] = None,
        declared_media_type: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        allow_duplicates: bool = False,
    ) -> EvidenceMetadata:
        """Execute end-to-end evidence ingestion into the immutable store.

        Steps:
        1. Pre-ingestion validation (safety, size, hash, type).
        2. Duplicate detection.
        3. Allocate canonical evidence ID.
        4. Atomic save to immutable original store.
        5. Generate and write manifest.json.
        6. Create verified working copy.
        7. State transition: 'acquired' -> 'verified'.
        """
        raw_bytes = content.encode("utf-8") if isinstance(content, str) else content

        # Step 1: Pre-validation
        val_result = self.validator.validate_content(
            filename=filename,
            content=raw_bytes,
            source=source,
            case_id=case_id,
            expected_sha256=expected_sha256,
            declared_media_type=declared_media_type,
        )
        val_result.raise_if_invalid()

        safe_filename = self.validator.sanitize_filename(filename)
        calculated_sha = val_result.calculated_sha256

        # Step 2: Duplicate check
        existing_meta = self.check_duplicate(case_id, calculated_sha)
        if existing_meta is not None:
            if not allow_duplicates:
                raise DuplicateEvidenceError(
                    f"Duplicate evidence with SHA-256 {calculated_sha} already exists ({existing_meta.evidence_id}) in case {case_id}",
                    details={"existing_evidence_id": existing_meta.evidence_id, "sha256": calculated_sha},
                )
            logger.info("Duplicate evidence permitted: returning existing metadata %s", existing_meta.evidence_id)
            return existing_meta

        # Step 3: Allocate evidence ID
        evidence_id = self.generate_evidence_id()
        ev_orig_dir = self.storage.get_case_original_dir(case_id, evidence_id)

        try:
            # Step 4: Atomic immutable save
            saved_original_path = self.storage.save_original(
                case_id=case_id,
                evidence_id=evidence_id,
                filename=safe_filename,
                content=raw_bytes,
            )

            # Step 5: Build metadata & manifest
            metadata = EvidenceManifestManager.create_metadata(
                evidence_id=evidence_id,
                case_id=case_id,
                filename=safe_filename,
                source=source,
                sha256=calculated_sha,
                size_bytes=val_result.size_bytes,
                media_type=val_result.detected_media_type,
                acquired_at=datetime.now(timezone.utc),
                status="verified",
                custom_metadata=custom_metadata,
            )
            metadata.validation_notes = val_result.warnings
            EvidenceManifestManager.write_manifest(ev_orig_dir, metadata)

            # Step 6: Create verified working copy for parsers
            self.storage.create_working_copy(
                case_id=case_id,
                evidence_id=evidence_id,
                filename=safe_filename,
            )

            logger.info(
                "Successfully ingested evidence artifact %s for case %s (SHA-256: %s)",
                evidence_id,
                case_id,
                calculated_sha,
            )
            return metadata

        except Exception as exc:
            # Clean up on failure to preserve store consistency
            if ev_orig_dir.exists():
                # On Windows/POSIX, read-only files must have write permissions restored before rmtree
                for p in ev_orig_dir.glob("**/*"):
                    if p.is_file():
                        try:
                            p.chmod(0o777)
                        except OSError:
                            pass
                shutil.rmtree(ev_orig_dir, ignore_errors=True)
            ev_working_dir = self.storage.get_case_working_dir(case_id, evidence_id)
            if ev_working_dir.exists():
                shutil.rmtree(ev_working_dir, ignore_errors=True)

            logger.error("Evidence ingestion failed for %s: %s", filename, exc)
            if isinstance(exc, (EvidenceError, EvidenceValidationError)):
                raise
            raise EvidenceError(f"Evidence ingestion failed: {exc}") from exc
