"""Forensic Evidence Collection Exceptions (PHASE-06)."""

from __future__ import annotations


class EvidenceError(Exception):
    """Base exception for all evidence-related failures."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EvidenceIntegrityError(EvidenceError):
    """Raised when an evidence cryptographic hash mismatches or original is tampered."""


class DuplicateEvidenceError(EvidenceError):
    """Raised when duplicate evidence is submitted under the same case."""


class CorruptedEvidenceError(EvidenceError):
    """Raised when evidence content is damaged, truncated, or unreadable."""


class EvidenceNotFoundError(EvidenceError):
    """Raised when an evidence artifact or metadata record is not found."""


class EvidenceValidationError(EvidenceError):
    """Raised when evidence metadata or content fails validation rules."""


class EvidenceStorageError(EvidenceError):
    """Raised when filesystem storage operations fail or immutability is violated."""
