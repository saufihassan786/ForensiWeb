"""Timeline Reconstructor and Attack Chain Builder for ForensiWeb."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from models.rule import DetectionAlert
from correlation.models import CorrelationGraph
from normalization.schema import AttackStage, CommonEventModel
from timeline.models import (
    AttackChainEdge,
    AttackChainGraph,
    AttackChainNode,
    AttackChainRelation,
    TimelineClassification,
    TimelineEntry,
)

# Standard stage progression sequence
STAGE_ORDER = [
    "RECON",
    "LFI",
    "LOG_POISONING",
    "RCE",
    "WEBSHELL",
    "POST_EXPLOITATION",
    "PRIVILEGE_ESCALATION",
    "IMPACT",
]


class TimelineReconstructor:
    """Reconstructs a defensible chronological attack timeline and attack-chain graph."""

    def __init__(self, max_gap_threshold_seconds: float = 3600.0) -> None:
        self.max_gap_threshold_seconds = max_gap_threshold_seconds

    def normalize_stage_name(self, raw_stage: str) -> str:
        """Map heterogeneous stage representations to canonical taxonomy."""
        cleaned = raw_stage.upper().replace("-", "_").replace(" ", "_")
        if "RECON" in cleaned:
            return "RECON"
        if "LFI" in cleaned or "LOCAL_FILE" in cleaned:
            return "LFI"
        if "POISON" in cleaned:
            return "LOG_POISONING"
        if "RCE" in cleaned or "EXECUTION" in cleaned:
            return "RCE"
        if "SHELL" in cleaned or "METERPRETER" in cleaned:
            return "WEBSHELL"
        if "PRIV" in cleaned or "ESCALATION" in cleaned or "SUDO" in cleaned or "PATH_HIJACK" in cleaned:
            return "PRIVILEGE_ESCALATION"
        if "IMPACT" in cleaned:
            return "IMPACT"
        return cleaned

    def reconstruct(
        self,
        events: List[CommonEventModel],
        alerts: Optional[List[DetectionAlert]] = None,
        correlation: Optional[CorrelationGraph] = None,
        case_id: str = "CASE-001",
    ) -> List[TimelineEntry]:
        """Reconstruct chronological timeline entries from normalized events and alerts."""
        alerts = alerts or []
        timeline_entries: List[TimelineEntry] = []

        # Index alerts by matched event IDs for fast lookup
        event_to_alerts: Dict[str, List[DetectionAlert]] = {}
        for alert in alerts:
            for matched_id in alert.matched_event_ids:
                event_to_alerts.setdefault(matched_id, []).append(alert)

        # Sort events strictly chronologically
        sorted_events = sorted(
            events,
            key=lambda e: (
                e.timestamp,
                getattr(e.source_location, "byte_offset_start", getattr(e.source_location, "byte_start", 0)) if e.source_location else 0,
                e.event_id,
            ),
        )

        order_idx = 1
        for evt in sorted_events:
            linked_alerts = event_to_alerts.get(evt.event_id, [])
            stage = self.normalize_stage_name(str(evt.attack_stage))

            actor_ip = evt.actor.get("ip") if isinstance(evt.actor, dict) else getattr(evt.actor, "ip", "unknown")
            target_svc = (
                evt.target.get("service_name") or evt.target.get("service")
                if isinstance(evt.target, dict)
                else getattr(evt.target, "service_name", "system")
            )
            action_desc = evt.action if isinstance(evt.action, str) else f"{getattr(evt.action, 'method', '')} {getattr(evt.action, 'path', '')}".strip()
            raw_text = getattr(evt, "raw_content", "") or getattr(evt, "raw_payload", "")
            b_start = getattr(evt.source_location, "byte_offset_start", getattr(evt.source_location, "byte_start", 0)) if evt.source_location else 0
            b_end = getattr(evt.source_location, "byte_offset_end", getattr(evt.source_location, "byte_end", 0)) if evt.source_location else 0
            ev_id = getattr(evt, "source_artifact_id", "") or getattr(evt, "evidence_id", "")
            evidence_refs = [ev_id] if ev_id else []

            # Determine classification and confidence
            if linked_alerts:
                # Event triggered an alert
                highest_alert = max(linked_alerts, key=lambda a: a.confidence)
                classification = (
                    TimelineClassification.CORRELATED
                    if correlation and any(edge.source_event_id == evt.event_id or edge.target_event_id == evt.event_id for edge in correlation.edges)
                    else TimelineClassification.LIKELY
                )
                confidence = highest_alert.confidence
                title = f"[{stage}] {highest_alert.rule_name}"
                summary = f"{highest_alert.explanation} (Actor: {actor_ip}, Target: {target_svc})"
            else:
                classification = TimelineClassification.OBSERVED
                confidence = 1.0
                title = f"[{stage}] {action_desc}".strip()
                summary = f"Recorded {evt.source_type} event: {raw_text[:120] if raw_text else 'Telemetry record'}"

            metadata: Dict[str, Any] = {
                "source_type": evt.source_type,
                "actor_ip": actor_ip,
                "target_service": target_svc,
                "action": action_desc,
                "raw_bytes": {
                    "start": b_start,
                    "end": b_end,
                },
            }

            entry = TimelineEntry(
                id=f"TL-{order_idx:03d}",
                case_id=case_id,
                timestamp=evt.timestamp,
                attack_stage=stage,
                title=title,
                summary=summary,
                order_index=order_idx,
                event_ids=[evt.event_id],
                detection_ids=[a.alert_id for a in linked_alerts],
                evidence_references=evidence_refs,
                classification=classification,
                confidence=confidence,
                metadata=metadata,
            )
            timeline_entries.append(entry)
            order_idx += 1

        # Check for standalone alerts that had no direct event in `events`
        all_included_events = {e.event_id for e in sorted_events}
        for alert in alerts:
            if not any(mid in all_included_events for mid in alert.matched_event_ids):
                stage = self.normalize_stage_name(alert.attack_stage)
                entry = TimelineEntry(
                    id=f"TL-{order_idx:03d}",
                    case_id=case_id,
                    timestamp=alert.created_at,
                    attack_stage=stage,
                    title=f"[{stage}] {alert.rule_name} (Analytical Alert)",
                    summary=alert.explanation,
                    order_index=order_idx,
                    event_ids=alert.matched_event_ids,
                    detection_ids=[alert.alert_id],
                    evidence_references=alert.evidence_references,
                    classification=TimelineClassification.INFERRED,
                    confidence=alert.confidence,
                    metadata={"rule_id": alert.rule_id, "alert_severity": alert.severity},
                )
                timeline_entries.append(entry)
                order_idx += 1

        # Final sort in case standalone alerts were appended
        timeline_entries.sort(key=lambda t: (t.timestamp, t.order_index))
        # Re-index order
        for i, entry in enumerate(timeline_entries, start=1):
            entry.order_index = i

        return timeline_entries

    def perform_gap_analysis(self, entries: List[TimelineEntry]) -> List[Dict[str, Any]]:
        """Identify significant temporal gaps or clock skew anomalies between timeline entries."""
        anomalies: List[Dict[str, Any]] = []
        if len(entries) < 2:
            return anomalies

        for i in range(len(entries) - 1):
            prev_entry = entries[i]
            curr_entry = entries[i + 1]
            delta_sec = (curr_entry.timestamp - prev_entry.timestamp).total_seconds()

            if delta_sec < 0:
                anomalies.append({
                    "type": "CLOCK_SKEW_REVERSAL",
                    "from_entry_id": prev_entry.id,
                    "to_entry_id": curr_entry.id,
                    "delta_seconds": delta_sec,
                    "description": f"Timestamp moved backwards by {abs(delta_sec):.2f}s indicating clock drift or out-of-order log generation.",
                })
            elif delta_sec > self.max_gap_threshold_seconds:
                anomalies.append({
                    "type": "INACTIVITY_GAP",
                    "from_entry_id": prev_entry.id,
                    "to_entry_id": curr_entry.id,
                    "delta_seconds": delta_sec,
                    "description": f"Prolonged inactivity gap of {delta_sec / 60:.1f} minutes between attack milestones.",
                })

        return anomalies

    def build_attack_chain(
        self,
        timeline_entries: List[TimelineEntry],
        correlation: Optional[CorrelationGraph] = None,
        case_id: str = "CASE-001",
    ) -> AttackChainGraph:
        """Construct a coherent Attack Chain graph mapping the attack progression across stages."""
        nodes: List[AttackChainNode] = []
        edges: List[AttackChainEdge] = []
        stage_sequence: List[str] = []

        # If no entries, return empty graph
        if not timeline_entries:
            return AttackChainGraph(case_id=case_id)

        # Collapse entries by stage to form clear attack milestones
        stage_first_entries: Dict[str, TimelineEntry] = {}
        for entry in timeline_entries:
            stage = entry.attack_stage
            if stage not in stage_first_entries:
                stage_first_entries[stage] = entry
                stage_sequence.append(stage)

        # Create graph nodes
        for stage, entry in stage_first_entries.items():
            node = AttackChainNode(
                id=entry.id,
                label=f"{stage}: {entry.title}",
                stage=stage,
                node_type="milestone",
                timestamp=entry.timestamp,
                classification=entry.classification,
                confidence=entry.confidence,
                evidence_references=entry.evidence_references,
                details={
                    "order_index": entry.order_index,
                    "event_ids": entry.event_ids,
                    "detection_ids": entry.detection_ids,
                    "summary": entry.summary,
                    "metadata": entry.metadata,
                },
            )
            nodes.append(node)

        # Sort nodes chronologically
        nodes.sort(key=lambda n: n.timestamp)

        # Create sequential causal edges between consecutive attack stages
        for i in range(len(nodes) - 1):
            src = nodes[i]
            tgt = nodes[i + 1]

            # Choose relation type based on stage progression
            if src.stage == "LFI" and tgt.stage == "LOG_POISONING":
                rel = AttackChainRelation.TRIGGERS
                explanation = "Reconnaissance via LFI revealed access logs, triggering log poisoning injection."
            elif src.stage == "LOG_POISONING" and tgt.stage == "RCE":
                rel = AttackChainRelation.CAUSES
                explanation = "Injected PHP User-Agent payload executed via LFI log inclusion, causing RCE."
            elif src.stage == "RCE" and tgt.stage in ("WEBSHELL", "POST_EXPLOITATION"):
                rel = AttackChainRelation.ESCALATES_TO
                explanation = "Arbitrary code execution escalated to web shell interaction and session establishment."
            elif src.stage in ("WEBSHELL", "POST_EXPLOITATION") and tgt.stage == "PRIVILEGE_ESCALATION":
                rel = AttackChainRelation.ESCALATES_TO
                explanation = "Web shell spawned commands that exploited PATH misconfiguration for root privilege escalation."
            else:
                rel = AttackChainRelation.OBSERVED_PRIOR_TO
                explanation = f"Observed stage {src.stage} preceded {tgt.stage} in forensic telemetry."

            edge_confidence = round((src.confidence + tgt.confidence) / 2.0, 3)
            edge_class = "Observed" if (src.classification == "Observed" and tgt.classification == "Observed") else "Correlated"

            edges.append(
                AttackChainEdge(
                    source_id=src.id,
                    target_id=tgt.id,
                    relation_type=rel,
                    confidence=edge_confidence,
                    classification=edge_class,
                    explanation=explanation,
                )
            )

        root_causes = [nodes[0].id] if nodes else []
        terminal_impacts = [nodes[-1].id] if nodes else []

        avg_conf = (
            sum(n.confidence for n in nodes) / len(nodes)
            if nodes
            else 1.0
        )

        return AttackChainGraph(
            case_id=case_id,
            nodes=nodes,
            edges=edges,
            root_causes=root_causes,
            terminal_impacts=terminal_impacts,
            stage_sequence=stage_sequence,
            overall_confidence=round(avg_conf, 3),
            reconstructed_at=datetime.now(timezone.utc),
        )
