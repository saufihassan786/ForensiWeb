"""Case API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CaseBase(BaseModel):
    title: str = Field(min_length=1, max_length=255, description="Investigation case title")
    description: Optional[str] = Field(default=None, description="Detailed case background")
    status: str = Field(default="open", description="Case state: open, investigating, closed, archived")
    priority: str = Field(default="medium", description="Priority level: low, medium, high, critical")


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class CaseRead(CaseBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
