"""Evidence Ingestion Validation Subsystem (PHASE-06-F05).

Enforces forensic integrity checks, MIME validation, format sanity,
and path traversal prevention prior to evidence ingestion.
"""

from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from .exceptions import EvidenceValidationError
from .hasher import calculate_sha256

# Standard default allowed media types
DEFAULT_ALLOWED_TYPES = [
    "text/plain",
    "application/json",
    "application/octet-stream",
    "text/x-log",
    "text/csv",
]

# Max evidence artifact size in bytes (100 MB default)
DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024


@dataclass
class ValidationResult:
    """Detailed evidence validation outcome."""

    is_valid: bool
    calculated_sha256: str
    size_bytes: int
    detected_media_type: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        """Raise EvidenceValidationError if validation failed."""
        if not self.is_valid:
            error_msg = "; ".join(self.errors)
            raise EvidenceValidationError(f"Evidence validation failed: {error_msg}")


class EvidenceValidator:
    """Validates raw evidence inputs before persistent storage."""

    def __init__(
        self,
        allowed_types: Optional[List[str]] = None,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE,
        disallow_empty: bool = True,
    ) -> None:
        self.allowed_types = allowed_types or DEFAULT_ALLOWED_TYPES
        self.max_file_size_bytes = max_file_size_bytes
        self.disallow_empty = disallow_empty

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Ensure filename is safe against directory traversal and special chars."""
        raw = filename.strip()
        if not raw or ".." in raw or "/" in raw or "\\" in raw:
            raise EvidenceValidationError(f"Invalid or unsafe evidence filename: {filename}")
        cleaned = Path(raw).name.strip()
        if not cleaned or cleaned in (".", ".."):
            raise EvidenceValidationError(f"Invalid or unsafe evidence filename: {filename}")
        # Strip potential null bytes or non-printable chars
        if "\0" in cleaned:
            raise EvidenceValidationError("Null byte detected in evidence filename")
        return cleaned

    @staticmethod
    def detect_media_type(filename: str, content: Optional[bytes] = None) -> str:
        """Detect MIME type from filename extension and content heuristics."""
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            return guessed

        if filename.endswith(".log"):
            return "text/x-log"
        if filename.endswith(".json") or filename.endswith(".jsonl"):
            return "application/json"

        # Check content heuristic if available
        if content:
            try:
                content.decode("utf-8")
                return "text/plain"
            except UnicodeDecodeError:
                return "application/octet-stream"

        return "text/plain"

    def validate_content(
        self,
        filename: str,
        content: Union[bytes, Path],
        source: str,
        case_id: str,
        expected_sha256: Optional[str] = None,
        declared_media_type: Optional[str] = None,
    ) -> ValidationResult:
        """Perform comprehensive validation on incoming evidence content."""
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Validate identifiers
        if not case_id or not str(case_id).strip():
            errors.append("Case ID cannot be empty")
        if not source or not str(source).strip():
            errors.append("Evidence source cannot be empty")

        # 2. Sanitize and validate filename
        try:
            safe_name = self.sanitize_filename(filename)
        except EvidenceValidationError as err:
            errors.append(str(err))
            safe_name = filename

        # 3. Read content and calculate size & hash
        if isinstance(content, Path):
            if not content.is_file():
                errors.append(f"Evidence file does not exist: {content}")
                return ValidationResult(
                    is_valid=False,
                    calculated_sha256="",
                    size_bytes=0,
                    detected_media_type="unknown",
                    errors=errors,
                )
            size_bytes = content.stat().st_size
            try:
                calc_sha = calculate_sha256(content)
            except Exception as e:
                errors.append(f"Hashing failed: {e}")
                calc_sha = ""
            sample_bytes = None
            if size_bytes <= 1024:
                try:
                    sample_bytes = content.read_bytes()
                except Exception:
                    pass
        elif isinstance(content, bytes):
            size_bytes = len(content)
            calc_sha = calculate_sha256(content)
            sample_bytes = content[:1024]
        else:
            errors.append(f"Unsupported content type: {type(content)}")
            return ValidationResult(
                is_valid=False,
                calculated_sha256="",
                size_bytes=0,
                detected_media_type="unknown",
                errors=errors,
            )

        # 4. Check size constraints
        if self.disallow_empty and size_bytes == 0:
            errors.append("Evidence artifact is empty (0 bytes)")

        if size_bytes > self.max_file_size_bytes:
            errors.append(
                f"Evidence size ({size_bytes} bytes) exceeds limit ({self.max_file_size_bytes} bytes)"
            )

        # 5. Verify cryptographic hash match if expected hash was provided
        if expected_sha256:
            norm_expected = expected_sha256.strip().lower()
            if calc_sha != norm_expected:
                errors.append(
                    f"Cryptographic hash mismatch: expected {norm_expected}, got {calc_sha}"
                )

        # 6. Detect and validate media type
        detected_type = declared_media_type or self.detect_media_type(safe_name, sample_bytes)
        if self.allowed_types and detected_type not in self.allowed_types:
            # Allow fallback if text/plain or octet-stream is allowed
            if "text/plain" not in self.allowed_types and "application/octet-stream" not in self.allowed_types:
                warnings.append(f"Media type '{detected_type}' not in explicitly allowed list")

        return ValidationResult(
            is_valid=len(errors) == 0,
            calculated_sha256=calc_sha,
            size_bytes=size_bytes,
            detected_media_type=detected_type,
            errors=errors,
            warnings=warnings,
        )
