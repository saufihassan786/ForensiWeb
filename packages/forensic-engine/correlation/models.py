"""Event Correlation Data Models (PHASE-10-F01 & F06).

Defines correlation edges, multi-tier confidence scoring, forensic classifications,
and graph representations adhering to forensic-model.md Section 6.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceClassification(str, enum.Enum):
    """Forensic evidence certainty classifications."""

    OBSERVED = "Observed"      # Directly represented by available evidence
    LIKELY = "Likely"          # Strongly supported but not directly proven
    CORRELATED = "Correlated"  # Supported by relationships between multiple observations
    INFERRED = "Inferred"      # Analytical interpretation requiring explicit qualification


class ConfidenceLevel(str, enum.Enum):
    """Correlation link confidence tier."""

    DEFINITIVE = "Definitive"  # 0.90 – 1.00
    HIGH = "High"              # 0.75 – 0.89
    PROBABLE = "Probable"      # 0.50 – 0.74
    LOW = "Low"                # < 0.50


class CorrelationEdge(BaseModel):
    """An explainable, evidence-backed relationship between two forensic events."""

    edge_id: str = Field(description="Unique correlation relationship identifier")
    case_id: str = Field(description="Target investigation case")
    source_event_id: str = Field(description="Originating event ID")
    target_event_id: str = Field(description="Subsequent or related event ID")
    correlation_type: str = Field(description="Correlation heuristic type")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Numerical confidence metric [0.0 - 1.0]")
    confidence_level: ConfidenceLevel = Field(description="Qualitative confidence tier")
    classification: EvidenceClassification = Field(description="Evidence certainty category")
    time_delta_seconds: float = Field(description="Temporal elapsed time in seconds")
    explanation: str = Field(description="Deterministic explanation of why events are linked")
    contributing_evidence: List[str] = Field(default_factory=list, description="Evidence artifacts supporting this link")
    attributes_matched: Dict[str, Any] = Field(default_factory=dict, description="Correlating attributes (IP, PID, path)")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class CorrelationGraph(BaseModel):
    """Full incident correlation topology for a forensic case."""

    case_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_events: int
    total_edges: int
    edges: List[CorrelationEdge] = Field(default_factory=list)
    clusters: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
