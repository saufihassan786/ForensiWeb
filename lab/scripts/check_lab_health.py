"""ForensiWeb — Laboratory Health & Readiness Status Probe (PHASE-05-F06).

Validates the operational readiness, isolation configuration, and file integrity
of the isolated laboratory environment:
- Verification of scenario descriptors (YAML & JSON)
- File system access and write permissions in fixture directories
- Strict network isolation confirmation in compose manifests (internal: true)
- Target application responsiveness (online HTTP check or standby validation)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class LabHealthChecker:
    """Performs deep health and safety checks on the laboratory environment."""

    def __init__(self, api_url: str = "http://127.0.0.1:5000") -> None:
        self.api_url = api_url.rstrip("/")

    def check_scenario_definitions(self) -> Dict[str, Any]:
        """Verify YAML and JSON scenario descriptors."""
        scenario_yaml = REPO_ROOT / "lab" / "scenarios" / "WEB-CHAIN-001.yaml"
        catalogue_json = REPO_ROOT / "lab" / "scenarios" / "artifacts_catalogue.json"

        yaml_valid = False
        json_valid = False
        details: List[str] = []

        if scenario_yaml.is_file():
            try:
                data = yaml.safe_load(scenario_yaml.read_text(encoding="utf-8"))
                if data and data.get("scenario_id") == "WEB-CHAIN-001":
                    yaml_valid = True
            except Exception as e:
                details.append(f"YAML parse error: {e}")
        else:
            details.append("WEB-CHAIN-001.yaml missing")

        if catalogue_json.is_file():
            try:
                cdata = json.loads(catalogue_json.read_text(encoding="utf-8"))
                if cdata and cdata.get("scenario_id") == "WEB-CHAIN-001":
                    json_valid = True
            except Exception as e:
                details.append(f"Catalogue JSON parse error: {e}")
        else:
            details.append("artifacts_catalogue.json missing")

        return {
            "status": "healthy" if (yaml_valid and json_valid) else "unhealthy",
            "yaml_valid": yaml_valid,
            "json_valid": json_valid,
            "details": details,
        }

    def check_fixture_directories(self) -> Dict[str, Any]:
        """Verify logs and docs fixtures exist and have correct permissions."""
        fixtures_dir = REPO_ROOT / "lab" / "fixtures"
        logs_dir = fixtures_dir / "logs"
        docs_dir = fixtures_dir / "docs"

        logs_writable = False
        docs_intact = False

        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            test_file = logs_dir / ".health_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink()
            logs_writable = True
        except Exception:
            logs_writable = False

        welcome_file = docs_dir / "welcome.txt"
        about_file = docs_dir / "about.txt"
        docs_intact = welcome_file.is_file() and about_file.is_file()

        healthy = logs_writable and docs_intact
        return {
            "status": "healthy" if healthy else "unhealthy",
            "logs_writable": logs_writable,
            "docs_intact": docs_intact,
        }

    def check_isolation_configuration(self) -> Dict[str, Any]:
        """Verify internal network and localhost-only bindings in compose manifests."""
        root_compose = REPO_ROOT / "docker-compose.yml"
        lab_compose = REPO_ROOT / "lab" / "docker" / "docker-compose.lab.yml"

        internal_net_declared = False
        localhost_bound = False

        content = ""
        if root_compose.is_file():
            content += root_compose.read_text(encoding="utf-8")
        if lab_compose.is_file():
            content += lab_compose.read_text(encoding="utf-8")

        if "internal: true" in content:
            internal_net_declared = True
        if "127.0.0.1:" in content:
            localhost_bound = True

        healthy = internal_net_declared and localhost_bound
        return {
            "status": "healthy" if healthy else "unhealthy",
            "internal_network": internal_net_declared,
            "localhost_bound": localhost_bound,
        }

    def check_target_connectivity(self) -> Dict[str, Any]:
        """Check live HTTP connectivity to target application if running."""
        try:
            status_url = f"{self.api_url}/api/status"
            req = urllib.request.Request(status_url, headers={"User-Agent": "ForensiWeb-HealthCheck"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "status": "online",
                        "accessible": True,
                        "data": data,
                    }
        except Exception:
            pass

        return {
            "status": "standby",
            "accessible": False,
            "message": "Service offline or in container test mode (expected when containers are halted)",
        }

    def run_full_check(self) -> Dict[str, Any]:
        scenarios = self.check_scenario_definitions()
        fixtures = self.check_fixture_directories()
        isolation = self.check_isolation_configuration()
        connectivity = self.check_target_connectivity()

        # Lab is healthy if descriptors, fixtures, and isolation are all confirmed
        all_healthy = (
            scenarios["status"] == "healthy"
            and fixtures["status"] == "healthy"
            and isolation["status"] == "healthy"
        )

        return {
            "healthy": all_healthy,
            "checks": {
                "scenarios": scenarios,
                "fixtures": fixtures,
                "isolation": isolation,
                "target_connectivity": connectivity,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="ForensiWeb Laboratory Health Check")
    parser.add_argument("--api-url", type=str, default="http://127.0.0.1:5000", help="Vulnerable app base URL")
    args = parser.parse_args()

    checker = LabHealthChecker(api_url=args.api_url)
    res = checker.run_full_check()
    print(json.dumps(res, indent=2))
    return 0 if res.get("healthy") else 1


if __name__ == "__main__":
    sys.exit(main())
