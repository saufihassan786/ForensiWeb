"""Application Log Parser (PHASE-07-F04).

Extracts structured events, log levels, module namespaces, and security warnings
from standard Python, Flask, and microservice log records.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import BaseParser
from .models import EvidenceReference, ParsedRecord, SourceLocation


class ApplicationLogParser(BaseParser):
    """Parser for structured application and security runtime logs."""

    # [2026-10-06 14:31:22,810] [WARNING] [app.security] Path traversal attempt detected: '../../../../etc/passwd'
    APP_LOG_REGEX = re.compile(
        r'^\[(?P<time>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[,\.]\d{3})\]\s+'
        r'\[(?P<level>[A-Z]+)\]\s+'
        r'\[(?P<logger>[\w\.\-]+)\]\s+'
        r'(?P<message>.*)$'
    )

    @property
    def parser_name(self) -> str:
        return "ApplicationLogParser"

    @property
    def supported_source_types(self) -> List[str]:
        return ["app_log", "application", "flask_log", "error_log"]

    def can_parse(self, content_sample: str) -> bool:
        return bool(self.APP_LOG_REGEX.search(content_sample))

    @staticmethod
    def parse_app_datetime(time_str: str) -> Optional[str]:
        """Convert '2026-10-06 14:31:22,810' to ISO-8601 UTC timestamp."""
        try:
            clean_time = time_str.replace(",", ".")
            dt = datetime.strptime(clean_time, "%Y-%m-%d %H:%M:%S.%f")
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            return None

    def parse_line(
        self,
        line: str,
        line_number: int,
        byte_start: int,
        byte_end: int,
        evidence_ref: EvidenceReference,
    ) -> ParsedRecord:
        """Parse an application log line into a structured record."""
        rec_id = f"REC-APP-{uuid.uuid4().hex[:8].upper()}"
        location = SourceLocation(
            line_number=line_number,
            byte_offset_start=byte_start,
            byte_offset_end=byte_end,
        )

        match = self.APP_LOG_REGEX.match(line)
        if not match:
            return ParsedRecord(
                record_id=rec_id,
                parser_name=self.parser_name,
                source_type="app_log",
                timestamp_raw=None,
                timestamp_utc=None,
                source_location=location,
                evidence_ref=evidence_ref,
                fields={},
                raw_content=line,
                status="malformed",
                error_message="Line does not match Application Log pattern [YYYY-MM-DD HH:MM:SS,mmm] [LEVEL] [LOGGER] MSG",
            )

        data = match.groupdict()
        raw_time = data.get("time")
        iso_time = self.parse_app_datetime(raw_time) if raw_time else None
        level = (data.get("level") or "INFO").upper()
        logger_name = data.get("logger") or "root"
        message = data.get("message") or ""

        # Identify application security indicators
        indicators: List[str] = []
        msg_lower = message.lower()
        if "traversal" in msg_lower or "../" in msg_lower:
            indicators.append("path_traversal_detection")
        if "spawn" in msg_lower or "child process" in msg_lower:
            indicators.append("child_process_spawn")
        if "poison" in msg_lower:
            indicators.append("log_poisoning_alert")

        fields: Dict[str, Any] = {
            "level": level,
            "logger": logger_name,
            "message": message,
            "indicators": indicators,
        }

        return ParsedRecord(
            record_id=rec_id,
            parser_name=self.parser_name,
            source_type="app_log",
            timestamp_raw=raw_time,
            timestamp_utc=iso_time,
            source_location=location,
            evidence_ref=evidence_ref,
            fields=fields,
            raw_content=line,
            status="valid",
            error_message=None,
        )
