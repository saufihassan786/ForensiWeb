"""Event API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    timestamp: datetime = Field(description="Normalized UTC ISO-8601 timestamp")
    source: str = Field(description="Origin source identifier")
    event_type: str = Field(description="Classified event type")
    severity: str = Field(default="informational", description="Severity: informational, low, medium, high, critical")
    actor_ip: Optional[str] = None
    target_service: Optional[str] = None
    action_method: Optional[str] = None
    action_path: Optional[str] = None
    attack_stage: Optional[str] = None
    raw_payload: Optional[str] = None
    normalized_data: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    case_id: str
    evidence_id: Optional[str] = None


class EventRead(EventBase):
    id: str
    case_id: str
    evidence_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
