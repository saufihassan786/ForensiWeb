"""Finding API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FindingBase(BaseModel):
    title: str = Field(description="Finding title")
    severity: str = Field(description="Severity: low, medium, high, critical")
    attack_stage: str = Field(description="Identified attack stage")
    analysis_summary: str = Field(description="Comprehensive forensic finding analysis")
    mitigation_summary: Optional[str] = Field(default=None, description="Recommended remediation action")
    evidence_references: List[str] = Field(default_factory=list)


class FindingCreate(FindingBase):
    case_id: str


class FindingRead(FindingBase):
    id: str
    case_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
