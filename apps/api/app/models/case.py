"""Case domain entity model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.evidence import Evidence
    from app.models.event import Event
    from app.models.detection import Detection
    from app.models.timeline import TimelineEntry
    from app.models.finding import Finding
    from app.models.report import Report


class Case(Base):
    """Investigation case container."""

    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open", index=True
    )  # open, investigating, closed, archived
    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default="medium", index=True
    )  # low, medium, high, critical
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    evidence_items: Mapped[List[Evidence]] = relationship(
        "Evidence", back_populates="case", cascade="all, delete-orphan"
    )
    events: Mapped[List[Event]] = relationship(
        "Event", back_populates="case", cascade="all, delete-orphan"
    )
    detections: Mapped[List[Detection]] = relationship(
        "Detection", back_populates="case", cascade="all, delete-orphan"
    )
    timeline_entries: Mapped[List[TimelineEntry]] = relationship(
        "TimelineEntry", back_populates="case", cascade="all, delete-orphan"
    )
    findings: Mapped[List[Finding]] = relationship(
        "Finding", back_populates="case", cascade="all, delete-orphan"
    )
    reports: Mapped[List[Report]] = relationship(
        "Report", back_populates="case", cascade="all, delete-orphan"
    )
