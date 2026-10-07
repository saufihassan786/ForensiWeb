"""Dashboard Analytics API schemas (PHASE-13)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CaseOverviewMetric(BaseModel):
    case_id: str
    title: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime


class EvidenceMetrics(BaseModel):
    total_artifacts: int
    verified_hashes: int
    tampered_count: int
    total_bytes: int
    format_breakdown: Dict[str, int] = Field(default_factory=dict)


class EventMetrics(BaseModel):
    total_events: int
    by_source_type: Dict[str, int] = Field(default_factory=dict)
    by_attack_stage: Dict[str, int] = Field(default_factory=dict)


class DetectionMetrics(BaseModel):
    total_alerts: int
    by_severity: Dict[str, int] = Field(default_factory=dict)
    by_rule: Dict[str, int] = Field(default_factory=dict)


class FindingMetrics(BaseModel):
    total_findings: int
    by_severity: Dict[str, int] = Field(default_factory=dict)
    mitigated_count: int
    unmitigated_count: int


class EventTrendBucket(BaseModel):
    bucket_start: datetime
    count: int
    stages: Dict[str, int] = Field(default_factory=dict)


class SeverityDistribution(BaseModel):
    counts: Dict[str, int] = Field(default_factory=dict)
    percentages: Dict[str, float] = Field(default_factory=dict)


class AttackStageAnalytics(BaseModel):
    stages_detected: List[str] = Field(default_factory=list)
    highest_stage_reached: str
    sequence_completion_percent: float


class RecentActivityItem(BaseModel):
    timestamp: datetime
    activity_type: str
    summary: str
    entity_id: str
    severity: Optional[str] = None


class RiskExplanationFactor(BaseModel):
    factor: str
    points: int
    rationale: str


class RiskSummary(BaseModel):
    case_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str = Field(description="CRITICAL, HIGH, MEDIUM, LOW, MINIMAL")
    explanation_factors: List[RiskExplanationFactor] = Field(default_factory=list)
    calculated_at: datetime


class DashboardAnalytics(BaseModel):
    case_overview: CaseOverviewMetric
    evidence_metrics: EvidenceMetrics
    event_metrics: EventMetrics
    detection_metrics: DetectionMetrics
    finding_metrics: FindingMetrics
    event_trends: List[EventTrendBucket] = Field(default_factory=list)
    severity_distribution: SeverityDistribution
    attack_stage_analytics: AttackStageAnalytics
    recent_activity: List[RecentActivityItem] = Field(default_factory=list)
    risk_summary: RiskSummary
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
