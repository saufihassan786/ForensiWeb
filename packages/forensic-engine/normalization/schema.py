"""Common Event Model (CEM) Schema Definition (PHASE-08-F01 & F02).

Implements the unified forensic event representation across heterogeneous sources,
conforming to forensic-model.md specifications and Pydantic validation rules.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SeverityLevel(str, enum.Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackStage(str, enum.Enum):
    STAGE_01_LFI = "stage_01_lfi"
    STAGE_02_LOG_POISONING = "stage_02_log_poisoning"
    STAGE_03_RCE = "stage_03_rce"
    STAGE_04_WEB_SHELL = "stage_04_web_shell"
    STAGE_05_ENV_MANIPULATION = "stage_05_env_manipulation"
    STAGE_06_PRIV_ESC = "stage_06_priv_esc"
    NORMAL = "normal"


class SourceLocationModel(BaseModel):
    """Source location coordinates in pristine evidence file."""

    line_number: int = Field(ge=1, description="1-indexed line number in original file")
    byte_offset_start: int = Field(ge=0, description="Starting byte offset")
    byte_offset_end: int = Field(ge=0, description="Ending byte offset")

    model_config = ConfigDict(frozen=True)


class EvidenceRefModel(BaseModel):
    """Cryptographic evidence reference."""

    artifact_name: str
    sha256: str = Field(min_length=64, max_length=64)

    @field_validator("sha256")
    @classmethod
    def normalize_sha256(cls, v: str) -> str:
        return v.lower()


class CommonEventModel(BaseModel):
    """Normalized forensic event complying with ISO/IEC 27037 and project CEM."""

    event_id: str = Field(description="Unique event ID, e.g., EVT-xxxxxxxx")
    case_id: str = Field(description="Target investigation case reference")
    timestamp: datetime = Field(description="Normalized UTC ISO-8601 timestamp")
    source_type: str = Field(description="Evidence origin classification")
    source_artifact_id: str = Field(description="ID of source evidence artifact")
    source_location: SourceLocationModel = Field(description="Line and byte coordinates in source")
    attack_stage: AttackStage = Field(default=AttackStage.NORMAL, description="Attack chain stage")
    severity: SeverityLevel = Field(default=SeverityLevel.INFORMATIONAL, description="Event severity")
    action: str = Field(description="Normalized action descriptor")
    actor: Dict[str, Any] = Field(default_factory=dict, description="Initiator context (IP, user, pid)")
    target: Dict[str, Any] = Field(default_factory=dict, description="Targeted resource context")
    details: Dict[str, Any] = Field(default_factory=dict, description="Source-specific fields and payload")
    evidence_ref: EvidenceRefModel = Field(description="Cryptographic evidence link")
    raw_content: str = Field(description="Exact original log line content")

    @field_validator("timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
