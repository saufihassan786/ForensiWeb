"""Timeline Repository for Database and Query Operations (PHASE-11)."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeline import TimelineEntry


class TimelineRepository:
    """Repository managing TimelineEntry entity persistence and retrieval."""

    @staticmethod
    async def get_by_id(session: AsyncSession, entry_id: str) -> Optional[TimelineEntry]:
        """Retrieve a timeline milestone by unique identifier."""
        stmt = select(TimelineEntry).where(TimelineEntry.id == entry_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_case(
        session: AsyncSession,
        case_id: Optional[str] = None,
        attack_stage: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[TimelineEntry], int]:
        """Retrieve paginated and filtered timeline milestones."""
        query = select(TimelineEntry)
        count_query = select(func.count(TimelineEntry.id))

        if case_id:
            query = query.where(TimelineEntry.case_id == case_id)
            count_query = count_query.where(TimelineEntry.case_id == case_id)
        if attack_stage:
            query = query.where(TimelineEntry.attack_stage == attack_stage)
            count_query = count_query.where(TimelineEntry.attack_stage == attack_stage)
        if start_time:
            query = query.where(TimelineEntry.timestamp >= start_time)
            count_query = count_query.where(TimelineEntry.timestamp >= start_time)
        if end_time:
            query = query.where(TimelineEntry.timestamp <= end_time)
            count_query = count_query.where(TimelineEntry.timestamp <= end_time)

        query = query.order_by(TimelineEntry.order_index.asc(), TimelineEntry.timestamp.asc()).offset(skip).limit(limit)

        total_res = await session.execute(count_query)
        total = total_res.scalar_one() or 0

        items_res = await session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    @staticmethod
    async def create(session: AsyncSession, entry: TimelineEntry) -> TimelineEntry:
        """Persist a single timeline milestone."""
        session.add(entry)
        await session.flush()
        return entry

    @staticmethod
    async def bulk_create(session: AsyncSession, entries: List[TimelineEntry]) -> List[TimelineEntry]:
        """Persist multiple timeline milestones atomically."""
        session.add_all(entries)
        await session.flush()
        return entries
