"""ForensiWeb — Phase 04 Controlled Vulnerable Application Verification Protocol.

Validates that all 10 features of Phase 4 are implemented according to
architecture.md, threat-model.md, and task.md before Phase 4 completion sign-off:
- PHASE-04-F01: Controlled Target Application
- PHASE-04-F02: Controlled File-Access Scenario
- PHASE-04-F03: Controlled Logging Scenario
- PHASE-04-F04: Controlled Log-Poisoning Scenario
- PHASE-04-F05: Controlled RCE Evidence Scenario
- PHASE-04-F06: Controlled Post-Exploitation Evidence
- PHASE-04-F07: Controlled Environment/PATH Scenario
- PHASE-04-F08: Scenario Reset
- PHASE-04-F09: Expected Artifact Catalogue
- PHASE-04-F10: Vulnerable Application Verification & Isolation
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Ensure vuln_app is imported cleanly
import importlib.util
vuln_app_dir = REPO_ROOT / "apps" / "vulnerable-web-app" / "app"
if "vuln_app" not in sys.modules and vuln_app_dir.is_dir():
    spec = importlib.util.spec_from_file_location(
        "vuln_app",
        vuln_app_dir / "__init__.py",
        submodule_search_locations=[str(vuln_app_dir)],
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["vuln_app"] = mod
        spec.loader.exec_module(mod)

from vuln_app.config import LabConfig
from vuln_app.main import create_app


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    msg = f"[{status}] {name}"
    if details and not condition:
        msg += f" -> {details}"
    print(msg)
    return condition


def verify_f01_target_application() -> bool:
    """Verify Flask application creation and service index endpoint."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        resp = client.get("/")
        data = resp.get_json() or {}
        cond = (
            resp.status_code == 200
            and data.get("service") == "ForensiWeb Controlled Vulnerable Application"
            and len(data.get("stages", [])) >= 5
        )
        return check("PHASE-04-F01: Controlled Target Application", cond)


def verify_f02_file_access_and_containment() -> bool:
    """Verify legitimate document access and traversal containment guard."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        cfg.docs_dir = Path(tmp_dir) / "docs"
        cfg.docs_dir.mkdir(parents=True, exist_ok=True)
        cfg._init_default_documents()
        app = create_app(cfg)
        client = app.test_client()

        legit_resp = client.get("/document?file=welcome.txt")
        traversal_resp = client.get("/document?file=../../../../etc/shadow")
        cond = (
            legit_resp.status_code == 200
            and "Welcome to the Academic Research Portal" in legit_resp.text
            and traversal_resp.status_code == 404
            and "[CONTAINMENT_GUARD]" in traversal_resp.text
        )
        return check("PHASE-04-F02: Controlled File-Access Scenario", cond)


def verify_f03_logging_scenario() -> bool:
    """Verify Apache Combined format logging in access.log."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        client.get("/document?file=welcome.txt")
        access_log = cfg.access_log_path.read_text(encoding="utf-8")
        cond = (
            ' "GET /document?file=welcome.txt HTTP/1.1" ' in access_log
            and cfg.access_log_path.exists()
        )
        return check("PHASE-04-F03: Controlled Logging Scenario", cond)


def verify_f04_log_poisoning_scenario() -> bool:
    """Verify User-Agent poisoning is captured in access.log."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        client.get("/document?file=welcome.txt", headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"})
        access_log = cfg.access_log_path.read_text(encoding="utf-8")
        status_resp = client.get("/api/status")
        status_data = status_resp.get_json() or {}
        cond = (
            "SIMULATED_POISON_PAYLOAD" in access_log
            and status_data.get("is_poisoned") is True
        )
        return check("PHASE-04-F04: Controlled Log-Poisoning Scenario", cond)


def verify_f05_rce_evidence_scenario() -> bool:
    """Verify RCE via log inclusion produces EXECVE telemetry."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        resp = client.get("/document?file=access.log&cmd=id")
        audit_log = cfg.audit_log_path.read_text(encoding="utf-8")
        cond = (
            resp.status_code == 200
            and "[LOG_INCLUSION_EXECUTION]" in resp.text
            and "type=EXECVE" in audit_log
            and 'comm="sh"' in audit_log
        )
        return check("PHASE-04-F05: Controlled RCE Evidence Scenario", cond)


def verify_f06_post_exploitation_evidence() -> bool:
    """Verify web shell and meterpreter telemetry generation."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        shell_resp = client.get("/shell?cmd=whoami")
        shell_data = shell_resp.get_json() or {}
        meterpreter_resp = client.post("/post-exploitation/meterpreter?lhost=10.0.50.10&lport=4444")
        meterpreter_data = meterpreter_resp.get_json() or {}
        audit_log = cfg.audit_log_path.read_text(encoding="utf-8")
        cond = (
            shell_data.get("stage") == "WEB_SHELL"
            and meterpreter_data.get("stage") == "METERPRETER_POST_EXPLOITATION"
            and 'comm="meterpreter_mock"' in audit_log
        )
        return check("PHASE-04-F06: Controlled Post-Exploitation Evidence", cond)


def verify_f07_environment_path_scenario() -> bool:
    """Verify PATH hijacking privilege escalation triggers elevated audit log."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        resp = client.post("/privesc/run-backup", headers={"X-Lab-PATH": "/tmp/bin:/usr/bin"})
        data = resp.get_json() or {}
        audit_log = cfg.audit_log_path.read_text(encoding="utf-8")
        cond = (
            data.get("stage") == "PRIVILEGE_ESCALATION"
            and data.get("effective_uid") == 0
            and 'comm="backup_tool"' in audit_log
            and "uid=0" in audit_log
        )
        return check("PHASE-04-F07: Controlled Environment/PATH Scenario", cond)


def verify_f08_scenario_reset() -> bool:
    """Verify reset clears logs and restores baseline cleanly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cfg = LabConfig(log_dir=Path(tmp_dir) / "logs")
        app = create_app(cfg)
        client = app.test_client()
        client.get("/document?file=welcome.txt", headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"})
        client.get("/shell?cmd=id")
        reset_resp = client.post("/api/reset")
        reset_data = reset_resp.get_json() or {}
        access_log = cfg.access_log_path.read_text(encoding="utf-8")
        audit_log = cfg.audit_log_path.read_text(encoding="utf-8")
        cond = (
            reset_data.get("status") == "reset"
            and access_log == ""
            and audit_log == ""
        )
        return check("PHASE-04-F08: Scenario Reset", cond)


def verify_f09_expected_artifact_catalogue() -> bool:
    """Verify artifacts_catalogue.json matches required scenario schema."""
    catalogue_path = REPO_ROOT / "lab" / "scenarios" / "artifacts_catalogue.json"
    if not catalogue_path.is_file():
        return check("PHASE-04-F09: Expected Artifact Catalogue", False, "Missing artifacts_catalogue.json")
    try:
        data = json.loads(catalogue_path.read_text(encoding="utf-8"))
        artifacts = data.get("artifacts", [])
        artifact_ids = {a.get("id") for a in artifacts}
        expected = {"ART-01", "ART-02", "ART-03", "ART-04", "ART-04b", "ART-05"}
        cond = expected.issubset(artifact_ids) and data.get("scenario_id") == "WEB-CHAIN-001"
        return check("PHASE-04-F09: Expected Artifact Catalogue", cond)
    except Exception as exc:
        return check("PHASE-04-F09: Expected Artifact Catalogue", False, str(exc))


def verify_f10_application_isolation() -> bool:
    """Verify target application strictly enforces safety boundaries."""
    dockerfile_path = REPO_ROOT / "apps" / "vulnerable-web-app" / "Dockerfile"
    compose_path = REPO_ROOT / "docker-compose.yml"
    cond = (
        dockerfile_path.is_file()
        and "USER labuser" in dockerfile_path.read_text(encoding="utf-8")
        and compose_path.is_file()
        and "forensiweb-lab-net" in compose_path.read_text(encoding="utf-8")
        and "127.0.0.1:" in compose_path.read_text(encoding="utf-8")
    )
    return check("PHASE-04-F10: Vulnerable Application Verification", cond)


def run_all_checks() -> bool:
    print("=" * 70)
    print("ForensiWeb Phase 04 — Controlled Vulnerable Application Verification")
    print("=" * 70)
    results = [
        verify_f01_target_application(),
        verify_f02_file_access_and_containment(),
        verify_f03_logging_scenario(),
        verify_f04_log_poisoning_scenario(),
        verify_f05_rce_evidence_scenario(),
        verify_f06_post_exploitation_evidence(),
        verify_f07_environment_path_scenario(),
        verify_f08_scenario_reset(),
        verify_f09_expected_artifact_catalogue(),
        verify_f10_application_isolation(),
    ]
    passed = sum(results)
    total = len(results)
    print("=" * 70)
    print(f"Summary: {passed}/{total} verification checks passed.")
    if passed == total:
        print("[SUCCESS] Phase 04 Controlled Vulnerable Application verified completely!")
        return True
    else:
        print("[FAILURE] Phase 04 verification failed.")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
