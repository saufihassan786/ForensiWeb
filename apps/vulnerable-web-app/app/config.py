"""Configuration for Controlled Vulnerable Web Application."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class LabConfig:
    """Settings governing the isolated laboratory simulation and log generation."""

    def __init__(self, log_dir: Path | None = None) -> None:
        self.log_dir = log_dir or (REPO_ROOT / "lab" / "fixtures" / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.access_log_path = self.log_dir / "access.log"
        self.audit_log_path = self.log_dir / "audit.log"
        self.error_log_path = self.log_dir / "error.log"

        # Mitigation state toggle
        self.is_mitigated = False

        # Mock legitimate documents directory
        self.docs_dir = REPO_ROOT / "lab" / "fixtures" / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_documents()

    def _init_default_documents(self) -> None:
        """Seed baseline legitimate documents if not already created."""
        welcome_file = self.docs_dir / "welcome.txt"
        if not welcome_file.exists():
            welcome_file.write_text(
                "Welcome to the Academic Research Portal.\nAuthorized laboratory access only.\n",
                encoding="utf-8",
            )
        about_file = self.docs_dir / "about.txt"
        if not about_file.exists():
            about_file.write_text(
                "ForensiWeb Controlled Lab Environment.\nScenario WEB-CHAIN-001.\n",
                encoding="utf-8",
            )
