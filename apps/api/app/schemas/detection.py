"""Detection API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class DetectionBase(BaseModel):
    rule_id: str = Field(description="Unique rule identifier")
    rule_name: str = Field(description="Human readable rule name")
    description: str = Field(description="Rule description")
    severity: str = Field(description="Severity classification")
    attack_stage: str = Field(description="Attack stage classification")
    explanation: str = Field(description="Human-interpretable explanation of detection logic")
    matched_event_ids: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)


class DetectionCreate(DetectionBase):
    case_id: str


class DetectionRead(DetectionBase):
    id: str
    case_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
