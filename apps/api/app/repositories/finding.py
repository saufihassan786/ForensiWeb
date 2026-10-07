"""Finding Repository for Database Operations (PHASE-12)."""

from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding


class FindingRepository:
    """Repository managing Finding entity persistence and queries."""

    @staticmethod
    async def get_by_id(session: AsyncSession, finding_id: str) -> Optional[Finding]:
        """Retrieve a finding by ID."""
        stmt = select(Finding).where(Finding.id == finding_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_case(
        session: AsyncSession,
        case_id: Optional[str] = None,
        severity: Optional[str] = None,
        attack_stage: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Finding], int]:
        """List findings filtered by case, severity, or attack stage."""
        query = select(Finding)
        count_query = select(func.count(Finding.id))

        if case_id:
            query = query.where(Finding.case_id == case_id)
            count_query = count_query.where(Finding.case_id == case_id)
        if severity:
            query = query.where(Finding.severity == severity)
            count_query = count_query.where(Finding.severity == severity)
        if attack_stage:
            query = query.where(Finding.attack_stage == attack_stage)
            count_query = count_query.where(Finding.attack_stage == attack_stage)

        query = query.order_by(Finding.created_at.desc()).offset(skip).limit(limit)

        total_res = await session.execute(count_query)
        total = total_res.scalar_one() or 0

        items_res = await session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    @staticmethod
    async def create(session: AsyncSession, finding: Finding) -> Finding:
        """Persist a new finding entity."""
        session.add(finding)
        await session.flush()
        return finding

    @staticmethod
    async def update(session: AsyncSession, finding: Finding) -> Finding:
        """Update an existing finding."""
        await session.flush()
        return finding
