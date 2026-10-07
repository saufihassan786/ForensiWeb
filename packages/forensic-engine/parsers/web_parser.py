"""Web Access Log Parser (PHASE-07-F03).

Extracts HTTP methods, paths, status codes, user agents, query parameters,
and attack indicators from Combined and Common Log Format records.
"""

from __future__ import annotations

import re
import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import BaseParser
from .models import EvidenceReference, ParsedRecord, SourceLocation


class WebAccessLogParser(BaseParser):
    """Parser for Nginx and Apache HTTP access logs."""

    # Combined Log Format: 127.0.0.1 - - [06/Oct/2026:14:30:10 +0000] "GET / HTTP/1.1" 200 4522 "referer" "user_agent"
    COMBINED_LOG_REGEX = re.compile(
        r'^(?P<ip>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+'
        r'\[(?P<time>[^\]]+)\]\s+'
        r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)(?:\s+(?P<protocol>HTTP/[0-9.]+))?"\s+'
        r'(?P<status>\d{3})\s+(?P<bytes>\S+)'
        r'(?:\s+"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)")?'
    )

    @property
    def parser_name(self) -> str:
        return "WebAccessLogParser"

    @property
    def supported_source_types(self) -> List[str]:
        return ["web_access_log", "web_server", "nginx_access", "apache_access"]

    def can_parse(self, content_sample: str) -> bool:
        return bool(self.COMBINED_LOG_REGEX.search(content_sample))

    @staticmethod
    def parse_clf_datetime(time_str: str) -> Optional[str]:
        """Convert Common Log Format timestamp (e.g. 06/Oct/2026:14:31:22 +0000) to ISO-8601 UTC."""
        try:
            # 06/Oct/2026:14:31:22 +0000
            dt = datetime.strptime(time_str, "%d/%b/%Y:%H:%M:%S %z")
            return dt.astimezone(timezone.utc).isoformat()
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
        """Parse a single web log line into a structured record."""
        rec_id = f"REC-WEB-{uuid.uuid4().hex[:8].upper()}"
        location = SourceLocation(
            line_number=line_number,
            byte_offset_start=byte_start,
            byte_offset_end=byte_end,
        )

        match = self.COMBINED_LOG_REGEX.match(line)
        if not match:
            return ParsedRecord(
                record_id=rec_id,
                parser_name=self.parser_name,
                source_type="web_access_log",
                timestamp_raw=None,
                timestamp_utc=None,
                source_location=location,
                evidence_ref=evidence_ref,
                fields={},
                raw_content=line,
                status="malformed",
                error_message="Line does not match Combined or Common Log Format regex",
            )

        data = match.groupdict()
        raw_time = data.get("time")
        iso_time = self.parse_clf_datetime(raw_time) if raw_time else None

        raw_path = data.get("path") or ""
        parsed_url = urllib.parse.urlparse(raw_path)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Flatten single query parameter values for cleaner forensic analysis
        flat_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        user_agent = data.get("user_agent") or ""
        bytes_val = int(data["bytes"]) if data.get("bytes", "").isdigit() else 0
        status_val = int(data["status"]) if data.get("status", "").isdigit() else 0

        # Forensic indicators
        indicators: List[str] = []
        if ".." in raw_path:
            indicators.append("path_traversal")
        ua_lower = user_agent.lower()
        if "<?php" in user_agent or "system(" in user_agent or "poison" in ua_lower:
            indicators.append("log_poisoning_payload")
        if "cmd=" in raw_path or "cmd" in flat_params:
            indicators.append("command_execution_parameter")

        fields: Dict[str, Any] = {
            "client_ip": data.get("ip"),
            "ident": data.get("ident"),
            "auth_user": data.get("user"),
            "http_method": data.get("method"),
            "uri_path": parsed_url.path,
            "raw_uri": raw_path,
            "query_params": flat_params,
            "http_protocol": data.get("protocol"),
            "status_code": status_val,
            "response_bytes": bytes_val,
            "referer": data.get("referer"),
            "user_agent": user_agent,
            "indicators": indicators,
        }

        return ParsedRecord(
            record_id=rec_id,
            parser_name=self.parser_name,
            source_type="web_access_log",
            timestamp_raw=raw_time,
            timestamp_utc=iso_time,
            source_location=location,
            evidence_ref=evidence_ref,
            fields=fields,
            raw_content=line,
            status="valid",
            error_message=None,
        )
