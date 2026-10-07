"""System and Process Evidence Parser (PHASE-07-F05).

Parses Linux auditd logs (SYSCALL, EXECVE, PATH records) and environment dumps
to reconstruct process lineage, execution telemetry, and credential context.
"""

from __future__ import annotations

import json
import re
import shlex
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import BaseParser
from .models import EvidenceReference, ParsedRecord, SourceLocation


class AuditdParser(BaseParser):
    """Parser for Linux auditd daemon logs."""

    # type=SYSCALL msg=audit(1728225065.120:101): arch=c000003e ...
    AUDIT_HEADER_REGEX = re.compile(
        r'^type=(?P<type>[A-Z_]+)\s+msg=audit\((?P<epoch>\d+\.\d+):(?P<serial>\d+)\):\s*(?P<body>.*)$'
    )

    @property
    def parser_name(self) -> str:
        return "AuditdParser"

    @property
    def supported_source_types(self) -> List[str]:
        return ["system_audit", "auditd", "audit_log", "process_telemetry"]

    def can_parse(self, content_sample: str) -> bool:
        return bool(self.AUDIT_HEADER_REGEX.search(content_sample))

    @staticmethod
    def parse_key_value_body(body_str: str) -> Dict[str, Any]:
        """Extract key=value pairs, handling quoted strings."""
        result: Dict[str, Any] = {}
        # Simple regex for key=value where value can be "quoted" or unquoted
        pattern = re.compile(r'(?P<key>\w+)=(?:"(?P<qval>[^"]*)"|(?P<uval>\S+))')
        for match in pattern.finditer(body_str):
            key = match.group("key")
            val = match.group("qval") if match.group("qval") is not None else match.group("uval")
            # Type casting if integer
            if val is not None and val.isdigit():
                result[key] = int(val)
            else:
                result[key] = val
        return result

    def parse_line(
        self,
        line: str,
        line_number: int,
        byte_start: int,
        byte_end: int,
        evidence_ref: EvidenceReference,
    ) -> ParsedRecord:
        """Parse an individual auditd log record."""
        rec_id = f"REC-AUD-{uuid.uuid4().hex[:8].upper()}"
        location = SourceLocation(
            line_number=line_number,
            byte_offset_start=byte_start,
            byte_offset_end=byte_end,
        )

        match = self.AUDIT_HEADER_REGEX.match(line)
        if not match:
            return ParsedRecord(
                record_id=rec_id,
                parser_name=self.parser_name,
                source_type="system_audit",
                timestamp_raw=None,
                timestamp_utc=None,
                source_location=location,
                evidence_ref=evidence_ref,
                fields={},
                raw_content=line,
                status="malformed",
                error_message="Line does not match auditd type=TYPE msg=audit(epoch:serial): format",
            )

        data = match.groupdict()
        record_type = data.get("type")
        epoch_str = data.get("epoch")
        serial = data.get("serial")
        body = data.get("body") or ""

        # Epoch timestamp conversion
        raw_timestamp = f"{epoch_str}:{serial}"
        iso_time = None
        if epoch_str:
            try:
                epoch_flt = float(epoch_str)
                iso_time = datetime.fromtimestamp(epoch_flt, tz=timezone.utc).isoformat()
            except Exception:
                pass

        fields = self.parse_key_value_body(body)
        fields["record_type"] = record_type
        fields["audit_serial"] = serial

        # Identify indicators
        indicators: List[str] = []
        exe = fields.get("exe") or ""
        comm = fields.get("comm") or ""
        path_name = fields.get("name") or ""

        if "/bin/sh" in exe or "/bin/bash" in exe:
            indicators.append("shell_spawn")
        if "/tmp/" in path_name:
            indicators.append("temporary_directory_execution")
        if "su" in path_name or "su" in comm:
            indicators.append("privilege_escalation_target")

        fields["indicators"] = indicators

        return ParsedRecord(
            record_id=rec_id,
            parser_name=self.parser_name,
            source_type="system_audit",
            timestamp_raw=raw_timestamp,
            timestamp_utc=iso_time,
            source_location=location,
            evidence_ref=evidence_ref,
            fields=fields,
            raw_content=line,
            status="valid",
            error_message=None,
        )


class EnvironmentDumpParser(BaseParser):
    """Parser for captured system environment snapshots (JSON)."""

    @property
    def parser_name(self) -> str:
        return "EnvironmentDumpParser"

    @property
    def supported_source_types(self) -> List[str]:
        return ["env_dump", "environment_snapshot", "system_env"]

    def can_parse(self, content_sample: str) -> bool:
        sample = content_sample.strip()
        return sample.startswith("{") and sample.endswith("}")

    def parse_line(
        self,
        line: str,
        line_number: int,
        byte_start: int,
        byte_end: int,
        evidence_ref: EvidenceReference,
    ) -> ParsedRecord:
        """Parse JSON environment dump."""
        rec_id = f"REC-ENV-{uuid.uuid4().hex[:8].upper()}"
        location = SourceLocation(
            line_number=line_number,
            byte_offset_start=byte_start,
            byte_offset_end=byte_end,
        )
        try:
            env_vars = json.loads(line)
            indicators: List[str] = []
            path_val = env_vars.get("PATH", "")
            if path_val.startswith("/tmp") or ":/tmp" in path_val or ".:" in path_val:
                indicators.append("insecure_path_order")

            return ParsedRecord(
                record_id=rec_id,
                parser_name=self.parser_name,
                source_type="env_dump",
                timestamp_raw=None,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
                source_location=location,
                evidence_ref=evidence_ref,
                fields={"environment": env_vars, "indicators": indicators},
                raw_content=line,
                status="valid",
                error_message=None,
            )
        except Exception as exc:
            return ParsedRecord(
                record_id=rec_id,
                parser_name=self.parser_name,
                source_type="env_dump",
                timestamp_raw=None,
                timestamp_utc=None,
                source_location=location,
                evidence_ref=evidence_ref,
                fields={},
                raw_content=line,
                status="malformed",
                error_message=f"Invalid JSON environment dump: {exc}",
            )
