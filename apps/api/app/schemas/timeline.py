"""Timeline entry API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TimelineEntryBase(BaseModel):
    timestamp: datetime = Field(description="Milestone timestamp in UTC")
    attack_stage: str = Field(description="Classified attack stage")
    title: str = Field(description="Timeline item title")
    summary: str = Field(description="Analytical summary of milestone")
    order_index: int = Field(default=0, description="Sequential ordering index")
    event_ids: List[str] = Field(default_factory=list)
    detection_ids: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)
    classification: str = Field(default="Observed", description="Observed, Likely, Correlated, Inferred")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineEntryCreate(TimelineEntryBase):
    case_id: str


class TimelineEntryRead(TimelineEntryBase):
    id: str
    case_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttackChainNodeRead(BaseModel):
    id: str
    label: str
    stage: str
    node_type: str
    timestamp: datetime
    classification: str
    confidence: float
    evidence_references: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class AttackChainEdgeRead(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    confidence: float
    classification: str
    explanation: str


class AttackChainGraphRead(BaseModel):
    case_id: str
    nodes: List[AttackChainNodeRead] = Field(default_factory=list)
    edges: List[AttackChainEdgeRead] = Field(default_factory=list)
    root_causes: List[str] = Field(default_factory=list)
    terminal_impacts: List[str] = Field(default_factory=list)
    stage_sequence: List[str] = Field(default_factory=list)
    overall_confidence: float
    reconstructed_at: datetime


class TimelineDrillDownRead(BaseModel):
    milestone_id: str
    title: str
    stage: str
    timestamp: datetime
    summary: str
    classification: str
    confidence: float
    order_index: int
    metadata: Dict[str, Any]
    detection_ids: List[str]
    evidence_references: List[str]
    supporting_events_count: int
    events: List[Dict[str, Any]]
