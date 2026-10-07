"""Timeline Application Service (PHASE-11).

Coordinates chronological timeline reconstruction, graph synthesis, filtering,
and drill-down operations across normalized events, alerts, and custody evidence.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeline import TimelineEntry as DBTimelineEntry
from app.repositories.timeline import TimelineRepository
from app.schemas.timeline import (
    AttackChainEdgeRead,
    AttackChainGraphRead,
    AttackChainNodeRead,
    TimelineDrillDownRead,
    TimelineEntryCreate,
    TimelineEntryRead,
)
from models.rule import DetectionAlert
from correlation.models import CorrelationGraph
from normalization.schema import CommonEventModel
from normalization.store import EventStore
from timeline.filter import TimelineFilter
from timeline.models import (
    AttackChainGraph,
    TimelineClassification,
    TimelineEntry as EngineTimelineEntry,
)
from timeline.reconstructor import TimelineReconstructor

logger = logging.getLogger("forensiweb.services.timeline")


class TimelineService:
    """Service providing timeline reconstruction, querying, and attack-chain analysis."""

    def __init__(self, event_store: Optional[EventStore] = None) -> None:
        self.reconstructor = TimelineReconstructor()
        self.event_store = event_store or EventStore()
        # In-memory storage cache for fast headless querying and testing fallback
        self._memory_entries: Dict[str, List[EngineTimelineEntry]] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        """Seed baseline demonstration timeline milestone for CASE-001."""
        now = datetime.now(timezone.utc)
        default_entry = EngineTimelineEntry(
            id="TL-001",
            case_id="CASE-001",
            timestamp=now,
            attack_stage="LFI",
            title="Initial Directory Traversal Probing",
            summary="Attacker probed for system logs through path traversal in page query parameter.",
            order_index=1,
            event_ids=["EVT-001"],
            detection_ids=["DET-001"],
            evidence_references=["EV-001"],
            classification=TimelineClassification.OBSERVED,
            confidence=1.0,
            metadata={"source_ip": "192.168.1.100", "path": "/index.php?page=../../apache2/access.log"},
            created_at=now,
        )
        self._memory_entries["CASE-001"] = [default_entry]

    def reconstruct_from_events(
        self,
        case_id: str,
        events: List[CommonEventModel],
        alerts: Optional[List[DetectionAlert]] = None,
        correlation: Optional[CorrelationGraph] = None,
    ) -> List[EngineTimelineEntry]:
        """Run engine reconstruction algorithm and cache result."""
        reconstructed = self.reconstructor.reconstruct(
            events=events,
            alerts=alerts,
            correlation=correlation,
            case_id=case_id,
        )
        self._memory_entries[case_id] = reconstructed
        return reconstructed

    async def list_timeline(
        self,
        session: Optional[AsyncSession] = None,
        case_id: Optional[str] = None,
        attack_stage: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        classification: Optional[str] = None,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[TimelineEntryRead], int]:
        """Retrieve filtered and paginated timeline entries."""
        # Try database first if session is available
        if session:
            try:
                db_items, total = await TimelineRepository.list_by_case(
                    session=session,
                    case_id=case_id,
                    attack_stage=attack_stage,
                    start_time=start_time,
                    end_time=end_time,
                    skip=skip,
                    limit=limit,
                )
                if total > 0:
                    reads = [
                        TimelineEntryRead(
                            id=item.id,
                            case_id=item.case_id,
                            timestamp=item.timestamp,
                            attack_stage=item.attack_stage,
                            title=item.title,
                            summary=item.summary,
                            order_index=item.order_index,
                            event_ids=item.event_ids or [],
                            evidence_references=item.evidence_references or [],
                            created_at=item.created_at,
                        )
                        for item in db_items
                    ]
                    return reads, total
            except Exception as e:
                logger.debug("Database timeline query fallback to memory: %s", e)

        # Fallback to memory store
        entries_pool: List[EngineTimelineEntry] = []
        if case_id and case_id in self._memory_entries:
            entries_pool = self._memory_entries[case_id]
        else:
            for case_list in self._memory_entries.values():
                entries_pool.extend(case_list)

        classifications = [classification] if classification else None
        stages = [attack_stage] if attack_stage else None
        filtered = TimelineFilter.filter_entries(
            entries=entries_pool,
            stages=stages,
            start_time=start_time,
            end_time=end_time,
            classifications=classifications,
            query=query,
        )

        total = len(filtered)
        paginated = filtered[skip : skip + limit]

        reads = [
            TimelineEntryRead(
                id=e.id,
                case_id=e.case_id,
                timestamp=e.timestamp,
                attack_stage=e.attack_stage,
                title=e.title,
                summary=e.summary,
                order_index=e.order_index,
                event_ids=e.event_ids,
                detection_ids=e.detection_ids,
                evidence_references=e.evidence_references,
                classification=e.classification,
                confidence=e.confidence,
                metadata=e.metadata,
                created_at=e.created_at,
            )
            for e in paginated
        ]
        return reads, total

    async def get_attack_chain_graph(
        self,
        case_id: str,
        session: Optional[AsyncSession] = None,
    ) -> AttackChainGraphRead:
        """Construct the Attack Chain progression graph for a given case."""
        entries = self._memory_entries.get(case_id, [])
        if not entries and "CASE-001" in self._memory_entries:
            entries = self._memory_entries["CASE-001"]

        graph = self.reconstructor.build_attack_chain(entries, case_id=case_id)

        return AttackChainGraphRead(
            case_id=graph.case_id,
            nodes=[
                AttackChainNodeRead(
                    id=n.id,
                    label=n.label,
                    stage=n.stage,
                    node_type=n.node_type,
                    timestamp=n.timestamp,
                    classification=n.classification,
                    confidence=n.confidence,
                    evidence_references=n.evidence_references,
                    details=n.details,
                )
                for n in graph.nodes
            ],
            edges=[
                AttackChainEdgeRead(
                    source_id=e.source_id,
                    target_id=e.target_id,
                    relation_type=e.relation_type,
                    confidence=e.confidence,
                    classification=e.classification,
                    explanation=e.explanation,
                )
                for e in graph.edges
            ],
            root_causes=graph.root_causes,
            terminal_impacts=graph.terminal_impacts,
            stage_sequence=graph.stage_sequence,
            overall_confidence=graph.overall_confidence,
            reconstructed_at=graph.reconstructed_at,
        )

    async def drill_down_entry(
        self,
        entry_id: str,
        case_id: Optional[str] = None,
    ) -> Optional[TimelineDrillDownRead]:
        """Drill down from a timeline entry to underlying events and byte offsets."""
        target_entry: Optional[EngineTimelineEntry] = None
        for cid, entries in self._memory_entries.items():
            if case_id and cid != case_id:
                continue
            for e in entries:
                if e.id == entry_id:
                    target_entry = e
                    break
            if target_entry:
                break

        if not target_entry:
            return None

        drill_down_data = TimelineFilter.drill_down(target_entry, event_store=self.event_store)
        return TimelineDrillDownRead(**drill_down_data)
