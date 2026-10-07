"""Finding Application Service (PHASE-12)."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finding import Finding as DBFinding
from app.repositories.finding import FindingRepository
from app.schemas.finding import FindingCreate, FindingRead, FindingUpdate

logger = logging.getLogger("forensiweb.services.finding")


class FindingService:
    """Manages forensic findings and remediation recommendations."""

    def __init__(self) -> None:
        self._memory_findings: Dict[str, FindingRead] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        now = datetime.now(timezone.utc)
        default_finding = FindingRead(
            id="FND-001",
            case_id="CASE-001",
            title="Unsanitized Local File Inclusion Vulnerability",
            severity="critical",
            attack_stage="LFI",
            analysis_summary="Vulnerability allows reading arbitrary local system files including web server logs.",
            mitigation_summary="Validate path inputs against an allowlist and disable direct log file readability.",
            evidence_references=["EV-001"],
            detection_ids=["DET-001"],
            event_ids=["EVT-001"],
            created_at=now,
            updated_at=now,
        )
        self._memory_findings["FND-001"] = default_finding

    async def list_findings(
        self,
        session: Optional[AsyncSession] = None,
        case_id: Optional[str] = None,
        severity: Optional[str] = None,
        attack_stage: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[FindingRead], int]:
        if session:
            try:
                db_findings, total = await FindingRepository.list_by_case(
                    session=session,
                    case_id=case_id,
                    severity=severity,
                    attack_stage=attack_stage,
                    skip=skip,
                    limit=limit,
                )
                if total > 0:
                    return [FindingRead.model_validate(f) for f in db_findings], total
            except Exception as e:
                logger.debug("Database finding list fallback: %s", e)

        findings = list(self._memory_findings.values())
        if case_id:
            findings = [f for f in findings if f.case_id == case_id]
        if severity:
            findings = [f for f in findings if f.severity == severity]
        if attack_stage:
            findings = [f for f in findings if f.attack_stage == attack_stage]

        total = len(findings)
        return findings[skip : skip + limit], total

    async def get_finding(self, finding_id: str, session: Optional[AsyncSession] = None) -> Optional[FindingRead]:
        if session:
            try:
                db_f = await FindingRepository.get_by_id(session, finding_id)
                if db_f:
                    return FindingRead.model_validate(db_f)
            except Exception as e:
                logger.debug("Database finding get fallback: %s", e)

        return self._memory_findings.get(finding_id)

    async def create_finding(
        self, finding_in: FindingCreate, session: Optional[AsyncSession] = None
    ) -> FindingRead:
        now = datetime.now(timezone.utc)
        finding_id = f"FND-{uuid.uuid4().hex[:6].upper()}"

        if session:
            try:
                db_f = DBFinding(
                    id=finding_id,
                    case_id=finding_in.case_id,
                    title=finding_in.title,
                    severity=finding_in.severity,
                    attack_stage=finding_in.attack_stage,
                    analysis_summary=finding_in.analysis_summary,
                    mitigation_summary=finding_in.mitigation_summary,
                    evidence_references=finding_in.evidence_references,
                    detection_ids=finding_in.detection_ids,
                    event_ids=finding_in.event_ids,
                )
                created = await FindingRepository.create(session, db_f)
                return FindingRead.model_validate(created)
            except Exception as e:
                logger.debug("Database finding create fallback: %s", e)

        new_finding = FindingRead(
            id=finding_id,
            case_id=finding_in.case_id,
            title=finding_in.title,
            severity=finding_in.severity,
            attack_stage=finding_in.attack_stage,
            analysis_summary=finding_in.analysis_summary,
            mitigation_summary=finding_in.mitigation_summary,
            evidence_references=finding_in.evidence_references,
            detection_ids=finding_in.detection_ids,
            event_ids=finding_in.event_ids,
            created_at=now,
            updated_at=now,
        )
        self._memory_findings[finding_id] = new_finding
        return new_finding

    async def update_finding(
        self, finding_id: str, finding_in: FindingUpdate, session: Optional[AsyncSession] = None
    ) -> Optional[FindingRead]:
        existing = await self.get_finding(finding_id, session)
        if not existing:
            return None

        now = datetime.now(timezone.utc)
        data = existing.model_dump()
        for k, v in finding_in.model_dump(exclude_unset=True).items():
            if v is not None:
                data[k] = v
        data["updated_at"] = now

        updated = FindingRead(**data)
        self._memory_findings[finding_id] = updated
        return updated
