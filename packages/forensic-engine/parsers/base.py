"""Base Parser Framework (PHASE-07-F01).

Establishes the extensible interface and offset-tracking pipeline for all
domain-specific forensic log parsers.
"""

from __future__ import annotations

import abc
import time
import uuid
from typing import List, Optional

from .models import EvidenceReference, ParseReport, ParsedRecord, SourceLocation


class BaseParser(abc.ABC):
    """Abstract base class for all forensic evidence parsers."""

    @property
    @abc.abstractmethod
    def parser_name(self) -> str:
        """Unique parser identifier."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def supported_source_types(self) -> List[str]:
        """List of source types handled by this parser."""
        raise NotImplementedError

    @abc.abstractmethod
    def can_parse(self, content_sample: str) -> bool:
        """Heuristic check to determine if parser can handle the provided sample."""
        raise NotImplementedError

    @abc.abstractmethod
    def parse_line(
        self,
        line: str,
        line_number: int,
        byte_start: int,
        byte_end: int,
        evidence_ref: EvidenceReference,
    ) -> ParsedRecord:
        """Parse an individual evidence line into a structured record."""
        raise NotImplementedError

    def parse_content(
        self,
        content: str,
        evidence_id: str,
        filename: str,
        sha256: str,
        source_type: Optional[str] = None,
    ) -> ParseReport:
        """Parse entire content string while computing microsecond execution time and byte offsets.

        Preserves malformed lines to guarantee evidence fidelity without data loss.
        """
        start_time = time.perf_counter()
        evidence_ref = EvidenceReference(
            evidence_id=evidence_id,
            filename=filename,
            sha256=sha256,
        )

        resolved_source_type = source_type or (
            self.supported_source_types[0] if self.supported_source_types else "unknown"
        )

        records: List[ParsedRecord] = []
        errors: List[dict] = []
        valid_count = 0
        malformed_count = 0

        # Encode content to bytes to track exact byte offsets
        content_bytes = content.encode("utf-8")
        current_offset = 0
        line_number = 1

        # Process line by line preserving line break bytes
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)

        for line in lines:
            line_bytes_len = len(line.encode("utf-8"))
            byte_start = current_offset
            byte_end = current_offset + line_bytes_len
            current_offset = byte_end

            # Strip trailing newline for clean parsing
            stripped_line = line.rstrip("\r\n")

            if not stripped_line.strip():
                # Blank lines are skipped or preserved with minimal overhead
                line_number += 1
                continue

            try:
                record = self.parse_line(
                    line=stripped_line,
                    line_number=line_number,
                    byte_start=byte_start,
                    byte_end=byte_end,
                    evidence_ref=evidence_ref,
                )
                records.append(record)
                if record.status == "valid":
                    valid_count += 1
                else:
                    malformed_count += 1
                    if record.error_message:
                        errors.append({
                            "line_number": line_number,
                            "error": record.error_message,
                            "raw": stripped_line[:200],
                        })
            except Exception as exc:
                malformed_count += 1
                rec_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
                malformed_record = ParsedRecord(
                    record_id=rec_id,
                    parser_name=self.parser_name,
                    source_type=resolved_source_type,
                    timestamp_raw=None,
                    timestamp_utc=None,
                    source_location=SourceLocation(
                        line_number=line_number,
                        byte_offset_start=byte_start,
                        byte_offset_end=byte_end,
                    ),
                    evidence_ref=evidence_ref,
                    fields={},
                    raw_content=stripped_line,
                    status="malformed",
                    error_message=str(exc),
                )
                records.append(malformed_record)
                errors.append({
                    "line_number": line_number,
                    "error": str(exc),
                    "raw": stripped_line[:200],
                })

            line_number += 1

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return ParseReport(
            parser_name=self.parser_name,
            source_type=resolved_source_type,
            evidence_id=evidence_id,
            filename=filename,
            total_lines=total_lines,
            valid_count=valid_count,
            malformed_count=malformed_count,
            records=records,
            errors=errors,
            parse_duration_ms=round(elapsed_ms, 3),
        )
