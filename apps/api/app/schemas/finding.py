"""Finding and Traceability API schemas (PHASE-12)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FindingBase(BaseModel):
    title: str = Field(description="Finding title")
    severity: str = Field(description="Severity: low, medium, high, critical")
    attack_stage: str = Field(description="Identified attack stage")
    analysis_summary: str = Field(description="Comprehensive forensic finding analysis")
    mitigation_summary: Optional[str] = Field(default=None, description="Recommended remediation action")
    evidence_references: List[str] = Field(default_factory=list)
    detection_ids: List[str] = Field(default_factory=list, description="Linked detection alerts")
    event_ids: List[str] = Field(default_factory=list, description="Linked normalized events")


class FindingCreate(FindingBase):
    case_id: str


class FindingUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    attack_stage: Optional[str] = None
    analysis_summary: Optional[str] = None
    mitigation_summary: Optional[str] = None
    evidence_references: Optional[List[str]] = None
    detection_ids: Optional[List[str]] = None
    event_ids: Optional[List[str]] = None


class FindingRead(FindingBase):
    id: str
    case_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TraceabilityHopRead(BaseModel):
    layer: str = Field(description="Layer name: finding, detection, event, evidence, artifact")
    entity_id: str = Field(description="ID of entity at this layer")
    status: str = Field(description="verified, missing, or unlinked")
    details: Dict[str, Any] = Field(default_factory=dict)


class TraceabilityReportRead(BaseModel):
    finding_id: str
    case_id: str
    is_fully_traceable: bool
    chain_depth: int
    hops: List[TraceabilityHopRead] = Field(default_factory=list)
    unresolved_links: List[str] = Field(default_factory=list)
    verified_sha256: Optional[str] = None
    original_file_path: Optional[str] = None
    verified_at: datetime
