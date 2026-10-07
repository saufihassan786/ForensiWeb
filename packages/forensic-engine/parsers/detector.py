"""Evidence Source Detection Engine (PHASE-07-F02).

Automatically classifies heterogeneous log inputs to dispatch appropriate parsers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class SourceDetectionResult:
    """Outcome of source log format identification."""

    source_type: str
    confidence: float
    recommended_parser: str
    matched_pattern: Optional[str] = None


class SourceDetector:
    """Analyzes evidence filenames and content samples to infer evidence format."""

    # Pre-compiled regex heuristics
    REGEX_WEB_ACCESS = re.compile(
        r'^\S+\s+\S+\s+\S+\s+\[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+\-]\d{4}\]\s+"(GET|POST|HEAD|PUT|DELETE|OPTIONS)\s+',
        re.MULTILINE,
    )
    REGEX_APP_LOG = re.compile(
        r'^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[,\.]\d{3}\]\s+\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]',
        re.MULTILINE,
    )
    REGEX_AUDITD = re.compile(
        r'^type=(SYSCALL|EXECVE|PATH|CWD|PROCTITLE|USER_CMD|AVC)\s+msg=audit\(\d+\.\d+:\d+\):',
        re.MULTILINE,
    )
    REGEX_JSON_ENV = re.compile(r'^\s*\{\s*".*?(PATH|USER|SHELL|HOME|HOSTNAME).*?":', re.DOTALL)

    @classmethod
    def detect(cls, filename: str, content_sample: str) -> SourceDetectionResult:
        """Detect source type and recommended parser using content and filename signatures."""
        sample = content_sample.strip()
        fname = Path(filename).name.lower()

        # 1. Linux auditd records
        if cls.REGEX_AUDITD.search(sample):
            return SourceDetectionResult(
                source_type="system_audit",
                confidence=0.98,
                recommended_parser="AuditdParser",
                matched_pattern="type=(SYSCALL|EXECVE|PATH) msg=audit",
            )
        if "audit" in fname:
            return SourceDetectionResult(
                source_type="system_audit",
                confidence=0.85,
                recommended_parser="AuditdParser",
                matched_pattern="filename_audit",
            )

        # 2. Web Access logs (Combined / Common Log Format)
        if cls.REGEX_WEB_ACCESS.search(sample):
            return SourceDetectionResult(
                source_type="web_access_log",
                confidence=0.95,
                recommended_parser="WebAccessLogParser",
                matched_pattern="combined_log_format",
            )
        if "access" in fname or "nginx" in fname or "apache" in fname:
            return SourceDetectionResult(
                source_type="web_access_log",
                confidence=0.80,
                recommended_parser="WebAccessLogParser",
                matched_pattern="filename_web_access",
            )

        # 3. Application logs (Python / Flask)
        if cls.REGEX_APP_LOG.search(sample):
            return SourceDetectionResult(
                source_type="app_log",
                confidence=0.95,
                recommended_parser="ApplicationLogParser",
                matched_pattern="standard_app_log_brackets",
            )
        if "error" in fname or "app" in fname or "flask" in fname:
            return SourceDetectionResult(
                source_type="app_log",
                confidence=0.80,
                recommended_parser="ApplicationLogParser",
                matched_pattern="filename_app_log",
            )

        # 4. JSON Environment dump
        if cls.REGEX_JSON_ENV.search(sample) or (sample.startswith("{") and sample.endswith("}")):
            return SourceDetectionResult(
                source_type="env_dump",
                confidence=0.90,
                recommended_parser="EnvironmentDumpParser",
                matched_pattern="json_env_keys",
            )

        # Fallback unknown
        return SourceDetectionResult(
            source_type="unknown",
            confidence=0.20,
            recommended_parser="GenericTextParser",
            matched_pattern=None,
        )
