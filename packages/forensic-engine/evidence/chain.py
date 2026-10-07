"""Evidence Chain Verification and Audit Subsystem (PHASE-06-F08).

Performs end-to-end cryptographic integrity verification across all preserved artifacts,
confirming custody, immutability, and absence of tampering.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .hasher import calculate_sha256
from .manifest import EvidenceManifestManager, EvidenceMetadata
from .storage import EvidenceStorage

logger = logging.getLogger("forensiweb.evidence.chain")


@dataclass
class ArtifactVerificationResult:
    """Verification outcome for an individual evidence artifact."""

    evidence_id: str
    filename: str
    is_valid: bool
    manifest_sha256: str
    disk_sha256: str
    manifest_size: int
    disk_size: int
    is_read_only: bool
    working_copy_synced: bool
    discrepancies: List[str] = field(default_factory=list)


@dataclass
class EvidenceChainReport:
    """Comprehensive case-level evidence chain verification report."""

    case_id: str
    verified_at: str
    total_artifacts: int
    intact_artifacts: int
    compromised_artifacts: int
    is_chain_intact: bool
    artifact_results: List[ArtifactVerificationResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to serializable dictionary."""
        return asdict(self)


class EvidenceChainVerifier:
    """Audits evidence repository for tampering, hash collisions, and immutability violations."""

    def __init__(self, storage: Optional[EvidenceStorage] = None) -> None:
        self.storage = storage or EvidenceStorage()

    def verify_artifact(self, case_id: str, evidence_id: str) -> ArtifactVerificationResult:
        """Audit an individual evidence artifact on disk."""
        discrepancies: List[str] = []
        ev_dir = self.storage.get_case_original_dir(case_id, evidence_id)

        if not ev_dir.exists():
            return ArtifactVerificationResult(
                evidence_id=evidence_id,
                filename="unknown",
                is_valid=False,
                manifest_sha256="",
                disk_sha256="",
                manifest_size=0,
                disk_size=0,
                is_read_only=False,
                working_copy_synced=False,
                discrepancies=[f"Evidence directory missing: {ev_dir}"],
            )

        # 1. Read manifest
        try:
            meta = EvidenceManifestManager.read_manifest(ev_dir)
        except Exception as exc:
            return ArtifactVerificationResult(
                evidence_id=evidence_id,
                filename="unknown",
                is_valid=False,
                manifest_sha256="",
                disk_sha256="",
                manifest_size=0,
                disk_size=0,
                is_read_only=False,
                working_copy_synced=False,
                discrepancies=[f"Manifest could not be read or is invalid: {exc}"],
            )

        orig_file = ev_dir / meta.filename
        if not orig_file.is_file():
            discrepancies.append(f"Original evidence file '{meta.filename}' is missing from {ev_dir}")
            return ArtifactVerificationResult(
                evidence_id=evidence_id,
                filename=meta.filename,
                is_valid=False,
                manifest_sha256=meta.sha256,
                disk_sha256="",
                manifest_size=meta.size_bytes,
                disk_size=0,
                is_read_only=False,
                working_copy_synced=False,
                discrepancies=discrepancies,
            )

        # 2. Check disk size and hash
        disk_size = orig_file.stat().st_size
        disk_sha = calculate_sha256(orig_file)

        if disk_size != meta.size_bytes:
            discrepancies.append(
                f"Size discrepancy: manifest records {meta.size_bytes} bytes, file has {disk_size} bytes"
            )

        if disk_sha != meta.sha256.lower():
            discrepancies.append(
                f"Cryptographic hash mismatch: manifest records {meta.sha256}, disk calculation is {disk_sha}"
            )

        # 3. Check read-only immutability
        is_ro = self.storage.is_read_only(orig_file)
        if not is_ro:
            # Immutability warning or discrepancy
            discrepancies.append("Original file is not marked read-only (immutability violated)")

        # 4. Check working copy
        working_dir = self.storage.get_case_working_dir(case_id, evidence_id)
        working_file = working_dir / meta.filename
        working_synced = False
        if working_file.is_file():
            working_sha = calculate_sha256(working_file)
            working_synced = (working_sha == disk_sha)
            if not working_synced:
                discrepancies.append("Working copy checksum differs from original checksum")
        else:
            # Not yet generated is acceptable, but note it
            working_synced = True

        is_valid = len(discrepancies) == 0
        return ArtifactVerificationResult(
            evidence_id=evidence_id,
            filename=meta.filename,
            is_valid=is_valid,
            manifest_sha256=meta.sha256,
            disk_sha256=disk_sha,
            manifest_size=meta.size_bytes,
            disk_size=disk_size,
            is_read_only=is_ro,
            working_copy_synced=working_synced,
            discrepancies=discrepancies,
        )

    def verify_case_chain(self, case_id: str) -> EvidenceChainReport:
        """Audit the entire evidence chain for a case."""
        case_dir = self.storage.get_case_original_dir(case_id)
        now_utc = datetime.now(timezone.utc).isoformat()

        if not case_dir.exists():
            return EvidenceChainReport(
                case_id=case_id,
                verified_at=now_utc,
                total_artifacts=0,
                intact_artifacts=0,
                compromised_artifacts=0,
                is_chain_intact=True,
                artifact_results=[],
            )

        results: List[ArtifactVerificationResult] = []
        for d in case_dir.iterdir():
            if d.is_dir() and (d / EvidenceManifestManager.MANIFEST_FILENAME).is_file():
                res = self.verify_artifact(case_id, d.name)
                results.append(res)

        total = len(results)
        intact = sum(1 for r in results if r.is_valid)
        compromised = total - intact

        return EvidenceChainReport(
            case_id=case_id,
            verified_at=now_utc,
            total_artifacts=total,
            intact_artifacts=intact,
            compromised_artifacts=compromised,
            is_chain_intact=(compromised == 0),
            artifact_results=results,
        )
