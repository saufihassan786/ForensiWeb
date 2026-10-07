"""Evidence Repository for Database Access (PHASE-06)."""

from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence


class EvidenceRepository:
    """Repository managing Evidence entity persistence operations."""

    @staticmethod
    async def get_by_id(session: AsyncSession, evidence_id: str) -> Optional[Evidence]:
        """Retrieve evidence item by its unique ID."""
        stmt = select(Evidence).where(Evidence.id == evidence_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_sha256(session: AsyncSession, case_id: str, sha256: str) -> Optional[Evidence]:
        """Find evidence with identical SHA-256 in the specified case."""
        stmt = select(Evidence).where(
            Evidence.case_id == case_id,
            Evidence.sha256 == sha256.lower(),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_case(
        session: AsyncSession,
        case_id: Optional[str] = None,
        source: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Evidence], int]:
        """Retrieve paginated evidence entities filtered by case, source, or status."""
        query = select(Evidence)
        count_query = select(func.count(Evidence.id))

        if case_id:
            query = query.where(Evidence.case_id == case_id)
            count_query = count_query.where(Evidence.case_id == case_id)
        if source:
            query = query.where(Evidence.source == source)
            count_query = count_query.where(Evidence.source == source)
        if status:
            query = query.where(Evidence.status == status)
            count_query = count_query.where(Evidence.status == status)

        query = query.order_by(Evidence.acquired_at.desc()).offset(skip).limit(limit)

        total_res = await session.execute(count_query)
        total = total_res.scalar_one() or 0

        items_res = await session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    @staticmethod
    async def create(session: AsyncSession, evidence: Evidence) -> Evidence:
        """Persist a new Evidence entity."""
        session.add(evidence)
        await session.flush()
        return evidence

    @staticmethod
    async def update_status(
        session: AsyncSession, evidence_id: str, new_status: str
    ) -> Optional[Evidence]:
        """Update lifecycle status of an evidence record."""
        ev = await EvidenceRepository.get_by_id(session, evidence_id)
        if ev:
            ev.status = new_status
            await session.flush()
        return ev
