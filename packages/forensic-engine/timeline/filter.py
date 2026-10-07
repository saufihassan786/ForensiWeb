"""Timeline filtering, query, and event drill-down module."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from normalization.schema import CommonEventModel
from normalization.store import EventStore
from timeline.models import TimelineClassification, TimelineEntry


class TimelineFilter:
    """Provides querying, faceted filtering, and forensic drill-down for timeline entries."""

    @staticmethod
    def filter_entries(
        entries: List[TimelineEntry],
        stages: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        classifications: Optional[List[str]] = None,
        min_confidence: Optional[float] = None,
        query: Optional[str] = None,
        evidence_id: Optional[str] = None,
    ) -> List[TimelineEntry]:
        """Apply multi-attribute filtering across timeline entries."""
        filtered = entries

        if stages:
            stage_set = {s.upper() for s in stages}
            filtered = [e for e in filtered if e.attack_stage.upper() in stage_set]

        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        if classifications:
            class_set = {c.lower() for c in classifications}
            filtered = [e for e in filtered if str(e.classification).lower() in class_set]

        if min_confidence is not None:
            filtered = [e for e in filtered if e.confidence >= min_confidence]

        if evidence_id:
            filtered = [e for e in filtered if evidence_id in e.evidence_references]

        if query:
            q = query.lower()
            filtered = [
                e
                for e in filtered
                if q in e.title.lower()
                or q in e.summary.lower()
                or q in e.attack_stage.lower()
                or any(q in ev_id.lower() for ev_id in e.evidence_references)
                or any(q in str(v).lower() for v in e.metadata.values())
            ]

        return filtered

    @staticmethod
    def drill_down(
        entry: TimelineEntry,
        event_store: Optional[EventStore] = None,
        events: Optional[List[CommonEventModel]] = None,
    ) -> Dict[str, Any]:
        """Drill down from a timeline milestone to underlying events, byte offsets, and raw evidence."""
        resolved_events: List[Dict[str, Any]] = []

        # Find supporting events either from provided list or EventStore
        candidate_events: List[CommonEventModel] = []
        if events:
            candidate_events.extend([e for e in events if e.event_id in entry.event_ids])
        elif event_store:
            for eid in entry.event_ids:
                stored = event_store.get(eid)
                if stored:
                    candidate_events.append(stored)

        for evt in candidate_events:
            actor_dict = evt.actor if isinstance(evt.actor, dict) else (evt.actor.model_dump() if hasattr(evt.actor, "model_dump") else {})
            target_dict = evt.target if isinstance(evt.target, dict) else (evt.target.model_dump() if hasattr(evt.target, "model_dump") else {})
            loc_dict = evt.source_location if isinstance(evt.source_location, dict) else (evt.source_location.model_dump() if hasattr(evt.source_location, "model_dump") else {})
            raw_text = getattr(evt, "raw_content", "") or getattr(evt, "raw_payload", "")
            ev_ref = getattr(evt, "source_artifact_id", "") or getattr(evt, "evidence_id", "")
            resolved_events.append({
                "event_id": evt.event_id,
                "timestamp": evt.timestamp.isoformat(),
                "source_type": evt.source_type,
                "event_type": getattr(evt, "event_type", "event"),
                "severity": str(evt.severity),
                "actor": actor_dict,
                "target": target_dict,
                "action": evt.action if isinstance(evt.action, str) else str(evt.action),
                "raw_payload": raw_text,
                "source_location": loc_dict,
                "evidence_id": ev_ref,
            })

        return {
            "milestone_id": entry.id,
            "title": entry.title,
            "stage": entry.attack_stage,
            "timestamp": entry.timestamp.isoformat(),
            "summary": entry.summary,
            "classification": entry.classification,
            "confidence": entry.confidence,
            "order_index": entry.order_index,
            "metadata": entry.metadata,
            "detection_ids": entry.detection_ids,
            "evidence_references": entry.evidence_references,
            "supporting_events_count": len(resolved_events),
            "events": resolved_events,
        }
