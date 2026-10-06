"""Timeline entry API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class TimelineEntryBase(BaseModel):
    timestamp: datetime = Field(description="Milestone timestamp in UTC")
    attack_stage: str = Field(description="Classified attack stage")
    title: str = Field(description="Timeline item title")
    summary: str = Field(description="Analytical summary of milestone")
    order_index: int = Field(default=0, description="Sequential ordering index")
    event_ids: List[str] = Field(default_factory=list)
    evidence_references: List[str] = Field(default_factory=list)


class TimelineEntryCreate(TimelineEntryBase):
    case_id: str


class TimelineEntryRead(TimelineEntryBase):
    id: str
    case_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
