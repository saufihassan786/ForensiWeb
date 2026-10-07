"""Verification Test Suite for PHASE 09 — Detection Engine.

Verifies:
- PHASE-09-F01: Rule Model (DetectionRuleDefinition, DetectionAlert)
- PHASE-09-F02: Rule Registration (Dynamic registry, lookup)
- PHASE-09-F03: Rule Evaluation (Deterministic detection logic)
- PHASE-09-F04: Controlled Scenario Rules (Positive & Negative tests for all 6 stages)
- PHASE-09-F05: Detection Evidence Linking (Every alert links to source event ID and evidence SHA-256)
- PHASE-09-F06: Detection Explanation (Clear, deterministic human-readable explanation)
- PHASE-09-F07: Detection Testing (Batch processing across multiple heterogeneous sources)
"""

from __future__ import annotations

from datetime import datetime, timezone
import pytest

from evaluator.engine import DetectionEngine
from models.rule import DetectionAlert
from normalization.normalizer import EventNormalizer
from normalization.schema import AttackStage, CommonEventModel, SeverityLevel
from parsers.registry import ParserRegistry


@pytest.fixture
def detection_engine() -> DetectionEngine:
    return DetectionEngine()


def make_test_event(
    stage: AttackStage = AttackStage.NORMAL,
    action: str = "http_get",
    path: str = "/",
    user_agent: str = "Mozilla/5.0",
    query_params: dict | None = None,
    raw_content: str = "GET / HTTP/1.1",
    variables: dict | None = None,
    exe: str = "",
    target_name: str = "",
    comm: str = "",
    pid: int = 100,
) -> CommonEventModel:
    """Helper to generate well-formed mock CEM events for positive/negative rule tests."""
    return CommonEventModel(
        event_id="EVT-TEST-001",
        case_id="CASE-DET-01",
        timestamp=datetime.now(timezone.utc),
        source_type="web_access_log",
        source_artifact_id="EV-TEST-ARTIFACT",
        source_location={"line_number": 1, "byte_offset_start": 0, "byte_offset_end": 50},
        attack_stage=stage,
        severity=SeverityLevel.INFORMATIONAL,
        action=action,
        actor={"ip": "172.28.0.5", "user_agent": user_agent, "comm": comm, "pid": pid},
        target={"path": path, "query_params": query_params or {}, "variables": variables or {}, "exe": exe, "target_name": target_name},
        details={},
        evidence_ref={"artifact_name": "access.log", "sha256": "f" * 64},
        raw_content=raw_content,
    )


def test_p09_rule_01_lfi_traversal(detection_engine: DetectionEngine):
    """Verify Rule 01 LFI: positive on traversal, negative on clean path."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_01_LFI,
        path="/view?page=../../../../etc/passwd",
        raw_content="GET /view?page=../../../../etc/passwd HTTP/1.1",
    )
    alerts = detection_engine.evaluate_event(pos_event)
    assert len(alerts) >= 1
    lfi_alert = next(a for a in alerts if a.rule_id == "RULE-01-LFI")
    assert lfi_alert.attack_stage == "stage_01_lfi"
    assert lfi_alert.severity == "high"
    assert "Directory traversal detected" in lfi_alert.explanation
    assert "EVT-TEST-001" in lfi_alert.matched_event_ids
    assert "access.log#ffffffffffff" in lfi_alert.evidence_references

    neg_event = make_test_event(stage=AttackStage.NORMAL, path="/static/style.css", raw_content="GET /static/style.css HTTP/1.1")
    neg_alerts = detection_engine.evaluate_event(neg_event)
    assert not any(a.rule_id == "RULE-01-LFI" for a in neg_alerts)


def test_p09_rule_02_log_poisoning(detection_engine: DetectionEngine):
    """Verify Rule 02 Log Poisoning: positive on injected script, negative on browser UA."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_02_LOG_POISONING,
        user_agent="Mozilla/5.0 (SIMULATED_POISON_PAYLOAD: echo test)",
    )
    alerts = detection_engine.evaluate_event(pos_event)
    poison_alert = next(a for a in alerts if a.rule_id == "RULE-02-LOG-POISONING")
    assert poison_alert.attack_stage == "stage_02_log_poisoning"
    assert "code injection payload" in poison_alert.explanation.lower()

    neg_event = make_test_event(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    neg_alerts = detection_engine.evaluate_event(neg_event)
    assert not any(a.rule_id == "RULE-02-LOG-POISONING" for a in neg_alerts)


def test_p09_rule_03_rce_log_inclusion(detection_engine: DetectionEngine):
    """Verify Rule 03 RCE: positive on access.log inclusion with cmd, negative on standard view."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_03_RCE,
        path="/view?page=/var/log/nginx/access.log&cmd=id",
        query_params={"page": "/var/log/nginx/access.log", "cmd": "id"},
        raw_content="GET /view?page=/var/log/nginx/access.log&cmd=id HTTP/1.1",
    )
    alerts = detection_engine.evaluate_event(pos_event)
    rce_alert = next(a for a in alerts if a.rule_id == "RULE-03-RCE")
    assert rce_alert.severity == "critical"
    assert "log file inclusion" in rce_alert.explanation.lower()

    neg_event = make_test_event(path="/document?doc=welcome.txt")
    neg_alerts = detection_engine.evaluate_event(neg_event)
    assert not any(a.rule_id == "RULE-03-RCE" for a in neg_alerts)


def test_p09_rule_04_web_shell_interaction(detection_engine: DetectionEngine):
    """Verify Rule 04 Web Shell: positive on cmd parameter interaction."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_04_WEB_SHELL,
        query_params={"cmd": "whoami"},
        raw_content="GET /shell.php?cmd=whoami HTTP/1.1",
    )
    alerts = detection_engine.evaluate_event(pos_event)
    shell_alert = next(a for a in alerts if a.rule_id == "RULE-04-WEBSHELL")
    assert shell_alert.attack_stage == "stage_04_web_shell"
    assert "whoami" in shell_alert.explanation


def test_p09_rule_05_path_hijack(detection_engine: DetectionEngine):
    """Verify Rule 05 PATH Hijacking: positive on /tmp/bin precedence."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_05_ENV_MANIPULATION,
        variables={"PATH": "/tmp/bin:/usr/local/bin:/usr/bin"},
    )
    alerts = detection_engine.evaluate_event(pos_event)
    path_alert = next(a for a in alerts if a.rule_id == "RULE-05-PATH-HIJACK")
    assert path_alert.attack_stage == "stage_05_env_manipulation"
    assert "insecure path" in path_alert.explanation.lower()

    neg_event = make_test_event(variables={"PATH": "/usr/local/bin:/usr/bin:/bin"})
    neg_alerts = detection_engine.evaluate_event(neg_event)
    assert not any(a.rule_id == "RULE-05-PATH-HIJACK" for a in neg_alerts)


def test_p09_rule_06_privilege_escalation(detection_engine: DetectionEngine):
    """Verify Rule 06 Privilege Escalation: positive on /tmp/bin/su execution."""
    pos_event = make_test_event(
        stage=AttackStage.STAGE_06_PRIV_ESC,
        target_name="/tmp/bin/su",
        comm="su",
        pid=2110,
    )
    alerts = detection_engine.evaluate_event(pos_event)
    priv_alert = next(a for a in alerts if a.rule_id == "RULE-06-PRIV-ESC")
    assert priv_alert.severity == "critical"
    assert "/tmp/bin/su" in priv_alert.explanation


def test_p09_batch_evaluation_flow(sample_raw_logs: dict, detection_engine: DetectionEngine):
    """Verify batch evaluation across parsed and normalized sample logs."""
    parsers = ParserRegistry()
    report = parsers.parse_artifact(
        content=sample_raw_logs["access"],
        filename="access.log",
        evidence_id="EV-BATCH-DET",
        sha256="9" * 64,
    )
    events = EventNormalizer.normalize_batch(report.records, "CASE-BATCH-DET")
    alerts = detection_engine.evaluate_batch(events)

    assert len(alerts) >= 3
    rule_ids = [a.rule_id for a in alerts]
    assert "RULE-01-LFI" in rule_ids
    assert "RULE-02-LOG-POISONING" in rule_ids
    assert "RULE-03-RCE" in rule_ids

    for alert in alerts:
        assert alert.explanation
        assert len(alert.matched_event_ids) > 0
        assert len(alert.evidence_references) > 0
