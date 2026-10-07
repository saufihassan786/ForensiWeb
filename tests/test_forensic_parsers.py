"""Verification Test Suite for PHASE 07 — Forensic Processing Engine.

Verifies:
- PHASE-07-F01: Parser Framework (SourceLocation, EvidenceReference, line/byte offsets)
- PHASE-07-F02: Source Detection (Web logs, App logs, Audit logs, Environment dumps)
- PHASE-07-F03: Web Access Log Parser (CLF, query params, attack indicators)
- PHASE-07-F04: Application Log Parser (timestamps, severity levels, modules)
- PHASE-07-F05: System/Process Evidence Parser (auditd syscalls, exe, ppid/pid, environment)
- PHASE-07-F06: Parser Error Handling (graceful exception handling)
- PHASE-07-F07: Malformed Evidence Handling (malformed lines preserved with status="malformed")
- PHASE-07-F08: Processing Verification (validity checks and evidence reference fidelity)
"""

from __future__ import annotations

from pathlib import Path
import pytest

from parsers.app_parser import ApplicationLogParser
from parsers.auditd_parser import AuditdParser, EnvironmentDumpParser
from parsers.detector import SourceDetector
from parsers.models import EvidenceReference, SourceLocation
from parsers.registry import ParserRegistry
from parsers.web_parser import WebAccessLogParser


@pytest.fixture
def parser_registry() -> ParserRegistry:
    return ParserRegistry()


# ==============================================================================
# PHASE-07-F01: Parser Framework & Offset Tracking
# ==============================================================================

def test_p07_f01_line_and_byte_offset_accuracy(parser_registry: ParserRegistry):
    """Verify that parsers calculate strictly accurate byte offsets for each line."""
    log_content = (
        '127.0.0.1 - - [06/Oct/2026:14:30:10 +0000] "GET /index HTTP/1.1" 200 100\n'
        '127.0.0.1 - - [06/Oct/2026:14:30:15 +0000] "GET /about HTTP/1.1" 200 200\n'
    )
    report = parser_registry.parse_artifact(
        content=log_content,
        filename="access.log",
        evidence_id="EV-OFFSET-01",
        sha256="0" * 64,
        source_type="web_access_log",
    )

    assert report.total_lines == 2
    assert report.valid_count == 2
    rec1 = report.records[0]
    rec2 = report.records[1]

    # Verify line 1 offsets
    assert rec1.source_location.line_number == 1
    assert rec1.source_location.byte_offset_start == 0
    line1_len = len(log_content.splitlines(keepends=True)[0].encode("utf-8"))
    assert rec1.source_location.byte_offset_end == line1_len

    # Verify line 2 starts where line 1 ended
    assert rec2.source_location.line_number == 2
    assert rec2.source_location.byte_offset_start == line1_len

    # Traceability to evidence reference
    assert rec1.evidence_ref.evidence_id == "EV-OFFSET-01"
    assert rec1.evidence_ref.filename == "access.log"


# ==============================================================================
# PHASE-07-F02: Source Detection
# ==============================================================================

def test_p07_f02_source_detection_heuristics():
    """Verify automatic classification of evidence source types."""
    web_sample = '172.28.0.5 - - [06/Oct/2026:14:31:22 +0000] "GET /view HTTP/1.1" 200 500 "-" "curl/7.88.1"'
    app_sample = '[2026-10-06 14:31:22,810] [WARNING] [app.security] Path traversal attempt detected'
    audit_sample = 'type=SYSCALL msg=audit(1728225065.120:101): arch=c000003e syscall=59 success=yes comm="sh"'
    env_sample = '{"PATH": "/tmp/bin:/usr/bin", "USER": "www-data"}'

    assert SourceDetector.detect("access.log", web_sample).source_type == "web_access_log"
    assert SourceDetector.detect("error.log", app_sample).source_type == "app_log"
    assert SourceDetector.detect("auditd.log", audit_sample).source_type == "system_audit"
    assert SourceDetector.detect("env.json", env_sample).source_type == "env_dump"


# ==============================================================================
# PHASE-07-F03: Web Access Log Parser
# ==============================================================================

def test_p07_f03_web_parser_execution(sample_raw_logs: dict, parser_registry: ParserRegistry):
    """Verify parsing of sample Nginx access log from tests/fixtures."""
    access_log = sample_raw_logs.get("access")
    assert access_log is not None

    report = parser_registry.parse_artifact(
        content=access_log,
        filename="sample_access.log",
        evidence_id="EV-WEB-01",
        sha256="a" * 64,
    )

    assert report.is_successful
    assert report.valid_count >= 5

    # Inspect LFI line with traversal indicator
    lfi_record = next(r for r in report.records if "passwd" in r.raw_content)
    assert lfi_record.fields["client_ip"] == "172.28.0.5"
    assert lfi_record.fields["http_method"] == "GET"
    assert "path_traversal" in lfi_record.fields["indicators"]
    assert lfi_record.fields["status_code"] == 400

    # Inspect log poisoning user agent line
    poison_record = next(r for r in report.records if "SIMULATED_POISON" in r.raw_content)
    assert "log_poisoning_payload" in poison_record.fields["indicators"]

    # Inspect web shell invocation with query parameter
    rce_record = next(r for r in report.records if "cmd=id" in r.raw_content)
    assert "cmd" in rce_record.fields["query_params"]
    assert rce_record.fields["query_params"]["cmd"] == "id"
    assert "command_execution_parameter" in rce_record.fields["indicators"]


# ==============================================================================
# PHASE-07-F04: Application Log Parser
# ==============================================================================

def test_p07_f04_app_log_parser_execution(sample_raw_logs: dict, parser_registry: ParserRegistry):
    """Verify parsing of sample Flask/app log from tests/fixtures."""
    error_log = sample_raw_logs.get("error")
    assert error_log is not None

    report = parser_registry.parse_artifact(
        content=error_log,
        filename="sample_error.log",
        evidence_id="EV-APP-01",
        sha256="b" * 64,
    )

    assert report.is_successful
    assert report.valid_count >= 5

    # Check warning level and traversal detection
    warn_rec = next(r for r in report.records if r.fields.get("level") == "WARNING")
    assert warn_rec.fields["logger"] == "app.security"
    assert "path_traversal_detection" in warn_rec.fields["indicators"]
    assert warn_rec.timestamp_utc is not None

    # Check error level and child process detection
    err_rec = next(r for r in report.records if r.fields.get("level") == "ERROR")
    assert "child_process_spawn" in err_rec.fields["indicators"]


# ==============================================================================
# PHASE-07-F05: System/Process Evidence Parser
# ==============================================================================

def test_p07_f05_auditd_parser_execution(sample_raw_logs: dict, parser_registry: ParserRegistry):
    """Verify parsing of sample auditd log from tests/fixtures."""
    audit_log = sample_raw_logs.get("auditd")
    assert audit_log is not None

    report = parser_registry.parse_artifact(
        content=audit_log,
        filename="sample_auditd.log",
        evidence_id="EV-AUD-01",
        sha256="c" * 64,
    )

    assert report.is_successful
    assert report.valid_count >= 5

    # Check syscall record
    syscall_rec = next(r for r in report.records if r.fields.get("record_type") == "SYSCALL")
    assert syscall_rec.fields["syscall"] == 59
    assert syscall_rec.fields["comm"] == "sh"
    assert syscall_rec.fields["ppid"] == 1420
    assert syscall_rec.fields["pid"] == 2105
    assert "shell_spawn" in syscall_rec.fields["indicators"]

    # Check path record targeting /tmp/bin/su
    path_rec = next(r for r in report.records if r.fields.get("name") == "/tmp/bin/su")
    assert "temporary_directory_execution" in path_rec.fields["indicators"]
    assert "privilege_escalation_target" in path_rec.fields["indicators"]


# ==============================================================================
# PHASE-07-F06 & F07: Error Handling & Malformed Evidence Preservation
# ==============================================================================

def test_p07_f06_and_f07_malformed_evidence_preserved(parser_registry: ParserRegistry):
    """Verify that corrupt or malformed log lines are preserved with status='malformed'."""
    corrupted_log = (
        '127.0.0.1 - - [06/Oct/2026:14:30:10 +0000] "GET /valid HTTP/1.1" 200 100\n'
        'CORRUPT_GARBAGE_UNPARSABLE_LINE_WITH_NO_STRUCTURE\n'
        'ANOTHER_MALFORMED_RECORD\n'
        '127.0.0.1 - - [06/Oct/2026:14:30:20 +0000] "GET /valid2 HTTP/1.1" 200 100\n'
    )

    report = parser_registry.parse_artifact(
        content=corrupted_log,
        filename="corrupted.log",
        evidence_id="EV-CORRUPT-01",
        sha256="d" * 64,
        source_type="web_access_log",
    )

    assert report.total_lines == 4
    assert report.valid_count == 2
    assert report.malformed_count == 2

    # Malformed lines must be in records with status="malformed" and detailed error
    malformed_records = [r for r in report.records if r.status == "malformed"]
    assert len(malformed_records) == 2
    assert malformed_records[0].source_location.line_number == 2
    assert malformed_records[0].error_message is not None
    assert "CORRUPT_GARBAGE" in malformed_records[0].raw_content


# ==============================================================================
# PHASE-07-F08: Processing Verification
# ==============================================================================

def test_p07_f08_processing_verification_integrity(parser_registry: ParserRegistry):
    """Verify that all parsed records strictly pass traceability and contract checks."""
    content = '[2026-10-06 14:30:00,102] [INFO] [app] System initialized'
    report = parser_registry.parse_artifact(
        content=content,
        filename="app.log",
        evidence_id="EV-VERIFY-01",
        sha256="e" * 64,
    )

    assert parser_registry.verify_processing_records(report) is True
    record = report.records[0]
    assert record.source_location.line_number >= 1
    assert record.source_location.byte_offset_start < record.source_location.byte_offset_end
    assert record.evidence_ref.evidence_id == "EV-VERIFY-01"
