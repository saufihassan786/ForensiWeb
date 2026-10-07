"""Event Normalization Pipeline (PHASE-08-F03).

Transforms structured ParsedRecord objects into validated CommonEventModel instances,
mapping actions, actors, targets, and attack chain phases.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from parsers.models import ParsedRecord
from .schema import (
    AttackStage,
    CommonEventModel,
    EvidenceRefModel,
    SeverityLevel,
    SourceLocationModel,
)


class EventNormalizer:
    """Normalizes heterogeneous parsed records into the Common Event Model."""

    @staticmethod
    def generate_event_id() -> str:
        return f"EVT-{uuid.uuid4().hex[:8].upper()}"

    @classmethod
    def normalize_record(cls, record: ParsedRecord, case_id: str) -> CommonEventModel:
        """Convert a single ParsedRecord into a validated CommonEventModel instance."""
        # 1. Resolve timestamp
        dt_utc = datetime.now(timezone.utc)
        if record.timestamp_utc:
            try:
                dt_utc = datetime.fromisoformat(record.timestamp_utc)
            except Exception:
                pass

        fields = record.fields
        indicators = fields.get("indicators", [])

        # 2. Determine attack stage, severity, and action based on parsed features
        stage = AttackStage.NORMAL
        severity = SeverityLevel.INFORMATIONAL
        action = "log_event"
        actor: dict = {}
        target: dict = {}

        # Web Access Logs
        if record.source_type == "web_access_log":
            actor = {
                "ip": fields.get("client_ip"),
                "user_agent": fields.get("user_agent"),
                "user": fields.get("auth_user") or "anonymous",
            }
            target = {
                "method": fields.get("http_method"),
                "path": fields.get("uri_path"),
                "status_code": fields.get("status_code"),
                "query_params": fields.get("query_params", {}),
            }
            action = f"http_{fields.get('http_method', 'get').lower()}"

            if "path_traversal" in indicators:
                stage = AttackStage.STAGE_01_LFI
                severity = SeverityLevel.HIGH
                action = "http_lfi_probe"
            if "log_poisoning_payload" in indicators:
                stage = AttackStage.STAGE_02_LOG_POISONING
                severity = SeverityLevel.HIGH
                action = "http_log_poisoning_injection"
            if "command_execution_parameter" in indicators and "access.log" in fields.get("raw_uri", ""):
                stage = AttackStage.STAGE_03_RCE
                severity = SeverityLevel.CRITICAL
                action = "http_rce_log_inclusion"

        # Application Logs
        elif record.source_type == "app_log":
            actor = {
                "logger": fields.get("logger"),
                "level": fields.get("level"),
            }
            target = {
                "message": fields.get("message"),
            }
            action = f"app_log_{fields.get('level', 'info').lower()}"

            if "path_traversal_detection" in indicators:
                stage = AttackStage.STAGE_01_LFI
                severity = SeverityLevel.HIGH
                action = "app_lfi_detected"
            elif "log_poisoning_alert" in indicators:
                stage = AttackStage.STAGE_02_LOG_POISONING
                severity = SeverityLevel.HIGH
                action = "app_poisoning_detected"
            elif "child_process_spawn" in indicators:
                stage = AttackStage.STAGE_03_RCE
                severity = SeverityLevel.CRITICAL
                action = "app_child_process_spawn_detected"
            elif fields.get("level") in ("ERROR", "CRITICAL"):
                severity = SeverityLevel.HIGH
            elif fields.get("level") == "WARNING":
                severity = SeverityLevel.MEDIUM

        # System Audit Logs
        elif record.source_type == "system_audit":
            actor = {
                "pid": fields.get("pid"),
                "ppid": fields.get("ppid"),
                "uid": fields.get("uid"),
                "gid": fields.get("gid"),
                "auid": fields.get("auid"),
                "comm": fields.get("comm"),
            }
            target = {
                "exe": fields.get("exe"),
                "target_name": fields.get("name"),
                "record_type": fields.get("record_type"),
                "syscall": fields.get("syscall"),
            }
            action = f"audit_{fields.get('record_type', 'syscall').lower()}"

            if "privilege_escalation_target" in indicators or "temporary_directory_execution" in indicators:
                stage = AttackStage.STAGE_06_PRIV_ESC
                severity = SeverityLevel.CRITICAL
                action = "audit_privilege_escalation_attempt"
            elif "shell_spawn" in indicators:
                stage = AttackStage.STAGE_03_RCE
                severity = SeverityLevel.CRITICAL
                action = "audit_unauthorized_shell_spawn"

        # Environment Dump
        elif record.source_type == "env_dump":
            actor = {"system": "environment_probe"}
            target = {"variables": fields.get("environment", {})}
            if "insecure_path_order" in indicators:
                stage = AttackStage.STAGE_05_ENV_MANIPULATION
                severity = SeverityLevel.HIGH
                action = "env_insecure_path_order_detected"

        # Fallback / Generic
        else:
            actor = {"source": record.source_type}
            target = {"raw": record.raw_content[:200]}
            action = "generic_event"

        location_model = SourceLocationModel(
            line_number=record.source_location.line_number,
            byte_offset_start=record.source_location.byte_offset_start,
            byte_offset_end=record.source_location.byte_offset_end,
        )

        evidence_ref_model = EvidenceRefModel(
            artifact_name=record.evidence_ref.filename,
            sha256=record.evidence_ref.sha256,
        )

        return CommonEventModel(
            event_id=cls.generate_event_id(),
            case_id=case_id,
            timestamp=dt_utc,
            source_type=record.source_type,
            source_artifact_id=record.evidence_ref.evidence_id,
            source_location=location_model,
            attack_stage=stage,
            severity=severity,
            action=action,
            actor=actor,
            target=target,
            details=fields,
            evidence_ref=evidence_ref_model,
            raw_content=record.raw_content,
        )

    @classmethod
    def normalize_batch(cls, records: List[ParsedRecord], case_id: str) -> List[CommonEventModel]:
        """Normalize a collection of parsed records."""
        events: List[CommonEventModel] = []
        for r in records:
            if r.status == "valid":
                events.append(cls.normalize_record(r, case_id))
        return events
