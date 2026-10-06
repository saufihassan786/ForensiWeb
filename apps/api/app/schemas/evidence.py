"""Evidence API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceBase(BaseModel):
    source: str = Field(description="Evidence origin system/log source")
    filename: str = Field(description="Original filename of the evidence artifact")
    file_path: str = Field(description="Internal storage path to preserved artifact")
    sha256: str = Field(min_length=64, max_length=64, description="Cryptographic SHA-256 checksum")
    size_bytes: int = Field(ge=0, description="Artifact byte size")
    media_type: str = Field(description="MIME/media type")
    acquired_at: datetime = Field(description="Timestamp of acquisition in UTC")
    status: str = Field(default="acquired", description="Status: acquired, parsed, verified, corrupted")


class EvidenceCreate(EvidenceBase):
    case_id: str = Field(description="Target investigation case ID")


class EvidenceRead(EvidenceBase):
    id: str
    case_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
