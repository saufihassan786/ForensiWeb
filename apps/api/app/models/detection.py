"""Detection domain entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class Detection(Base):
    """Detection rule outcome / alert."""

    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: f"DET-{uuid.uuid4().hex[:8]}"
    )
    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # informational, low, medium, high, critical
    attack_stage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # RECON, LFI, LOG_POISONING, RCE, POST_EXPLOITATION, PRIVILEGE_ESCALATION, IMPACT
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    matched_event_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_references: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    case: Mapped[Case] = relationship("Case", back_populates="detections")
