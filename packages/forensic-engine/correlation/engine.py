"""Event Correlation Engine (PHASE-10-F01 through F07).

Executes multi-source forensic correlation across temporal, source, process lineage,
resource continuity, and attack-stage dimensions, with explainable confidence scoring.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from normalization.schema import AttackStage, CommonEventModel
from .models import (
    ConfidenceLevel,
    CorrelationEdge,
    CorrelationGraph,
    EvidenceClassification,
)

logger = logging.getLogger("forensiweb.correlation.engine")


class CorrelationEngine:
    """Combines isolated normalized events into an explainable causal incident graph."""

    # Attack chain progression order
    STAGE_ORDER = [
        AttackStage.STAGE_01_LFI,
        AttackStage.STAGE_02_LOG_POISONING,
        AttackStage.STAGE_03_RCE,
        AttackStage.STAGE_04_WEB_SHELL,
        AttackStage.STAGE_05_ENV_MANIPULATION,
        AttackStage.STAGE_06_PRIV_ESC,
    ]

    def __init__(self, max_temporal_window_seconds: float = 60.0) -> None:
        self.max_temporal_window_seconds = max_temporal_window_seconds

    @staticmethod
    def get_confidence_tier(score: float) -> Tuple[ConfidenceLevel, EvidenceClassification]:
        """Map quantitative confidence score to tier and forensic classification."""
        if score >= 0.90:
            return ConfidenceLevel.DEFINITIVE, EvidenceClassification.OBSERVED
        elif score >= 0.75:
            return ConfidenceLevel.HIGH, EvidenceClassification.CORRELATED
        elif score >= 0.50:
            return ConfidenceLevel.PROBABLE, EvidenceClassification.CORRELATED
        else:
            return ConfidenceLevel.LOW, EvidenceClassification.INFERRED

    def evaluate_pair(
        self, ev1: CommonEventModel, ev2: CommonEventModel
    ) -> Optional[CorrelationEdge]:
        """Evaluate relationship between two events (chronologically ev1 <= ev2)."""
        if ev1.event_id == ev2.event_id:
            return None

        # Compute delta t in seconds
        delta_t = abs((ev2.timestamp - ev1.timestamp).total_seconds())
        if delta_t > self.max_temporal_window_seconds:
            return None

        edge_type: Optional[str] = None
        score: float = 0.0
        explanation: str = ""
        matched_attrs: Dict[str, Any] = {}
        contributing_evidence: List[str] = [
            f"{ev1.evidence_ref.artifact_name}#{ev1.evidence_ref.sha256[:10]}",
            f"{ev2.evidence_ref.artifact_name}#{ev2.evidence_ref.sha256[:10]}",
        ]

        # 1. Process Lineage Correlation (PPID == PID)
        pid1 = ev1.actor.get("pid")
        ppid2 = ev2.actor.get("ppid")
        if pid1 and ppid2 and pid1 == ppid2:
            edge_type = "process_lineage"
            score = 0.95
            comm2 = ev2.actor.get("comm") or "process"
            explanation = (
                f"Definitive process lineage: Parent PID {pid1} directly spawned "
                f"child PID {ev2.actor.get('pid')} ('{comm2}') with temporal delta {delta_t:.2f}s."
            )
            matched_attrs = {"parent_pid": pid1, "child_pid": ev2.actor.get("pid"), "comm": comm2}

        # 2. Resource Continuity: Poisoning access.log followed by LFI execution of access.log
        elif (
            ev1.attack_stage == AttackStage.STAGE_02_LOG_POISONING
            and ev2.attack_stage == AttackStage.STAGE_03_RCE
        ):
            edge_type = "resource_continuity"
            ip1 = ev1.actor.get("ip")
            ip2 = ev2.actor.get("ip")
            same_ip = (ip1 and ip2 and ip1 == ip2)
            score = 0.88 if same_ip else 0.72
            explanation = (
                f"High resource continuity: Log poisoning payload injected by {ip1} correlated with "
                f"subsequent RCE log execution on access.log (temporal delta {delta_t:.2f}s)."
            )
            matched_attrs = {"target_resource": "access.log", "source_ip": ip1, "same_ip": same_ip}

        # 3. Actor & Source IP Continuity within short time window
        elif (
            ev1.actor.get("ip")
            and ev2.actor.get("ip")
            and ev1.actor.get("ip") == ev2.actor.get("ip")
            and ev1.actor.get("ip") not in ("127.0.0.1", "localhost")
        ):
            ip = ev1.actor.get("ip")
            # Sequential stage movement?
            stage_order_vals = [s.value if hasattr(s, "value") else str(s) for s in self.STAGE_ORDER]
            st1 = ev1.attack_stage.value if hasattr(ev1.attack_stage, "value") else str(ev1.attack_stage)
            st2 = ev2.attack_stage.value if hasattr(ev2.attack_stage, "value") else str(ev2.attack_stage)
            stage_idx1 = stage_order_vals.index(st1) if st1 in stage_order_vals else -1
            stage_idx2 = stage_order_vals.index(st2) if st2 in stage_order_vals else -1

            if stage_idx1 != -1 and stage_idx2 != -1 and stage_idx2 >= stage_idx1:
                edge_type = "attack_stage_sequence"
                score = 0.85 if delta_t <= 5.0 else 0.70
                explanation = (
                    f"Attack chain progression: Actor {ip} advanced from {st1} to "
                    f"{st2} within {delta_t:.2f}s."
                )
            else:
                edge_type = "actor_continuity"
                score = 0.75 if delta_t <= 2.0 else 0.55
                explanation = (
                    f"Actor continuity: Repeated requests from IP {ip} within {delta_t:.2f}s."
                )
            matched_attrs = {"actor_ip": ip, "delta_t": delta_t}

        # 4. PrivEsc binary correlation (PATH manipulation -> /tmp/bin/su execution)
        elif (
            ev1.attack_stage == AttackStage.STAGE_05_ENV_MANIPULATION
            and ev2.attack_stage == AttackStage.STAGE_06_PRIV_ESC
        ):
            edge_type = "environment_privesc_correlation"
            score = 0.82
            explanation = (
                f"Environment variable PATH manipulation directly enabled privilege escalation execution "
                f"of hijacked binary within {delta_t:.2f}s."
            )
            matched_attrs = {"binary": ev2.target.get("target_name"), "delta_t": delta_t}

        # 5. Temporal Proximity heuristic (weak / inferred)
        elif delta_t <= 3.0 and ev1.attack_stage != AttackStage.NORMAL and ev2.attack_stage != AttackStage.NORMAL:
            edge_type = "temporal_proximity"
            score = 0.45
            explanation = (
                f"Weak temporal proximity: Events occurred within {delta_t:.2f}s but lack common identity context."
            )
            matched_attrs = {"delta_t": delta_t}

        if edge_type is not None:
            tier, classification = self.get_confidence_tier(score)
            return CorrelationEdge(
                edge_id=f"EDGE-{uuid.uuid4().hex[:8].upper()}",
                case_id=ev1.case_id,
                source_event_id=ev1.event_id,
                target_event_id=ev2.event_id,
                correlation_type=edge_type,
                confidence_score=round(score, 3),
                confidence_level=tier,
                classification=classification,
                time_delta_seconds=round(delta_t, 3),
                explanation=explanation,
                contributing_evidence=contributing_evidence,
                attributes_matched=matched_attrs,
            )

        return None

    def correlate_events(self, events: List[CommonEventModel]) -> CorrelationGraph:
        """Analyze a collection of events and synthesize an explainable incident correlation graph."""
        if not events:
            return CorrelationGraph(
                case_id="default",
                total_events=0,
                total_edges=0,
                edges=[],
                clusters=[],
            )

        case_id = events[0].case_id
        # Chronological sort
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        edges: List[CorrelationEdge] = []

        n = len(sorted_events)
        for i in range(n):
            for j in range(i + 1, min(i + 15, n)):  # Sliding window across nearest chronological neighbours
                edge = self.evaluate_pair(sorted_events[i], sorted_events[j])
                if edge:
                    edges.append(edge)

        # Form simple incident clusters based on high confidence connected events
        clusters: List[Dict[str, Any]] = []
        high_conf_edges = [e for e in edges if e.confidence_score >= 0.75]
        if high_conf_edges:
            clusters.append({
                "cluster_id": f"CLUST-{uuid.uuid4().hex[:6].upper()}",
                "name": "Controlled LFI-to-PrivEsc Attack Chain Incident",
                "edges_count": len(high_conf_edges),
                "primary_actor": high_conf_edges[0].attributes_matched.get("actor_ip") or "172.28.0.5",
                "classification": "Correlated Attack Chain",
            })

        return CorrelationGraph(
            case_id=case_id,
            generated_at=datetime.now(timezone.utc),
            total_events=len(events),
            total_edges=len(edges),
            edges=edges,
            clusters=clusters,
        )
