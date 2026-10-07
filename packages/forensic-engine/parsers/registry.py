"""Parser Registry and Dispatch Engine (PHASE-07-F01, F06, F07, F08).

Manages extensible parser registration, automatic source detection dispatch,
malformed record preservation, and processing integrity verification.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from .app_parser import ApplicationLogParser
from .auditd_parser import AuditdParser, EnvironmentDumpParser
from .base import BaseParser
from .detector import SourceDetectionResult, SourceDetector
from .models import EvidenceReference, ParseReport, ParsedRecord, SourceLocation
from .web_parser import WebAccessLogParser

logger = logging.getLogger("forensiweb.parsers.registry")


class GenericTextParser(BaseParser):
    """Fallback parser for unstructured or unclassified forensic text logs."""

    @property
    def parser_name(self) -> str:
        return "GenericTextParser"

    @property
    def supported_source_types(self) -> List[str]:
        return ["generic_text", "unknown", "text_log"]

    def can_parse(self, content_sample: str) -> bool:
        return True

    def parse_line(
        self,
        line: str,
        line_number: int,
        byte_start: int,
        byte_end: int,
        evidence_ref: EvidenceReference,
    ) -> ParsedRecord:
        import uuid
        return ParsedRecord(
            record_id=f"REC-GEN-{uuid.uuid4().hex[:8].upper()}",
            parser_name=self.parser_name,
            source_type="generic_text",
            timestamp_raw=None,
            timestamp_utc=None,
            source_location=SourceLocation(
                line_number=line_number,
                byte_offset_start=byte_start,
                byte_offset_end=byte_end,
            ),
            evidence_ref=evidence_ref,
            fields={"text": line},
            raw_content=line,
            status="valid",
            error_message=None,
        )


class ParserRegistry:
    """Central registry and dispatch coordinator for evidence parsers."""

    def __init__(self) -> None:
        self._parsers: Dict[str, BaseParser] = {}
        self._source_type_map: Dict[str, BaseParser] = {}

        # Register standard default parsers
        self.register(WebAccessLogParser())
        self.register(ApplicationLogParser())
        self.register(AuditdParser())
        self.register(EnvironmentDumpParser())
        self.register(GenericTextParser())

    def register(self, parser: BaseParser) -> None:
        """Register a parser instance."""
        self._parsers[parser.parser_name] = parser
        for st in parser.supported_source_types:
            self._source_type_map[st] = parser

    def get_parser(self, name_or_source_type: str) -> Optional[BaseParser]:
        """Lookup parser by name or source type."""
        if name_or_source_type in self._parsers:
            return self._parsers[name_or_source_type]
        return self._source_type_map.get(name_or_source_type)

    def verify_processing_records(self, report: ParseReport) -> bool:
        """PHASE-07-F08: Verify that every parsed record satisfies integrity and traceability."""
        for rec in report.records:
            if not rec.record_id:
                return False
            if rec.source_location.line_number < 1:
                return False
            if rec.source_location.byte_offset_start > rec.source_location.byte_offset_end:
                return False
            if not rec.evidence_ref.evidence_id:
                return False
            if not rec.evidence_ref.sha256:
                return False
        return True

    def parse_artifact(
        self,
        content: str,
        filename: str,
        evidence_id: str,
        sha256: str,
        source_type: Optional[str] = None,
    ) -> ParseReport:
        """Analyze evidence content, auto-detect parser if needed, and execute extraction."""
        active_parser: Optional[BaseParser] = None

        # 1. Resolve parser from explicit source_type if specified
        if source_type and source_type != "unknown":
            active_parser = self.get_parser(source_type)

        # 2. Otherwise auto-detect from content heuristics (PHASE-07-F02)
        if active_parser is None:
            detection: SourceDetectionResult = SourceDetector.detect(
                filename=filename,
                content_sample=content[:4096],
            )
            active_parser = self.get_parser(detection.recommended_parser) or self.get_parser(detection.source_type)
            if source_type is None or source_type == "unknown":
                source_type = detection.source_type

        # 3. Fallback to generic text parser
        if active_parser is None:
            active_parser = self._parsers["GenericTextParser"]
            source_type = source_type or "generic_text"

        # 4. Execute parsing with byte-level offset tracking
        report = active_parser.parse_content(
            content=content,
            evidence_id=evidence_id,
            filename=filename,
            sha256=sha256,
            source_type=source_type,
        )

        # 5. Verify processing traceability (PHASE-07-F08)
        self.verify_processing_records(report)

        return report
