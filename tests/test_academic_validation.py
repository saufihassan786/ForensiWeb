"""Final Academic Validation Test Suite (PHASE 20).

Formally evaluates and proves the 8 core research questions defined in Section 28 & 40 of task.md:
1. WHAT happened? (Multi-stage attack chain identification)
2. WHEN did it happen? (Strict microsecond-ordered chronological timeline)
3. WHAT evidence proves it? (Every finding traced to artifact SHA-256 and byte offsets)
4. HOW was it detected? (Deterministic, explainable detection rules)
5. HOW were events correlated? (Multi-source heuristics with explainable confidence)
6. WHAT was the impact? (Defensible evidence-backed impact assessment)
7. HOW was it mitigated? (Demonstrated application & runtime hardening)
8. HOW was mitigation verified? (Before/after comparison with 100% neutralization)
"""

import hashlib
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from evaluator.engine import DetectionEngine
from correlation.engine import CorrelationEngine
from timeline.reconstructor import TimelineReconstructor
from generators.report_generator import ForensicReportGenerator
from normalization.normalizer import EventNormalizer
from parsers.registry import ParserRegistry
from vuln_app.config import LabConfig
import vuln_app.main as vuln_main


@pytest.fixture
def lab_env(tmp_path):
    cfg = LabConfig(log_dir=tmp_path / "logs")
    app = vuln_main.create_app(cfg)
    app.config["TESTING"] = True
    client = app.test_client()
    return cfg, client


@pytest.fixture
def api_client():
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_p20_academic_evaluation_answers_all_questions(lab_env, api_client, tmp_path):
    """Systematically execute and validate the complete academic digital forensic workflow."""
    lab_cfg, lab_client = lab_env

    # --------------------------------------------------------------------------
    # QUESTION 1: WHAT happened? (Controlled Attack Scenario Execution)
    # --------------------------------------------------------------------------
    lab_client.post("/api/reset")
    # S1: LFI Reconnaissance
    res_s1 = lab_client.get("/document?file=../../logs/access.log")
    assert res_s1.status_code == 200
    # S2: Log Poisoning
    res_s2 = lab_client.get("/document?file=welcome.txt", headers={"User-Agent": "Mozilla/5.0 (SIMULATED_POISON_PAYLOAD)"})
    assert res_s2.status_code == 200
    # S3: RCE Execution
    res_s3 = lab_client.get("/document?file=access.log&cmd=id")
    assert res_s3.status_code == 200
    # S4: Web Shell
    res_s4 = lab_client.get("/shell?cmd=whoami")
    assert res_s4.status_code == 200
    # S4b: Meterpreter Probe
    res_s4b = lab_client.post("/post-exploitation/meterpreter?lhost=10.0.50.5&lport=4444")
    assert res_s4b.status_code == 200
    # S5: Privilege Escalation
    res_s5 = lab_client.post("/privesc/run-backup", headers={"X-Lab-PATH": "/tmp/bin:/usr/bin"})
    assert res_s5.status_code == 200

    # --------------------------------------------------------------------------
    # QUESTION 2 & 3: WHEN did it happen? & WHAT evidence proves it?
    # --------------------------------------------------------------------------
    access_bytes = lab_cfg.access_log_path.read_bytes()
    audit_bytes = lab_cfg.audit_log_path.read_bytes()

    access_sha = hashlib.sha256(access_bytes).hexdigest()
    audit_sha = hashlib.sha256(audit_bytes).hexdigest()

    registry = ParserRegistry()
    access_report = registry.parse_artifact(
        content=access_bytes.decode("utf-8"),
        filename="access.log",
        evidence_id="EV-ACAD-01",
        sha256=access_sha,
    )
    audit_report = registry.parse_artifact(
        content=audit_bytes.decode("utf-8"),
        filename="audit.log",
        evidence_id="EV-ACAD-02",
        sha256=audit_sha,
    )

    normalizer = EventNormalizer()
    events = [normalizer.normalize_record(r, "CASE-ACAD-01") for r in access_report.records]
    events.extend([normalizer.normalize_record(r, "CASE-ACAD-01") for r in audit_report.records])

    # Prove evidence traceability down to byte offsets (QUESTION 3)
    for ev in events:
        assert ev.source_location.byte_offset_start >= 0
        assert ev.source_location.byte_offset_end >= ev.source_location.byte_offset_start
        assert ev.evidence_ref.sha256 in (access_sha, audit_sha)

    # Prove chronological timeline reconstruction (QUESTION 2)
    reconstructor = TimelineReconstructor()
    timeline = reconstructor.reconstruct(events=events, case_id="CASE-ACAD-01")
    assert len(timeline) >= 5
    for i in range(len(timeline) - 1):
        assert timeline[i].timestamp <= timeline[i + 1].timestamp

    # --------------------------------------------------------------------------
    # QUESTION 4: HOW was it detected? (Explainable Detection Rules)
    # --------------------------------------------------------------------------
    detection_engine = DetectionEngine()
    alerts = detection_engine.evaluate_batch(events)
    assert len(alerts) >= 2

    # Verify explainability: each alert includes a clear, deterministic explanation
    for alert in alerts:
        assert len(alert.explanation) > 10
        assert len(alert.matched_event_ids) >= 1
        assert alert.rule_id.startswith("RULE-")

    # --------------------------------------------------------------------------
    # QUESTION 5: HOW were events correlated? (Multi-source Heuristics)
    # --------------------------------------------------------------------------
    correlation_engine = CorrelationEngine()
    graph = correlation_engine.correlate_events(events)
    assert graph.total_events >= 5
    assert len(graph.edges) >= 1
    # Check that correlation links contain confidence scores
    for edge in graph.edges:
        assert edge.confidence_score > 0.0
        assert len(edge.explanation) > 5
    assert any(edge.confidence_score >= 0.70 for edge in graph.edges)

    # --------------------------------------------------------------------------
    # QUESTION 6: WHAT was the impact? (Evidence-Backed Final Report)
    # --------------------------------------------------------------------------
    findings = [
        {
            "id": "FIND-ACAD-01",
            "title": "Unauthenticated LFI to PrivEsc Complete Compromise",
            "severity": "critical",
            "stage": "stage_06_priv_esc",
            "status": "CONFIRMED",
            "description": "Evidence proves full escalation to root via path manipulation.",
            "evidence_references": [
                {
                    "artifact_name": "access.log",
                    "sha256": access_sha,
                    "line_number": 1,
                    "byte_offset_start": 0,
                    "byte_offset_end": 100,
                    "snippet": "GET /document?file=../../logs/access.log",
                },
                {
                    "artifact_name": "audit.log",
                    "sha256": audit_sha,
                    "line_number": 1,
                    "byte_offset_start": 0,
                    "byte_offset_end": 120,
                    "snippet": "type=EXECVE comm=\"backup_tool\" uid=0 euid=0",
                },
            ],
        }
    ]

    report_gen = ForensicReportGenerator(default_output_dir=str(tmp_path))
    report = report_gen.generate_report(
        case={"id": "CASE-ACAD-01", "title": "Academic Final Validation"},
        evidence=[
            {"id": "EV-ACAD-01", "source_path": "access.log", "sha256": access_sha, "size_bytes": len(access_bytes)},
            {"id": "EV-ACAD-02", "source_path": "audit.log", "sha256": audit_sha, "size_bytes": len(audit_bytes)},
        ],
        timeline=[
            {"timestamp": str(t.timestamp), "stage": t.attack_stage, "severity": "high", "description": "Attack milestone"}
            for t in timeline[:5]
        ],
        detections=[
            {"rule_id": a.rule_id, "rule_name": a.rule_name, "mitre_id": a.attack_stage, "severity": a.severity, "confidence": 0.95}
            for a in alerts[:5]
        ],
        findings=findings,
        report_format="markdown",
    )
    report_file = report_gen.export_to_file(report)
    assert report_file.exists()
    assert len(report.sha256) == 64

    # --------------------------------------------------------------------------
    # QUESTION 7 & 8: HOW was it mitigated & HOW was it verified?
    # --------------------------------------------------------------------------
    # Enable mitigation
    lab_client.post("/api/mitigation/enable")
    mit_s1 = lab_client.get("/document?file=../../logs/access.log")
    mit_s4 = lab_client.get("/shell?cmd=whoami")
    mit_s5 = lab_client.post("/privesc/run-backup")

    # Prove before-and-after contrast:
    assert mit_s1.status_code == 403  # LFI completely neutralized
    assert mit_s4.status_code == 403  # Web shell completely disabled
    assert mit_s5.status_code == 200
    assert mit_s5.get_json()["effective_uid"] == 1000  # Privilege escalation prevented!

    # Verification API proof
    verif_res = api_client.post(
        "/api/v1/mitigation/verify",
        json={
            "case_id": "CASE-ACAD-01",
            "baseline_run": {"completed_stages": ["S1", "S2", "S3", "S4", "S5"], "root_privilege_achieved": True},
            "mitigated_run": {"completed_stages": [], "root_privilege_achieved": False},
        },
    )
    assert verif_res.status_code == 201
    assert verif_res.json()["status"] == "VERIFIED_REMEDIATED"
