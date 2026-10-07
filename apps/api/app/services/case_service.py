"""Case Application Service (PHASE-12)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case as DBCase
from app.repositories.case import CaseRepository
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate

logger = logging.getLogger("forensiweb.services.case")


class CaseService:
    """Manages investigation case lifecycles."""

    def __init__(self) -> None:
        self._memory_cases: Dict[str, CaseRead] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        now = datetime.now(timezone.utc)
        default_case = CaseRead(
            id="CASE-001",
            title="Sample LFI to PrivEsc Investigation",
            description="Controlled forensic investigation baseline case.",
            status="investigating",
            priority="high",
            created_at=now,
            updated_at=now,
        )
        self._memory_cases["CASE-001"] = default_case

    async def list_cases(
        self,
        session: Optional[AsyncSession] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[CaseRead], int]:
        if session:
            try:
                db_cases, total = await CaseRepository.list_cases(
                    session=session, status=status, priority=priority, skip=skip, limit=limit
                )
                if total > 0:
                    return [CaseRead.model_validate(c) for c in db_cases], total
            except Exception as e:
                logger.debug("Database case list fallback: %s", e)

        cases = list(self._memory_cases.values())
        if status:
            cases = [c for c in cases if c.status == status]
        if priority:
            cases = [c for c in cases if c.priority == priority]

        total = len(cases)
        return cases[skip : skip + limit], total

    async def get_case(self, case_id: str, session: Optional[AsyncSession] = None) -> Optional[CaseRead]:
        if session:
            try:
                db_case = await CaseRepository.get_by_id(session, case_id)
                if db_case:
                    return CaseRead.model_validate(db_case)
            except Exception as e:
                logger.debug("Database case get fallback: %s", e)

        return self._memory_cases.get(case_id)

    async def create_case(self, case_in: CaseCreate, session: Optional[AsyncSession] = None) -> CaseRead:
        now = datetime.now(timezone.utc)
        case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"

        if session:
            try:
                db_case = DBCase(
                    id=case_id,
                    title=case_in.title,
                    description=case_in.description,
                    status=case_in.status,
                    priority=case_in.priority,
                )
                created = await CaseRepository.create(session, db_case)
                return CaseRead.model_validate(created)
            except Exception as e:
                logger.debug("Database case create fallback: %s", e)

        new_case = CaseRead(
            id=case_id,
            title=case_in.title,
            description=case_in.description,
            status=case_in.status,
            priority=case_in.priority,
            created_at=now,
            updated_at=now,
        )
        self._memory_cases[case_id] = new_case
        return new_case

    async def update_case(
        self, case_id: str, case_in: CaseUpdate, session: Optional[AsyncSession] = None
    ) -> Optional[CaseRead]:
        existing = await self.get_case(case_id, session)
        if not existing:
            return None

        now = datetime.now(timezone.utc)
        updated_data = existing.model_dump()
        for k, v in case_in.model_dump(exclude_unset=True).items():
            if v is not None:
                updated_data[k] = v
        updated_data["updated_at"] = now

        updated_case = CaseRead(**updated_data)
        self._memory_cases[case_id] = updated_case
        return updated_case
