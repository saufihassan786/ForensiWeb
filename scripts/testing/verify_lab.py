"""ForensiWeb — Phase 05 Isolated Laboratory Environment Verification Protocol.

Validates that all 7 features of Phase 5 are implemented according to
architecture.md, threat-model.md, and task.md before Phase 5 completion sign-off:
- PHASE-05-F01: Lab Container Topology
- PHASE-05-F02: Dedicated Lab Network
- PHASE-05-F03: Supporting Services (Log Collector)
- PHASE-05-F04: Scenario Configuration (WEB-CHAIN-001.yaml)
- PHASE-05-F05: Lab Reset
- PHASE-05-F06: Lab Health Status
- PHASE-05-F07: Reproducibility Verification (End-to-End Cycle)
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Ensure vuln_app is registered
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

from lab.scripts.check_lab_health import LabHealthChecker
from lab.scripts.log_collector import EvidenceCollector
from lab.scripts.reset_lab import LabResetManager
from vuln_app.config import LabConfig
from vuln_app.main import create_app


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    msg = f"[{status}] {name}"
    if details and not condition:
        msg += f" -> {details}"
    print(msg)
    return condition


def verify_f01_container_topology() -> bool:
    """Verify container topology, resource limits, and capability dropping."""
    compose_path = REPO_ROOT / "docker-compose.yml"
    lab_compose_path = REPO_ROOT / "lab" / "docker" / "docker-compose.lab.yml"
    dockerfile_path = REPO_ROOT / "apps" / "vulnerable-web-app" / "Dockerfile"

    compose_txt = compose_path.read_text(encoding="utf-8") if compose_path.is_file() else ""
    lab_compose_txt = lab_compose_path.read_text(encoding="utf-8") if lab_compose_path.is_file() else ""
    dockerfile_txt = dockerfile_path.read_text(encoding="utf-8") if dockerfile_path.is_file() else ""

    cond = (
        "cap_drop:" in compose_txt
        and "512M" in compose_txt
        and "forensiweb-lab-target" in lab_compose_txt
        and "USER labuser" in dockerfile_txt
    )
    return check("PHASE-05-F01: Lab Container Topology", cond)


def verify_f02_dedicated_lab_network() -> bool:
    """Verify dedicated isolated network with zero external internet egress."""
    compose_path = REPO_ROOT / "docker-compose.yml"
    lab_compose_path = REPO_ROOT / "lab" / "docker" / "docker-compose.lab.yml"

    compose_txt = compose_path.read_text(encoding="utf-8") if compose_path.is_file() else ""
    lab_compose_txt = lab_compose_path.read_text(encoding="utf-8") if lab_compose_path.is_file() else ""

    cond = (
        "internal: true" in compose_txt
        and "forensiweb-lab-net" in compose_txt
        and "internal: true" in lab_compose_txt
        and "127.0.0.1:" in compose_txt
    )
    return check("PHASE-05-F02: Dedicated Lab Network", cond)


def verify_f03_supporting_services() -> bool:
    """Verify evidence collector ingests, hashes, and produces manifest."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_src = Path(tmp_dir) / "src"
        tmp_dest = Path(tmp_dir) / "dest"
        tmp_src.mkdir()

        # Seed sample log
        (tmp_src / "access.log").write_text("127.0.0.1 - - [06/Oct/2026] GET / 200\n", encoding="utf-8")
        (tmp_src / "audit.log").write_text("type=SYSCALL msg=audit(100): comm=sh\n", encoding="utf-8")

        collector = EvidenceCollector(source_dir=tmp_src, dest_dir=tmp_dest, scenario_id="TEST-001")
        manifest = collector.collect(dry_run=False)

        manifest_file = tmp_dest / "TEST-001_acquisition_manifest.json"
        cond = (
            manifest.get("artifact_count") == 2
            and manifest_file.is_file()
            and (tmp_dest / "TEST-001_access.log").is_file()
            and (tmp_dest / "TEST-001_audit.log").is_file()
            and len(manifest["artifacts"][0]["sha256"]) == 64
        )
        return check("PHASE-05-F03: Supporting Services (Evidence Collector)", cond)


def verify_f04_scenario_configuration() -> bool:
    """Verify WEB-CHAIN-001.yaml contains all required scenario specification sections."""
    yaml_file = REPO_ROOT / "lab" / "scenarios" / "WEB-CHAIN-001.yaml"
    if not yaml_file.is_file():
        return check("PHASE-05-F04: Scenario Configuration", False, "Missing WEB-CHAIN-001.yaml")

    try:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        required_keys = [
            "scenario_id",
            "purpose",
            "preconditions",
            "stages",
            "expected_artifacts",
            "expected_timestamps",
            "expected_evidence_sources",
            "reset_procedure",
            "verification_procedure",
            "failure_behavior",
        ]
        has_all_keys = all(k in data for k in required_keys)
        stage_ids = [s.get("id") for s in data.get("stages", [])]
        expected_stages = ["S1", "S2", "S3", "S4", "S5"]
        stages_present = all(s in stage_ids for s in expected_stages)

        cond = has_all_keys and stages_present and data.get("scenario_id") == "WEB-CHAIN-001"
        return check("PHASE-05-F04: Scenario Configuration", cond)
    except Exception as exc:
        return check("PHASE-05-F04: Scenario Configuration", False, str(exc))


def verify_f05_lab_reset() -> bool:
    """Verify reset restores baseline files and cleans logs deterministically."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        fixtures_dir = Path(tmp_dir) / "fixtures"
        logs_dir = fixtures_dir / "logs"
        docs_dir = fixtures_dir / "docs"
        logs_dir.mkdir(parents=True)
        docs_dir.mkdir(parents=True)

        (logs_dir / "access.log").write_text("dummy dirty log data", encoding="utf-8")
        (logs_dir / "audit.log").write_text("dummy dirty audit data", encoding="utf-8")

        manager = LabResetManager(fixtures_dir=fixtures_dir)
        res = manager.reset(dry_run=False, call_api=False)

        access_content = (logs_dir / "access.log").read_text(encoding="utf-8")
        welcome_content = (docs_dir / "welcome.txt").read_text(encoding="utf-8")

        cond = (
            res.get("status") == "success"
            and access_content == ""
            and "Welcome to the Academic Research Portal" in welcome_content
        )
        return check("PHASE-05-F05: Lab Reset", cond)


def verify_f06_lab_health_status() -> bool:
    """Verify health check script correctly reports operational status."""
    checker = LabHealthChecker()
    res = checker.run_full_check()
    cond = (
        res.get("healthy") is True
        and res["checks"]["scenarios"]["status"] == "healthy"
        and res["checks"]["fixtures"]["status"] == "healthy"
        and res["checks"]["isolation"]["status"] == "healthy"
    )
    return check("PHASE-05-F06: Lab Health Status", cond)


def verify_f07_reproducibility_verification() -> bool:
    """Verify full end-to-end reproducibility cycle (reset -> execute S1-S5 -> collect -> reset)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        log_dir = Path(tmp_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        cfg = LabConfig(log_dir=log_dir)
        cfg.docs_dir = Path(tmp_dir) / "docs"
        cfg.docs_dir.mkdir(parents=True, exist_ok=True)
        cfg._init_default_documents()

        app = create_app(cfg)
        client = app.test_client()

        # 1. Reset baseline
        client.post("/api/reset")
        init_status = client.get("/api/status").get_json()

        # 2. Stage S1: LFI Recon
        s1_resp = client.get("/document?file=welcome.txt")

        # 3. Stage S2: Log Poisoning
        s2_resp = client.get(
            "/document?file=welcome.txt",
            headers={"User-Agent": "SIMULATED_POISON_PAYLOAD"}
        )

        # 4. Stage S3: RCE via log inclusion
        s3_resp = client.get("/document?file=access.log&cmd=id")

        # 5. Stage S4: Web Shell
        s4_resp = client.get("/shell?cmd=whoami")

        # 6. Stage S4b: Meterpreter probe
        s4b_resp = client.post("/post-exploitation/meterpreter?lhost=10.0.50.5&lport=4444")

        # 7. Stage S5: PATH PrivEsc
        s5_resp = client.post("/privesc/run-backup", headers={"X-Lab-PATH": "/tmp/bin:/usr/bin"})

        # 8. Evidence Collection
        evidence_dest = Path(tmp_dir) / "evidence"
        collector = EvidenceCollector(source_dir=log_dir, dest_dir=evidence_dest, scenario_id="WEB-CHAIN-001")
        manifest = collector.collect(dry_run=False)

        # 9. Second Reset
        client.post("/api/reset")
        final_status = client.get("/api/status").get_json()

        cond = (
            init_status.get("access_log_lines") == 0
            and s1_resp.status_code == 200
            and s2_resp.status_code == 200
            and s3_resp.status_code == 200
            and s4_resp.status_code == 200
            and s4b_resp.status_code == 200
            and s5_resp.status_code == 200
            and manifest.get("artifact_count") >= 2
            and final_status.get("access_log_lines") == 0
            and final_status.get("is_poisoned") is False
        )
        return check("PHASE-05-F07: Reproducibility Verification", cond)


def run_all_checks() -> bool:
    print("=" * 70)
    print("ForensiWeb Phase 05 — Isolated Laboratory Environment Verification")
    print("=" * 70)
    results = [
        verify_f01_container_topology(),
        verify_f02_dedicated_lab_network(),
        verify_f03_supporting_services(),
        verify_f04_scenario_configuration(),
        verify_f05_lab_reset(),
        verify_f06_lab_health_status(),
        verify_f07_reproducibility_verification(),
    ]
    passed = sum(results)
    total = len(results)
    print("=" * 70)
    print(f"Summary: {passed}/{total} verification checks passed.")
    if passed == total:
        print("[SUCCESS] Phase 05 Isolated Laboratory Environment verified completely!")
        return True
    else:
        print("[FAILURE] Phase 05 verification failed.")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
