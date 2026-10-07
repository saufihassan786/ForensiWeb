"""Evidence Retrieval and Inspection Subsystem (PHASE-06-F07).

Provides secure, read-only access to preserved evidence artifacts,
preventing modification during inspection and analysis.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Generator, List, Optional

from .exceptions import CorruptedEvidenceError, EvidenceIntegrityError, EvidenceNotFoundError
from .hasher import calculate_sha256
from .manifest import EvidenceManifestManager, EvidenceMetadata
from .storage import EvidenceStorage

logger = logging.getLogger("forensiweb.evidence.retrieval")


class EvidenceRetrievalService:
    """Provides non-destructive access to original evidence and working copies."""

    def __init__(self, storage: Optional[EvidenceStorage] = None) -> None:
        self.storage = storage or EvidenceStorage()

    def get_metadata(self, case_id: str, evidence_id: str) -> EvidenceMetadata:
        """Fetch manifest metadata for a specific evidence item."""
        ev_dir = self.storage.get_case_original_dir(case_id, evidence_id)
        if not ev_dir.exists():
            raise EvidenceNotFoundError(
                f"Evidence artifact {evidence_id} not found in case {case_id}",
                details={"case_id": case_id, "evidence_id": evidence_id},
            )
        try:
            return EvidenceManifestManager.read_manifest(ev_dir)
        except FileNotFoundError as e:
            raise EvidenceNotFoundError(f"Manifest missing for evidence {evidence_id}: {e}") from e

    def list_evidence(self, case_id: str) -> List[EvidenceMetadata]:
        """List all preserved evidence items in a case."""
        case_dir = self.storage.get_case_original_dir(case_id)
        if not case_dir.exists():
            return []

        results: List[EvidenceMetadata] = []
        for item_dir in case_dir.iterdir():
            if item_dir.is_dir():
                manifest_file = item_dir / EvidenceManifestManager.MANIFEST_FILENAME
                if manifest_file.is_file():
                    try:
                        results.append(EvidenceManifestManager.read_manifest(item_dir))
                    except Exception as exc:
                        logger.warning("Could not read manifest in %s: %s", item_dir, exc)
        return results

    def get_original_path(self, case_id: str, evidence_id: str) -> Path:
        """Return the immutable original file path, verifying it exists."""
        meta = self.get_metadata(case_id, evidence_id)
        return self.storage.get_original_path(case_id, evidence_id, meta.filename)

    def read_original_bytes(self, case_id: str, evidence_id: str, verify_hash: bool = True) -> bytes:
        """Read pristine evidence bytes directly from the immutable store."""
        meta = self.get_metadata(case_id, evidence_id)
        original_path = self.storage.get_original_path(case_id, evidence_id, meta.filename)

        content = original_path.read_bytes()

        if verify_hash:
            actual_sha = calculate_sha256(content)
            if actual_sha != meta.sha256.lower():
                # Flag corruption
                self.update_status(case_id, evidence_id, "corrupted")
                raise EvidenceIntegrityError(
                    f"Integrity check failed while reading evidence {evidence_id}: expected {meta.sha256}, got {actual_sha}",
                    details={"evidence_id": evidence_id, "expected": meta.sha256, "actual": actual_sha},
                )

        return content

    def get_working_copy_path(self, case_id: str, evidence_id: str) -> Path:
        """Obtain path to the working copy intended for parsing operations."""
        meta = self.get_metadata(case_id, evidence_id)
        return self.storage.get_working_path(case_id, evidence_id, meta.filename, auto_create=True)

    def update_status(self, case_id: str, evidence_id: str, new_status: str) -> EvidenceMetadata:
        """Update processing status in the manifest (e.g., acquired, verified, parsed, corrupted)."""
        ev_dir = self.storage.get_case_original_dir(case_id, evidence_id)
        meta = self.get_metadata(case_id, evidence_id)
        meta.status = new_status
        EvidenceManifestManager.write_manifest(ev_dir, meta)
        return meta
