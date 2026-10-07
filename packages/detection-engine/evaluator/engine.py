"""Detection Rule Evaluation Engine (PHASE-09-F02, F03, F05, F06).

Coordinates deterministic rule registration, event stream evaluation,
deduplication, explainability generation, and evidence linking.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from models.rule import DetectionAlert, DetectionRuleDefinition
from normalization.schema import CommonEventModel
from rules.scenario_rules import (
    BaseDetectionRule,
    RuleEnvPathManipulation,
    RuleLfiTraversal,
    RuleLogPoisoning,
    RulePrivilegeEscalation,
    RuleRceLogExecution,
    RuleWebShellInteraction,
)

logger = logging.getLogger("forensiweb.detection.engine")


class DetectionEngine:
    """Manages rule registration and deterministic evaluation across normalized events."""

    def __init__(self) -> None:
        self._rules: Dict[str, BaseDetectionRule] = {}

        # Register standard controlled scenario rules
        self.register_rule(RuleLfiTraversal())
        self.register_rule(RuleLogPoisoning())
        self.register_rule(RuleRceLogExecution())
        self.register_rule(RuleWebShellInteraction())
        self.register_rule(RuleEnvPathManipulation())
        self.register_rule(RulePrivilegeEscalation())

    def register_rule(self, rule: BaseDetectionRule) -> None:
        """Register a detection rule."""
        self._rules[rule.definition.rule_id] = rule

    def get_rule(self, rule_id: str) -> Optional[BaseDetectionRule]:
        """Lookup a registered rule by its ID."""
        return self._rules.get(rule_id)

    @property
    def registered_rules(self) -> List[DetectionRuleDefinition]:
        """Return list of all registered rule definitions."""
        return [r.definition for r in self._rules.values()]

    def evaluate_event(self, event: CommonEventModel) -> List[DetectionAlert]:
        """Evaluate all registered rules against a single normalized event."""
        alerts: List[DetectionAlert] = []
        for rule_id, rule in self._rules.items():
            try:
                alert = rule.evaluate(event)
                if alert is not None:
                    alerts.append(alert)
            except Exception as exc:
                logger.error("Error evaluating rule %s on event %s: %s", rule_id, event.event_id, exc)
        return alerts

    def evaluate_batch(self, events: List[CommonEventModel]) -> List[DetectionAlert]:
        """Evaluate rules across an ordered sequence of events, preserving evidence links."""
        all_alerts: List[DetectionAlert] = []
        for event in events:
            alerts = self.evaluate_event(event)
            all_alerts.extend(alerts)
        return all_alerts
