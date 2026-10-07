"""Timeline and Attack Chain domain data models for ForensiWeb."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TimelineClassification(str, Enum):
    """Forensic classification of timeline entries distinguishing observations from interpretations."""
    OBSERVED = "Observed"        # Directly recorded in raw logs / audit events
    LIKELY = "Likely"            # Strongly supported by unambiguous direct evidence
    CORRELATED = "Correlated"    # Established through multi-source correlation
    INFERRED = "Inferred"        # Analytical deduction requiring explicit qualification


class AttackChainRelation(str, Enum):
    """Causal and chronological relationships between attack stages in the attack chain."""
    CAUSES = "causes"
    TRIGGERS = "triggers"
    ESCALATES_TO = "escalates_to"
    CORRELATED_WITH = "correlated_with"
    OBSERVED_PRIOR_TO = "observed_prior_to"


class TimelineEntry(BaseModel):
    """Chronological attack milestone entry with complete forensic traceability."""
    id: str = Field(description="Unique timeline milestone identifier (e.g. TL-001)")
    case_id: str = Field(description="Associated investigation case identifier")
    timestamp: datetime = Field(description="Timestamp in UTC (microsecond precision)")
    attack_stage: str = Field(description="Taxonomy stage: RECON, LFI, LOG_POISONING, RCE, WEBSHELL, PRIVILEGE_ESCALATION, IMPACT")
    title: str = Field(description="Human-readable milestone headline")
    summary: str = Field(description="Forensic analytical summary of what occurred")
    order_index: int = Field(default=0, description="Sequential ordering sequence")
    event_ids: List[str] = Field(default_factory=list, description="IDs of supporting normalized events")
    detection_ids: List[str] = Field(default_factory=list, description="IDs of linked detection alerts")
    evidence_references: List[str] = Field(default_factory=list, description="IDs or SHA-256 hashes of source evidence files")
    classification: TimelineClassification = Field(
        default=TimelineClassification.OBSERVED,
        description="Evidence classification: Observed, Likely, Correlated, Inferred",
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual attributes like IP, PID, URI, hashes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"use_enum_values": True}


class AttackChainNode(BaseModel):
    """Node in the attack-chain progression graph."""
    id: str = Field(description="Node identifier matching milestone, event, or detection ID")
    label: str = Field(description="Display label for visualization")
    stage: str = Field(description="Attack stage of the node")
    node_type: str = Field(description="Type: milestone, event, detection, finding")
    timestamp: datetime = Field(description="Node occurrence timestamp")
    classification: str = Field(default="Observed", description="Observed vs Inferred classification")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_references: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": True}


class AttackChainEdge(BaseModel):
    """Directed causal or chronological edge between attack progression nodes."""
    source_id: str = Field(description="Preceding node ID")
    target_id: str = Field(description="Succeeding node ID")
    relation_type: AttackChainRelation = Field(
        default=AttackChainRelation.CAUSES,
        description="Relationship type: causes, triggers, escalates_to, correlated_with, observed_prior_to",
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    classification: str = Field(default="Observed")
    explanation: str = Field(description="Deterministic forensic explanation of the link")

    model_config = {"use_enum_values": True}


class AttackChainGraph(BaseModel):
    """Complete visualization graph representing the reconstructed attack sequence."""
    case_id: str = Field(description="Associated case ID")
    nodes: List[AttackChainNode] = Field(default_factory=list)
    edges: List[AttackChainEdge] = Field(default_factory=list)
    root_causes: List[str] = Field(default_factory=list, description="IDs of earliest entry point nodes")
    terminal_impacts: List[str] = Field(default_factory=list, description="IDs of final exploitation or impact nodes")
    stage_sequence: List[str] = Field(default_factory=list, description="Ordered sequence of stages observed")
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reconstructed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"use_enum_values": True}
