"""Timeline entry domain entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class TimelineEntry(Base):
    """Chronological attack sequence milestone."""

    __tablename__ = "timeline_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: f"TL-{uuid.uuid4().hex[:8]}"
    )
    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    attack_stage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # RECON, LFI, LOG_POISONING, RCE, POST_EXPLOITATION, PRIVILEGE_ESCALATION, IMPACT
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    event_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_references: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    case: Mapped[Case] = relationship("Case", back_populates="timeline_entries")
