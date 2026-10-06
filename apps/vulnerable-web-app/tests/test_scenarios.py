"""Comprehensive Unit & Integration Tests for Vulnerable Web Application Scenarios.

Verifies:
- PHASE-04-F01: Controlled Target Application
- PHASE-04-F02: Controlled File-Access Scenario (Stage S1)
- PHASE-04-F03: Controlled Logging Scenario
- PHASE-04-F04: Controlled Log-Poisoning Scenario (Stage S2)
- PHASE-04-F05: Controlled RCE Evidence Scenario (Stage S3)
- PHASE-04-F06: Controlled Post-Exploitation Evidence (Stage S4 & S4b)
- PHASE-04-F07: Controlled Environment/PATH Scenario (Stage S5)
- PHASE-04-F08: Scenario Reset
- PHASE-04-F09: Expected Artifact Catalogue Matching
- PHASE-04-F10: Deterministic Execution & Containment Guard
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from flask import Flask
from flask.testing import FlaskClient

try:
    from app.config import LabConfig
    from app.main import create_app
except ImportError:
    from vuln_app.config import LabConfig
    from vuln_app.main import create_app


@pytest.fixture
def temp_lab_config(tmp_path: Path) -> LabConfig:
    """Fixture providing isolated temporary directories for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    cfg = LabConfig(log_dir=log_dir)
    # Ensure baseline documents exist in temp context
    cfg.docs_dir = tmp_path / "docs"
    cfg.docs_dir.mkdir(parents=True, exist_ok=True)
    cfg._init_default_documents()
    return cfg


@pytest.fixture
def client(temp_lab_config: LabConfig) -> FlaskClient:
    """Flask test client initialized with isolated temporary lab config."""
    app = create_app(config=temp_lab_config)
    app.config["TESTING"] = True
    return app.test_client()


def test_index_endpoint(client: FlaskClient) -> None:
    """PHASE-04-F01: Root endpoint provides service discovery and scenario metadata."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "ForensiWeb Controlled Vulnerable Application"
    assert data["scenario"] == "WEB-CHAIN-001 (LFI-to-PrivEsc)"
    assert len(data["stages"]) >= 5
    assert "reset" in data["controls"]


def test_stage_s1_legitimate_document_access(client: FlaskClient) -> None:
    """PHASE-04-F02: Legitimate document retrieval functions correctly."""
    resp = client.get("/document?file=welcome.txt")
    assert resp.status_code == 200
    assert "Welcome to the Academic Research Portal" in resp.text

    resp_about = client.get("/document?file=about.txt")
    assert resp_about.status_code == 200
    assert "ForensiWeb Controlled Lab Environment" in resp_about.text


def test_stage_s1_lfi_reconnaissance_and_containment(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F02: Traversal attempts are contained and logged in access.log."""
    resp = client.get("/document?file=../../../../etc/passwd")
    assert resp.status_code == 404
    assert "[CONTAINMENT_GUARD]" in resp.text

    # Verify request was written to access.log
    assert temp_lab_config.access_log_path.exists()
    log_content = temp_lab_config.access_log_path.read_text(encoding="utf-8")
    assert "GET /document?file=../../../../etc/passwd" in log_content
    assert " 404 " in log_content


def test_stage_s2_controlled_log_poisoning(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F04: Simulated payload token injected into User-Agent appears in access.log."""
    poison_ua = "Mozilla/5.0 (SIMULATED_POISON_PAYLOAD; ForensicTestToken)"
    resp = client.get("/document?file=welcome.txt", headers={"User-Agent": poison_ua})
    assert resp.status_code == 200

    log_content = temp_lab_config.access_log_path.read_text(encoding="utf-8")
    assert "SIMULATED_POISON_PAYLOAD" in log_content
    assert "ForensicTestToken" in log_content


def test_stage_s3_controlled_rce_via_log_inclusion(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F05: Inclusion of access.log with command executes simulated RCE and writes audit log."""
    # First poison the log
    client.get("/document?file=welcome.txt", headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"})

    # Trigger RCE via log inclusion
    resp = client.get("/document?file=access.log&cmd=id")
    assert resp.status_code == 200
    assert "[LOG_INCLUSION_EXECUTION]" in resp.text
    assert "uid=1000(labuser)" in resp.text

    # Verify auditd execution telemetry was created
    audit_content = temp_lab_config.audit_log_path.read_text(encoding="utf-8")
    assert "type=EXECVE" in audit_content
    assert 'comm="sh"' in audit_content
    assert 'a2="id"' in audit_content


def test_stage_s4_controlled_web_shell_interaction(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F06: Web shell endpoint executes simulated commands and emits auditd records."""
    resp = client.get("/shell?cmd=whoami")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "executed"
    assert data["output"] == "labuser"
    assert data["stage"] == "WEB_SHELL"

    audit_content = temp_lab_config.audit_log_path.read_text(encoding="utf-8")
    assert 'a2="whoami"' in audit_content


def test_stage_s4b_controlled_meterpreter_telemetry(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F06: Post-exploitation meterpreter probe generates expected process/network telemetry."""
    resp = client.post("/post-exploitation/meterpreter?lhost=10.0.50.99&lport=4444&session_id=sess-99")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "established"
    assert data["stage"] == "METERPRETER_POST_EXPLOITATION"
    assert data["lhost"] == "10.0.50.99"

    audit_content = temp_lab_config.audit_log_path.read_text(encoding="utf-8")
    assert 'comm="meterpreter_mock"' in audit_content
    assert 'a1="--stage2"' in audit_content


def test_stage_s5_controlled_privilege_escalation(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F07: PATH misconfiguration execution triggers elevated root audit record."""
    resp = client.post("/privesc/run-backup", headers={"X-Lab-PATH": "/tmp/bin:/usr/bin"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["stage"] == "PRIVILEGE_ESCALATION"
    assert data["effective_uid"] == 0
    assert data["effective_user"] == "root"

    audit_content = temp_lab_config.audit_log_path.read_text(encoding="utf-8")
    assert "type=SYSCALL" in audit_content
    assert 'comm="backup_tool"' in audit_content
    assert "uid=0" in audit_content
    assert "euid=0" in audit_content


def test_scenario_reset(client: FlaskClient, temp_lab_config: LabConfig) -> None:
    """PHASE-04-F08: Reset clears all logs and restores baseline."""
    # Generate some logs first
    client.get("/document?file=welcome.txt", headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"})
    client.get("/shell?cmd=id")

    assert temp_lab_config.access_log_path.read_text(encoding="utf-8") != ""
    assert temp_lab_config.audit_log_path.read_text(encoding="utf-8") != ""

    # Call reset
    resp = client.post("/api/reset")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "reset"

    # Confirm logs are cleared
    assert temp_lab_config.access_log_path.read_text(encoding="utf-8") == ""
    assert temp_lab_config.audit_log_path.read_text(encoding="utf-8") == ""


def test_api_status_and_log_views(client: FlaskClient) -> None:
    """PHASE-04-F08: Status endpoint accurately reflects counts and log viewing works."""
    # Reset first
    client.post("/api/reset")
    status_resp = client.get("/api/status")
    assert status_resp.status_code == 200
    status_data = status_resp.get_json()
    assert status_data["access_log_lines"] == 0
    assert status_data["is_poisoned"] is False

    # Perform poisoning
    client.get("/document?file=welcome.txt", headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"})
    status_resp2 = client.get("/api/status")
    status_data2 = status_resp2.get_json()
    assert status_data2["access_log_lines"] > 0
    assert status_data2["is_poisoned"] is True

    # View access log
    log_resp = client.get("/api/logs/access")
    assert log_resp.status_code == 200
    assert "SIMULATED_POISON_PAYLOAD" in log_resp.text
