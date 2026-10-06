"""Event domain entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.evidence import Evidence


class Event(Base):
    """Normalized forensic event."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: f"EVT-{uuid.uuid4().hex[:8]}"
    )
    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("evidence.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="informational", index=True
    )  # informational, low, medium, high, critical
    actor_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    target_service: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    action_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    attack_stage: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )  # RECON, LFI, LOG_POISONING, RCE, POST_EXPLOITATION, PRIVILEGE_ESCALATION, IMPACT
    raw_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    case: Mapped[Case] = relationship("Case", back_populates="events")
    evidence: Mapped[Optional[Evidence]] = relationship("Evidence", back_populates="events")
