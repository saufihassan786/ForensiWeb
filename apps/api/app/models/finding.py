"""Finding domain entity model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.case import Case


class Finding(Base):
    """Forensic investigation finding and security recommendation."""

    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: f"FND-{uuid.uuid4().hex[:8]}"
    )
    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # low, medium, high, critical
    attack_stage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # RECON, LFI, LOG_POISONING, RCE, POST_EXPLOITATION, PRIVILEGE_ESCALATION, IMPACT
    analysis_summary: Mapped[str] = mapped_column(Text, nullable=False)
    mitigation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_references: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
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
    case: Mapped[Case] = relationship("Case", back_populates="findings")
