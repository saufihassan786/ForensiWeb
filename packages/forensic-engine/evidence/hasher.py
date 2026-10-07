"""Evidence Integrity Hashing Service (PHASE-06-F03).

Provides deterministic cryptographic SHA-256 hashing and verification
adhering to ISO/IEC 27037 and NIST SP 800-86 digital forensic standards.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Union

from .exceptions import EvidenceIntegrityError

DEFAULT_CHUNK_SIZE = 65536  # 64 KB streaming buffer


def calculate_sha256(target: Union[bytes, str, Path], chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Calculate cryptographic SHA-256 digest of in-memory bytes or a file on disk.

    Args:
        target: Raw bytes or Path/str to the target file.
        chunk_size: Stream buffer size in bytes for disk files.

    Returns:
        Lowercase hexadecimal SHA-256 digest string (64 characters).

    Raises:
        FileNotFoundError: If target path does not exist.
        ValueError: If target is invalid.
    """
    hasher = hashlib.sha256()

    if isinstance(target, bytes):
        hasher.update(target)
        return hasher.hexdigest().lower()

    path = Path(target)
    if not path.is_file():
        raise FileNotFoundError(f"Evidence file not found for hashing: {path}")

    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)

    return hasher.hexdigest().lower()


def verify_sha256(
    target: Union[bytes, str, Path],
    expected_hash: str,
    raise_on_mismatch: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> bool:
    """Verify cryptographic SHA-256 integrity against an expected digest.

    Args:
        target: Raw bytes or Path/str to the target file.
        expected_hash: Expected 64-character hex digest.
        raise_on_mismatch: If True, raises EvidenceIntegrityError on discrepancy.
        chunk_size: Stream buffer size in bytes for disk files.

    Returns:
        True if digests match, False otherwise.

    Raises:
        EvidenceIntegrityError: If raise_on_mismatch is True and digests differ.
    """
    actual_hash = calculate_sha256(target, chunk_size=chunk_size)
    expected_normalized = expected_hash.strip().lower()

    if actual_hash == expected_normalized:
        return True

    if raise_on_mismatch:
        raise EvidenceIntegrityError(
            f"Cryptographic hash mismatch: expected {expected_normalized}, calculated {actual_hash}",
            details={"expected_hash": expected_normalized, "actual_hash": actual_hash},
        )

    return False


class StreamHasher:
    """Helper class providing static methods for stream hashing."""

    @staticmethod
    def compute_file_sha256(path: Union[str, Path], chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
        return calculate_sha256(path, chunk_size=chunk_size)

    @staticmethod
    def calculate_sha256(target: Union[bytes, str, Path], chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
        return calculate_sha256(target, chunk_size=chunk_size)

    @staticmethod
    def verify_sha256(
        target: Union[bytes, str, Path],
        expected_hash: str,
        raise_on_mismatch: bool = False,
    ) -> bool:
        return verify_sha256(target, expected_hash, raise_on_mismatch=raise_on_mismatch)

