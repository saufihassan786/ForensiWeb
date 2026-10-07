"""Normalized Event Store and Search/Filter Subsystem (PHASE-08-F04, F05, F06, F07).

Provides JSONL persistence in derived evidence directories, keyword search,
faceted filtering, and cryptographic evidence traceability.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from evidence.storage import EvidenceStorage
from .schema import AttackStage, CommonEventModel, SeverityLevel


class NormalizedEventStore:
    """Manages persistence, search, filtering, and evidence linkage for CommonEventModel events."""

    JSONL_FILENAME = "normalized_events.jsonl"

    def __init__(self, storage: Optional[EvidenceStorage] = None) -> None:
        self.storage = storage or EvidenceStorage()
        self._memory_cache: Dict[str, List[CommonEventModel]] = {}

    def get_case_derived_file(self, case_id: str) -> Path:
        """Resolve path to case normalized_events.jsonl file."""
        deriv_dir = self.storage.get_case_derived_dir(case_id)
        deriv_dir.mkdir(parents=True, exist_ok=True)
        return deriv_dir / self.JSONL_FILENAME

    def save_events(self, case_id: str, events: List[CommonEventModel]) -> int:
        """Append or persist normalized events to derived JSONL file."""
        if not events:
            return 0

        target_file = self.get_case_derived_file(case_id)
        with target_file.open("a", encoding="utf-8") as f:
            for ev in events:
                json_str = ev.model_dump_json()
                f.write(json_str + "\n")

        # Update cache
        if case_id not in self._memory_cache:
            self._memory_cache[case_id] = []
        self._memory_cache[case_id].extend(events)
        return len(events)

    def load_events(self, case_id: str) -> List[CommonEventModel]:
        """Load all normalized events for a case from JSONL store."""
        target_file = self.get_case_derived_file(case_id)
        if not target_file.is_file():
            return self._memory_cache.get(case_id, [])

        events: List[CommonEventModel] = []
        with target_file.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    data = json.loads(stripped)
                    events.append(CommonEventModel.model_validate(data))

        self._memory_cache[case_id] = events
        return events

    def get(self, event_id: str, case_id: Optional[str] = None) -> Optional[CommonEventModel]:
        """Retrieve a specific normalized event by ID."""
        if case_id:
            events = self.load_events(case_id)
            for ev in events:
                if ev.event_id == event_id:
                    return ev
            return None

        # Search across all cached cases
        for cached_events in self._memory_cache.values():
            for ev in cached_events:
                if ev.event_id == event_id:
                    return ev
        return None

    def search(self, case_id: str, query: str) -> List[CommonEventModel]:
        """Search events in case by keyword across actors, targets, actions, and raw payloads."""
        all_events = self.load_events(case_id)
        q = query.strip().lower()
        if not q:
            return all_events

        matches: List[CommonEventModel] = []
        for ev in all_events:
            combined_text = (
                f"{ev.action} {ev.raw_content} {json.dumps(ev.actor)} "
                f"{json.dumps(ev.target)} {json.dumps(ev.details)}"
            ).lower()
            if q in combined_text:
                matches.append(ev)
        return matches

    def filter(
        self,
        case_id: str,
        attack_stage: Optional[Union[str, AttackStage]] = None,
        severity: Optional[Union[str, SeverityLevel]] = None,
        source_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[CommonEventModel]:
        """Filter normalized events by multiple forensic criteria."""
        events = self.load_events(case_id)
        filtered = events

        if attack_stage:
            stage_val = attack_stage.value if isinstance(attack_stage, AttackStage) else attack_stage
            filtered = [e for e in filtered if e.attack_stage == stage_val]

        if severity:
            sev_val = severity.value if isinstance(severity, SeverityLevel) else severity
            filtered = [e for e in filtered if e.severity == sev_val]

        if source_type:
            filtered = [e for e in filtered if e.source_type == source_type]

        if start_time:
            st = start_time if start_time.tzinfo else start_time.replace(tzinfo=timezone.utc)
            filtered = [e for e in filtered if e.timestamp >= st]

        if end_time:
            et = end_time if end_time.tzinfo else end_time.replace(tzinfo=timezone.utc)
            filtered = [e for e in filtered if e.timestamp <= et]

        return filtered

    def verify_event_traceability(self, event: CommonEventModel) -> bool:
        """PHASE-08-F07: Verify that an event links back to valid byte offsets in original store."""
        try:
            orig_path = self.storage.get_original_path(
                event.case_id,
                event.source_artifact_id,
                event.evidence_ref.artifact_name,
            )
            if not orig_path.is_file():
                return False

            raw_bytes = orig_path.read_bytes()
            start = event.source_location.byte_offset_start
            end = event.source_location.byte_offset_end

            if start < 0 or end > len(raw_bytes) or start > end:
                return False

            extracted_slice = raw_bytes[start:end].decode("utf-8", errors="replace").rstrip("\r\n")
            return event.raw_content.rstrip("\r\n") == extracted_slice
        except Exception:
            return False


EventStore = NormalizedEventStore

