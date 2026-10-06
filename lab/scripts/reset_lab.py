"""ForensiWeb — Laboratory State Reset Utility (PHASE-05-F05).

Deterministically resets the isolated laboratory environment back to its initial baseline:
1. Clears generated laboratory log files (access.log, audit.log, error.log).
2. Re-seeds baseline research documents in lab/fixtures/docs/.
3. Optionally invokes the target application's /api/reset endpoint if running.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class LabResetManager:
    """Orchestrates deterministic restoration of laboratory fixtures and target state."""

    def __init__(
        self,
        fixtures_dir: Optional[Path] = None,
        target_api_url: Optional[str] = None,
    ) -> None:
        self.fixtures_dir = fixtures_dir or (REPO_ROOT / "lab" / "fixtures")
        self.logs_dir = self.fixtures_dir / "logs"
        self.docs_dir = self.fixtures_dir / "docs"
        self.target_api_url = target_api_url or "http://127.0.0.1:5000"

    def reset(self, dry_run: bool = False, call_api: bool = True) -> Dict[str, Any]:
        """Perform full laboratory reset."""
        actions_taken: List[str] = []

        # 1. Clear log files
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        for log_name in ["access.log", "audit.log", "error.log"]:
            log_file = self.logs_dir / log_name
            if not dry_run:
                log_file.write_text("", encoding="utf-8")
            actions_taken.append(f"Truncated {log_file}")

        # 2. Re-seed baseline documents
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        welcome_file = self.docs_dir / "welcome.txt"
        about_file = self.docs_dir / "about.txt"

        if not dry_run:
            welcome_file.write_text(
                "Welcome to the Academic Research Portal.\nAuthorized laboratory access only.\n",
                encoding="utf-8",
            )
            about_file.write_text(
                "ForensiWeb Controlled Lab Environment.\nScenario WEB-CHAIN-001.\n",
                encoding="utf-8",
            )
        actions_taken.append(f"Restored {welcome_file}")
        actions_taken.append(f"Restored {about_file}")

        # 3. Optional HTTP reset notification
        api_notified = False
        if call_api:
            try:
                reset_url = f"{self.target_api_url.rstrip('/')}/api/reset"
                req = urllib.request.Request(reset_url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        api_notified = True
                        actions_taken.append("Invoked target /api/reset endpoint successfully")
            except (urllib.error.URLError, TimeoutError, OSError):
                # Service may not be currently running in standalone test mode; this is expected
                actions_taken.append("Target API endpoint not reachable (offline reset applied)")

        return {
            "status": "success",
            "dry_run": dry_run,
            "api_notified": api_notified,
            "actions_count": len(actions_taken),
            "actions": actions_taken,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="ForensiWeb Lab Reset Utility")
    parser.add_argument("--dry-run", action="store_true", help="Simulate reset without altering files")
    parser.add_argument("--no-api", action="store_true", help="Skip invoking the target application /api/reset endpoint")
    parser.add_argument("--api-url", type=str, default="http://127.0.0.1:5000", help="Vulnerable app base URL")
    args = parser.parse_args()

    manager = LabResetManager(target_api_url=args.api_url)
    res = manager.reset(dry_run=args.dry_run, call_api=not args.no_api)
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
