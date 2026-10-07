"""Evidence Metadata and Cryptographic Manifest Management (PHASE-06-F02).

Implements forensic manifest generation, serialization, and integrity verification
per ISO/IEC 27037 standards.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import EvidenceIntegrityError, EvidenceValidationError
from .hasher import calculate_sha256


@dataclass
class EvidenceMetadata:
    """Strongly-typed metadata record for a preserved evidence artifact."""

    evidence_id: str
    case_id: str
    filename: str
    source: str
    sha256: str
    size_bytes: int
    media_type: str
    acquired_at: str
    status: str = "acquired"  # acquired, verified, parsed, corrupted
    collector_version: str = "1.0.0"
    validation_status: str = "valid"
    validation_notes: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidenceMetadata:
        """Construct EvidenceMetadata from dictionary."""
        return cls(
            evidence_id=data["evidence_id"],
            case_id=data["case_id"],
            filename=data["filename"],
            source=data["source"],
            sha256=data["sha256"],
            size_bytes=data["size_bytes"],
            media_type=data["media_type"],
            acquired_at=data["acquired_at"],
            status=data.get("status", "acquired"),
            collector_version=data.get("collector_version", "1.0.0"),
            validation_status=data.get("validation_status", "valid"),
            validation_notes=data.get("validation_notes", []),
            custom_metadata=data.get("custom_metadata", {}),
        )


class EvidenceManifestManager:
    """Manages manifest.json persistence and integrity checks."""

    MANIFEST_FILENAME = "manifest.json"

    @classmethod
    def create_metadata(
        cls,
        evidence_id: str,
        case_id: str,
        filename: str,
        source: str,
        sha256: str,
        size_bytes: int,
        media_type: str,
        acquired_at: Optional[datetime] = None,
        status: str = "acquired",
        custom_metadata: Optional[Dict[str, Any]] = None,
    ) -> EvidenceMetadata:
        """Create a validated EvidenceMetadata instance with standardized UTC timestamp."""
        timestamp_str = (
            acquired_at.astimezone(timezone.utc).isoformat()
            if acquired_at
            else datetime.now(timezone.utc).isoformat()
        )
        return EvidenceMetadata(
            evidence_id=evidence_id,
            case_id=case_id,
            filename=filename,
            source=source,
            sha256=sha256.lower(),
            size_bytes=size_bytes,
            media_type=media_type,
            acquired_at=timestamp_str,
            status=status,
            custom_metadata=custom_metadata or {},
        )

    @classmethod
    def write_manifest(cls, directory: Path, metadata: EvidenceMetadata) -> Path:
        """Write manifest.json inside the evidence directory."""
        manifest_path = directory / cls.MANIFEST_FILENAME
        manifest_data = metadata.to_dict()

        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, sort_keys=True)

        return manifest_path

    @classmethod
    def read_manifest(cls, directory: Path) -> EvidenceMetadata:
        """Read and parse manifest.json from an evidence directory."""
        manifest_path = directory / cls.MANIFEST_FILENAME
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return EvidenceMetadata.from_dict(data)

    @classmethod
    def verify_manifest_integrity(cls, directory: Path) -> bool:
        """Verify that the artifact in the directory matches its manifest hash and size."""
        meta = cls.read_manifest(directory)
        artifact_path = directory / meta.filename

        if not artifact_path.is_file():
            raise EvidenceIntegrityError(f"Artifact {meta.filename} declared in manifest does not exist")

        actual_size = artifact_path.stat().st_size
        if actual_size != meta.size_bytes:
            raise EvidenceIntegrityError(
                f"Artifact size mismatch for {meta.filename}: manifest says {meta.size_bytes}, disk has {actual_size}"
            )

        actual_sha256 = calculate_sha256(artifact_path)
        if actual_sha256 != meta.sha256:
            raise EvidenceIntegrityError(
                f"Artifact checksum mismatch for {meta.filename}: manifest says {meta.sha256}, disk has {actual_sha256}"
            )

        return True
