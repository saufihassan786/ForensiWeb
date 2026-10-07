"""Verification Test Suite for PHASE 06 — Evidence Collection.

Verifies:
- PHASE-06-F01: Evidence Storage (original, working, derived segregated layout, immutability)
- PHASE-06-F02: Evidence Metadata (manifest.json, ISO-8601 UTC timestamps, forensic metadata)
- PHASE-06-F03: Evidence Integrity Hashing (SHA-256 streaming digest, cryptographic verification)
- PHASE-06-F04: Evidence Ingestion (end-to-end atomic ingestion, canonical ID allocation)
- PHASE-06-F05: Evidence Validation (path traversal protection, size checks, MIME validation, hash check)
- PHASE-06-F06: Processing States (acquired, verified, parsed, corrupted state transitions)
- PHASE-06-F07: Evidence Retrieval (safe non-destructive reading, tamper detection)
- PHASE-06-F08: Evidence Chain Verification (case-level cryptographic audit, chain-of-custody report)
- Failure Scenarios: duplicates, hash mismatch, corrupted files, empty files, traversal attacks
"""

from __future__ import annotations

import os
import stat
from pathlib import Path
import pytest

from evidence.chain import EvidenceChainVerifier
from evidence.exceptions import (
    DuplicateEvidenceError,
    EvidenceIntegrityError,
    EvidenceNotFoundError,
    EvidenceStorageError,
    EvidenceValidationError,
)
from evidence.hasher import calculate_sha256, verify_sha256
from evidence.ingestion import EvidenceIngestionService
from evidence.manifest import EvidenceManifestManager, EvidenceMetadata
from evidence.retrieval import EvidenceRetrievalService
from evidence.storage import EvidenceStorage
from evidence.validation import EvidenceValidator


@pytest.fixture
def evidence_system(tmp_path: Path):
    """Instantiate fully wired isolated evidence components in a temporary sandbox."""
    storage = EvidenceStorage(root_dir=tmp_path / "evidence")
    validator = EvidenceValidator(max_file_size_bytes=5 * 1024 * 1024)  # 5 MB
    ingestion = EvidenceIngestionService(storage=storage, validator=validator)
    retrieval = EvidenceRetrievalService(storage=storage)
    verifier = EvidenceChainVerifier(storage=storage)
    return {
        "storage": storage,
        "validator": validator,
        "ingestion": ingestion,
        "retrieval": retrieval,
        "verifier": verifier,
        "root": tmp_path / "evidence",
    }


# ==============================================================================
# PHASE-06-F01: Evidence Storage & Immutability
# ==============================================================================

def test_p06_f01_storage_directory_layout(evidence_system):
    """Verify distinct separation of original, working, and derived directories."""
    storage = evidence_system["storage"]
    case_id = "CASE-2026-001"
    ev_id = "EV-A1B2C3D4"

    orig_dir = storage.get_case_original_dir(case_id, ev_id)
    work_dir = storage.get_case_working_dir(case_id, ev_id)
    deriv_dir = storage.get_case_derived_dir(case_id)

    assert "original" in str(orig_dir)
    assert "working" in str(work_dir)
    assert "derived" in str(deriv_dir)
    assert orig_dir != work_dir


def test_p06_f01_immutability_and_overwrite_protection(evidence_system):
    """Verify original files are made read-only and cannot be overwritten."""
    storage = evidence_system["storage"]
    case_id = "CASE-2026-001"
    ev_id = "EV-IMMUTABLE-01"
    filename = "web_access.log"
    content = b"172.28.0.5 - - [06/Oct/2026:14:30:00 +0000] GET / HTTP/1.1 200"

    saved_path = storage.save_original(case_id, ev_id, filename, content)
    assert saved_path.is_file()
    assert storage.is_read_only(saved_path)

    # Attempting to save over existing original must raise EvidenceStorageError
    with pytest.raises(EvidenceStorageError, match="Cannot overwrite immutable evidence"):
        storage.save_original(case_id, ev_id, filename, b"altered content")

    # Clean up permissions for temp directory teardown
    storage.enforce_read_only(saved_path)
    os.chmod(saved_path, stat.S_IWRITE | stat.S_IREAD)


def test_p06_f01_working_copy_separation(evidence_system):
    """Verify working copy is a verified replica and does not mutate the original."""
    storage = evidence_system["storage"]
    case_id = "CASE-2026-001"
    ev_id = "EV-WORK-01"
    filename = "syslog.log"
    orig_content = b"system startup complete"

    saved_orig = storage.save_original(case_id, ev_id, filename, orig_content)
    working_copy = storage.create_working_copy(case_id, ev_id, filename)

    assert working_copy.is_file()
    assert working_copy != saved_orig
    assert working_copy.read_bytes() == orig_content

    # Modifying working copy does not change original
    working_copy.write_bytes(b"modified by parser")
    assert saved_orig.read_bytes() == orig_content

    # Cleanup permissions
    os.chmod(saved_orig, stat.S_IWRITE | stat.S_IREAD)


# ==============================================================================
# PHASE-06-F02: Evidence Metadata & Manifest
# ==============================================================================

def test_p06_f02_manifest_creation_and_integrity(evidence_system):
    """Verify manifest.json generation and verification."""
    storage = evidence_system["storage"]
    case_id = "CASE-2026-001"
    ev_id = "EV-MANIFEST-01"
    filename = "audit.log"
    content = b"type=SYSCALL msg=audit(1728225065.120:101): exe=/bin/sh"

    saved_path = storage.save_original(case_id, ev_id, filename, content)
    sha = calculate_sha256(content)

    meta = EvidenceManifestManager.create_metadata(
        evidence_id=ev_id,
        case_id=case_id,
        filename=filename,
        source="system_audit",
        sha256=sha,
        size_bytes=len(content),
        media_type="text/x-log",
    )

    ev_dir = storage.get_case_original_dir(case_id, ev_id)
    manifest_path = EvidenceManifestManager.write_manifest(ev_dir, meta)
    assert manifest_path.is_file()

    loaded_meta = EvidenceManifestManager.read_manifest(ev_dir)
    assert loaded_meta.evidence_id == ev_id
    assert loaded_meta.sha256 == sha
    assert loaded_meta.size_bytes == len(content)
    assert loaded_meta.status == "acquired"

    # Integrity check passes
    assert EvidenceManifestManager.verify_manifest_integrity(ev_dir) is True

    # Cleanup permissions
    os.chmod(saved_path, stat.S_IWRITE | stat.S_IREAD)


# ==============================================================================
# PHASE-06-F03: Evidence Integrity Hashing
# ==============================================================================

def test_p06_f03_sha256_calculation_and_verification(tmp_path: Path):
    """Verify deterministic SHA-256 computation for bytes and files."""
    payload = b"ForensiWeb evidence artifact test payload"
    expected_hex = "bde9084713604181df5329964d767d30580c9b424aa53c9b91b718b598f4c0f9"

    # In-memory hashing
    assert calculate_sha256(payload) == expected_hex
    assert verify_sha256(payload, expected_hex) is True
    assert verify_sha256(payload, expected_hex.upper()) is True

    # File-based hashing
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(payload)
    assert calculate_sha256(test_file) == expected_hex
    assert verify_sha256(test_file, expected_hex) is True

    # Mismatch handling
    wrong_hash = "0" * 64
    assert verify_sha256(test_file, wrong_hash) is False
    with pytest.raises(EvidenceIntegrityError, match="hash mismatch"):
        verify_sha256(test_file, wrong_hash, raise_on_mismatch=True)


# ==============================================================================
# PHASE-06-F04: Evidence Ingestion Pipeline
# ==============================================================================

def test_p06_f04_end_to_end_ingestion(evidence_system):
    """Verify complete ingestion pipeline from raw log to verified store."""
    ingestion = evidence_system["ingestion"]
    storage = evidence_system["storage"]
    case_id = "CASE-LAB-101"
    raw_log = b"172.28.0.5 - - [06/Oct/2026:14:31:22 +0000] GET /view?page=../../../../etc/passwd 400"

    meta = ingestion.ingest(
        case_id=case_id,
        source="web_server",
        filename="nginx_access.log",
        content=raw_log,
        declared_media_type="text/x-log",
    )

    assert meta.evidence_id.startswith("EV-")
    assert meta.case_id == case_id
    assert meta.filename == "nginx_access.log"
    assert meta.size_bytes == len(raw_log)
    assert meta.status == "verified"
    assert meta.sha256 == calculate_sha256(raw_log)

    # Check disk layout
    orig_file = storage.get_case_original_dir(case_id, meta.evidence_id) / "nginx_access.log"
    working_file = storage.get_case_working_dir(case_id, meta.evidence_id) / "nginx_access.log"
    manifest_file = storage.get_case_original_dir(case_id, meta.evidence_id) / "manifest.json"

    assert orig_file.is_file()
    assert working_file.is_file()
    assert manifest_file.is_file()
    assert storage.is_read_only(orig_file)

    # Cleanup permissions
    os.chmod(orig_file, stat.S_IWRITE | stat.S_IREAD)


# ==============================================================================
# PHASE-06-F05: Evidence Validation
# ==============================================================================

def test_p06_f05_validation_path_traversal_prevention(evidence_system):
    """Verify directory traversal attempts in filename are rejected."""
    ingestion = evidence_system["ingestion"]
    case_id = "CASE-VAL-01"
    content = b"sample malicious filename test"

    with pytest.raises(EvidenceValidationError, match="Invalid or unsafe evidence filename"):
        ingestion.ingest(case_id=case_id, source="test", filename="../../etc/passwd", content=content)

    with pytest.raises(EvidenceValidationError, match="Invalid or unsafe evidence filename"):
        ingestion.ingest(case_id=case_id, source="test", filename="..\\windows\\system32\\cmd.exe", content=content)


def test_p06_f05_validation_empty_and_oversized_files(evidence_system):
    """Verify empty or oversized files are rejected."""
    ingestion = evidence_system["ingestion"]
    case_id = "CASE-VAL-02"

    # Empty file
    with pytest.raises(EvidenceValidationError, match="empty"):
        ingestion.ingest(case_id=case_id, source="test", filename="empty.log", content=b"")

    # Oversized file (> 5 MB limit configured in fixture)
    huge_payload = b"A" * (6 * 1024 * 1024)
    with pytest.raises(EvidenceValidationError, match="exceeds limit"):
        ingestion.ingest(case_id=case_id, source="test", filename="huge.log", content=huge_payload)


def test_p06_f05_validation_expected_hash_mismatch(evidence_system):
    """Verify ingestion rejects content that mismatches declared hash."""
    ingestion = evidence_system["ingestion"]
    case_id = "CASE-VAL-03"
    content = b"legitimate content"
    wrong_hash = "f" * 64

    with pytest.raises(EvidenceValidationError, match="Cryptographic hash mismatch"):
        ingestion.ingest(
            case_id=case_id,
            source="web",
            filename="auth.log",
            content=content,
            expected_sha256=wrong_hash,
        )


# ==============================================================================
# PHASE-06-F06: Processing States Lifecycle
# ==============================================================================

def test_p06_f06_processing_state_transitions(evidence_system):
    """Verify evidence status transitions: acquired -> verified -> parsed / corrupted."""
    ingestion = evidence_system["ingestion"]
    retrieval = evidence_system["retrieval"]
    case_id = "CASE-STATE-01"
    content = b"status transition telemetry data"

    meta = ingestion.ingest(case_id=case_id, source="sensor", filename="state.log", content=content)
    assert meta.status == "verified"

    # Transition to parsed after ingestion
    updated = retrieval.update_status(case_id, meta.evidence_id, "parsed")
    assert updated.status == "parsed"

    # Fetch again to verify persistence in manifest
    fetched = retrieval.get_metadata(case_id, meta.evidence_id)
    assert fetched.status == "parsed"

    # Cleanup permissions
    orig_path = retrieval.get_original_path(case_id, meta.evidence_id)
    os.chmod(orig_path, stat.S_IWRITE | stat.S_IREAD)


# ==============================================================================
# PHASE-06-F07: Evidence Retrieval & Tamper Detection
# ==============================================================================

def test_p06_f07_safe_retrieval_and_tamper_detection(evidence_system):
    """Verify non-destructive reading and detection of disk alteration."""
    ingestion = evidence_system["ingestion"]
    retrieval = evidence_system["retrieval"]
    case_id = "CASE-RET-01"
    content = b"pristine original log data"

    meta = ingestion.ingest(case_id=case_id, source="network", filename="traffic.pcap", content=content)

    # 1. Normal read returns exact bytes
    read_bytes = retrieval.read_original_bytes(case_id, meta.evidence_id)
    assert read_bytes == content

    # 2. Simulate malicious tampering on disk
    orig_file = retrieval.get_original_path(case_id, meta.evidence_id)
    os.chmod(orig_file, stat.S_IWRITE | stat.S_IREAD)
    orig_file.write_bytes(b"tampered content inserted by attacker")
    os.chmod(orig_file, stat.S_IREAD)

    # Subsequent retrieval must fail with EvidenceIntegrityError and mark corrupted
    with pytest.raises(EvidenceIntegrityError, match="Integrity check failed"):
        retrieval.read_original_bytes(case_id, meta.evidence_id)

    # Verify status changed to corrupted
    corrupt_meta = retrieval.get_metadata(case_id, meta.evidence_id)
    assert corrupt_meta.status == "corrupted"

    # Cleanup permissions
    os.chmod(orig_file, stat.S_IWRITE | stat.S_IREAD)


# ==============================================================================
# PHASE-06-F08: Evidence Chain Verification & Failure Scenarios
# ==============================================================================

def test_p06_f08_case_evidence_chain_audit(evidence_system):
    """Verify case-wide cryptographic chain-of-custody report."""
    ingestion = evidence_system["ingestion"]
    verifier = evidence_system["verifier"]
    retrieval = evidence_system["retrieval"]
    case_id = "CASE-CHAIN-01"

    # Ingest two valid artifacts
    m1 = ingestion.ingest(case_id=case_id, source="web", filename="access.log", content=b"log 1 content")
    m2 = ingestion.ingest(case_id=case_id, source="system", filename="audit.log", content=b"log 2 content")

    # Initial chain verification should be intact
    report = verifier.verify_case_chain(case_id)
    assert report.is_chain_intact is True
    assert report.total_artifacts == 2
    assert report.intact_artifacts == 2
    assert report.compromised_artifacts == 0

    # Tamper with m2
    orig_m2 = retrieval.get_original_path(case_id, m2.evidence_id)
    os.chmod(orig_m2, stat.S_IWRITE | stat.S_IREAD)
    orig_m2.write_bytes(b"tampered log 2 content")
    os.chmod(orig_m2, stat.S_IREAD)

    # Re-audit should report compromised artifact
    compromised_report = verifier.verify_case_chain(case_id)
    assert compromised_report.is_chain_intact is False
    assert compromised_report.intact_artifacts == 1
    assert compromised_report.compromised_artifacts == 1

    # Cleanup permissions
    p1 = retrieval.get_original_path(case_id, m1.evidence_id)
    os.chmod(p1, stat.S_IWRITE | stat.S_IREAD)
    os.chmod(orig_m2, stat.S_IWRITE | stat.S_IREAD)


def test_p06_duplicate_evidence_handling(evidence_system):
    """Verify duplicate evidence submission is blocked by default."""
    ingestion = evidence_system["ingestion"]
    case_id = "CASE-DUP-01"
    content = b"identical evidence byte stream"

    # First ingestion succeeds
    m1 = ingestion.ingest(case_id=case_id, source="web", filename="first.log", content=content)
    assert m1.status == "verified"

    # Duplicate ingestion fails with DuplicateEvidenceError
    with pytest.raises(DuplicateEvidenceError, match="Duplicate evidence"):
        ingestion.ingest(case_id=case_id, source="web", filename="second.log", content=content)

    # Permitted duplicates return existing metadata
    existing = ingestion.ingest(
        case_id=case_id,
        source="web",
        filename="second.log",
        content=content,
        allow_duplicates=True,
    )
    assert existing.evidence_id == m1.evidence_id

    # Cleanup permissions
    orig_file = evidence_system["retrieval"].get_original_path(case_id, m1.evidence_id)
    os.chmod(orig_file, stat.S_IWRITE | stat.S_IREAD)
