"""Detection Rule and Alert Models (PHASE-09-F01, F05, F06).

Defines deterministic detection rules, explanations, and evidence-linked alerts.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DetectionAlert(BaseModel):
    """Detection alert linking back directly to source events and evidence artifacts."""

    detection_id: str = Field(description="Unique alert identifier, e.g. DET-xxxxxxxx")
    case_id: str = Field(description="Target investigation case")
    rule_id: str = Field(description="Detection rule code, e.g. RULE-LFI-001")
    rule_name: str = Field(description="Human-readable rule name")
    description: str = Field(description="Detailed rule description")
    severity: str = Field(description="Alert severity: informational, low, medium, high, critical")
    attack_stage: str = Field(description="Mapped attack chain stage")
    explanation: str = Field(description="Deterministic forensic explanation of WHY this rule triggered")
    matched_event_ids: List[str] = Field(default_factory=list, description="IDs of trigger events")
    evidence_references: List[str] = Field(default_factory=list, description="Associated evidence hashes/names")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual telemetry extracted")

    model_config = ConfigDict(from_attributes=True)


@dataclass
class DetectionRuleDefinition:
    """Specification of a deterministic forensic detection rule."""

    rule_id: str
    name: str
    description: str
    severity: str
    attack_stage: str
    input_source_types: List[str]
    explanation_template: str

    def format_explanation(self, **kwargs) -> str:
        """Format the deterministic explanation string."""
        return self.explanation_template.format(**kwargs)
