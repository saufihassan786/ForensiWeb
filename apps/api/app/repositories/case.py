"""Case Repository for Database Operations (PHASE-12)."""

from __future__ import annotations

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case


class CaseRepository:
    """Repository managing Case entity persistence and queries."""

    @staticmethod
    async def get_by_id(session: AsyncSession, case_id: str) -> Optional[Case]:
        """Retrieve a case by ID."""
        stmt = select(Case).where(Case.id == case_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_cases(
        session: AsyncSession,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Case], int]:
        """List cases with optional status or priority filters."""
        query = select(Case)
        count_query = select(func.count(Case.id))

        if status:
            query = query.where(Case.status == status)
            count_query = count_query.where(Case.status == status)
        if priority:
            query = query.where(Case.priority == priority)
            count_query = count_query.where(Case.priority == priority)

        query = query.order_by(Case.created_at.desc()).offset(skip).limit(limit)

        total_res = await session.execute(count_query)
        total = total_res.scalar_one() or 0

        items_res = await session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    @staticmethod
    async def create(session: AsyncSession, case: Case) -> Case:
        """Persist a new case entity."""
        session.add(case)
        await session.flush()
        return case

    @staticmethod
    async def update(session: AsyncSession, case: Case) -> Case:
        """Update an existing case entity."""
        await session.flush()
        return case
