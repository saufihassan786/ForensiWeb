"""Evidence Storage and Preservation Subsystem (PHASE-06-F01).

Implements strict forensic separation between:
1. Original Store: Read-only, cryptographically verified immutable artifacts.
2. Working Store: Working copies generated for non-destructive parsing.
3. Derived Store: Structured analysis artifacts and normalizations.

Adheres to ISO/IEC 27037 digital forensic standards.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Optional, Union

from .exceptions import EvidenceNotFoundError, EvidenceStorageError
from .hasher import calculate_sha256, verify_sha256


class EvidenceStorage:
    """Manages segregated evidence directories and enforces artifact immutability."""

    def __init__(self, root_dir: Union[str, Path] = "data/evidence") -> None:
        self.root_dir = Path(root_dir).resolve()
        self.original_dir = self.root_dir / "original"
        self.working_dir = self.root_dir / "working"
        self.derived_dir = self.root_dir / "derived"

        # Ensure base directories exist
        for d in (self.original_dir, self.working_dir, self.derived_dir):
            d.mkdir(parents=True, exist_ok=True)

    def get_case_original_dir(self, case_id: str, evidence_id: Optional[str] = None) -> Path:
        """Return directory path for pristine original evidence."""
        p = self.original_dir / case_id
        if evidence_id:
            p = p / evidence_id
        return p

    def get_case_working_dir(self, case_id: str, evidence_id: Optional[str] = None) -> Path:
        """Return directory path for mutable working copies."""
        p = self.working_dir / case_id
        if evidence_id:
            p = p / evidence_id
        return p

    def get_case_derived_dir(self, case_id: str) -> Path:
        """Return directory path for derived analytical outputs."""
        return self.derived_dir / case_id

    @staticmethod
    def enforce_read_only(file_path: Path) -> None:
        """Mark a file as strictly read-only on both POSIX and Windows filesystems."""
        if not file_path.is_file():
            return
        # Set read-only permission (read-only for user, group, others)
        mode = os.stat(file_path).st_mode
        # Remove write bits: S_IWUSR, S_IWGRP, S_IWOTH
        readonly_mode = mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        # Ensure at least read permission
        readonly_mode |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        os.chmod(file_path, readonly_mode)

    @staticmethod
    def is_read_only(file_path: Path) -> bool:
        """Check whether a file has write permissions revoked."""
        if not file_path.is_file():
            return False
        mode = os.stat(file_path).st_mode
        return not bool(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))

    def save_original(
        self,
        case_id: str,
        evidence_id: str,
        filename: str,
        content: Union[bytes, str, Path],
    ) -> Path:
        """Store an artifact into the immutable original evidence store.

        Atomic write via temporary file, followed by applying read-only attributes.
        Fails if destination already exists to preserve pristine immutability.
        """
        dest_dir = self.get_case_original_dir(case_id, evidence_id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename

        if dest_path.exists():
            raise EvidenceStorageError(
                f"Cannot overwrite immutable evidence at {dest_path}",
                details={"case_id": case_id, "evidence_id": evidence_id, "filename": filename},
            )

        # Write atomically via temp file in the same parent directory
        temp_fd, temp_path_str = tempfile.mkstemp(dir=dest_dir, prefix=".upload_tmp_")
        temp_path = Path(temp_path_str)

        try:
            with open(temp_fd, "wb") as f:
                if isinstance(content, bytes):
                    f.write(content)
                elif isinstance(content, str):
                    f.write(content.encode("utf-8"))
                elif isinstance(content, Path):
                    with content.open("rb") as src:
                        shutil.copyfileobj(src, f)
                else:
                    raise TypeError(f"Unsupported content type: {type(content)}")

            # Move temp file to final destination
            temp_path.replace(dest_path)
            # Enforce read-only permissions
            self.enforce_read_only(dest_path)
            return dest_path
        except Exception as exc:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise EvidenceStorageError(f"Failed to persist original evidence: {exc}") from exc

    def create_working_copy(
        self,
        case_id: str,
        evidence_id: str,
        filename: str,
    ) -> Path:
        """Create a verified working copy from the original store for safe parser consumption."""
        original_path = self.get_case_original_dir(case_id, evidence_id) / filename
        if not original_path.is_file():
            raise EvidenceNotFoundError(
                f"Original evidence artifact not found at {original_path}",
                details={"case_id": case_id, "evidence_id": evidence_id, "filename": filename},
            )

        working_dest_dir = self.get_case_working_dir(case_id, evidence_id)
        working_dest_dir.mkdir(parents=True, exist_ok=True)
        working_path = working_dest_dir / filename

        # Copy original bytes to working destination
        shutil.copy2(original_path, working_path)

        # Ensure working copy is writable for parsing annotations if necessary
        mode = os.stat(working_path).st_mode
        os.chmod(working_path, mode | stat.S_IWUSR)

        # Cryptographically verify that the working copy is identical to the original
        verify_sha256(working_path, calculate_sha256(original_path), raise_on_mismatch=True)
        return working_path

    def get_original_path(self, case_id: str, evidence_id: str, filename: str) -> Path:
        """Resolve path to an original artifact, ensuring it exists."""
        p = self.get_case_original_dir(case_id, evidence_id) / filename
        if not p.is_file():
            raise EvidenceNotFoundError(f"Original evidence file not found: {p}")
        return p

    def get_working_path(
        self,
        case_id: str,
        evidence_id: str,
        filename: str,
        auto_create: bool = True,
    ) -> Path:
        """Resolve path to a working copy artifact, creating it if requested."""
        p = self.get_case_working_dir(case_id, evidence_id) / filename
        if not p.is_file():
            if auto_create:
                return self.create_working_copy(case_id, evidence_id, filename)
            raise EvidenceNotFoundError(f"Working copy file not found: {p}")
        return p

    def list_original_files(self, case_id: str) -> List[Path]:
        """List all preserved pristine original evidence files for a case."""
        case_orig_dir = self.get_case_original_dir(case_id)
        if not case_orig_dir.exists():
            return []
        files: List[Path] = []
        for p in case_orig_dir.rglob("*"):
            if p.is_file():
                files.append(p)
        return files


