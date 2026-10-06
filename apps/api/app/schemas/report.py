"""Report API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class ReportBase(BaseModel):
    report_type: str = Field(description="Report type: executive, technical, evidence_summary")
    title: str = Field(description="Report document title")
    file_path: str = Field(description="Stored path to compiled document")
    sha256: str = Field(min_length=64, max_length=64, description="Cryptographic SHA-256 checksum")
    format: str = Field(default="pdf", description="Output format: pdf, html, json")
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class ReportCreate(ReportBase):
    case_id: str


class ReportRead(ReportBase):
    id: str
    case_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
