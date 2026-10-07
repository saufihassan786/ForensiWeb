"""Data Models for Forensic Processing Engine (PHASE-07-F01).

Defines structured records, source locations, evidence references,
and parse audit reports to ensure absolute evidence traceability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SourceLocation:
    """Exact byte and line offsets within the original evidence file."""

    line_number: int
    byte_offset_start: int
    byte_offset_end: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceReference:
    """Cryptographic link to the originating evidence artifact."""

    evidence_id: str
    filename: str
    sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParsedRecord:
    """Structured forensic record extracted by a parser."""

    record_id: str
    parser_name: str
    source_type: str
    timestamp_raw: Optional[str]
    timestamp_utc: Optional[str]
    source_location: SourceLocation
    evidence_ref: EvidenceReference
    fields: Dict[str, Any]
    raw_content: str
    status: str = "valid"  # valid, malformed, partial
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParseReport:
    """Comprehensive parser execution audit report."""

    parser_name: str
    source_type: str
    evidence_id: str
    filename: str
    total_lines: int
    valid_count: int
    malformed_count: int
    records: List[ParsedRecord] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    parse_duration_ms: float = 0.0

    @property
    def is_successful(self) -> bool:
        """True if at least one valid record was produced and parser did not crash."""
        return self.valid_count > 0 or (self.total_lines == 0 and self.malformed_count == 0)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
