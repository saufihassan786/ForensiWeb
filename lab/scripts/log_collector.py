"""ForensiWeb — Laboratory Log & Telemetry Collector (PHASE-05-F03).

Collects generated logs from the isolated laboratory environment, computes
cryptographic SHA-256 hashes to guarantee evidence integrity, generates an
acquisition manifest, and writes preserved artifacts to data/evidence/original/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def calculate_sha256(file_path: Path) -> str:
    """Compute hex-encoded SHA-256 digest of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class EvidenceCollector:
    """Manages forensic evidence intake and preservation from lab environments."""

    def __init__(
        self,
        source_dir: Optional[Path] = None,
        dest_dir: Optional[Path] = None,
        scenario_id: str = "WEB-CHAIN-001",
    ) -> None:
        self.source_dir = source_dir or (REPO_ROOT / "lab" / "fixtures" / "logs")
        self.dest_dir = dest_dir or (REPO_ROOT / "data" / "evidence" / "original")
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        self.scenario_id = scenario_id

    def collect(self, dry_run: bool = False) -> Dict[str, Any]:
        """Collect all log files from source directory, hash, and preserve."""
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        collected_artifacts: List[Dict[str, Any]] = []

        if not self.source_dir.exists():
            return {
                "status": "error",
                "message": f"Source directory {self.source_dir} does not exist",
                "artifacts": [],
            }

        # Look for target log files
        target_files = [f for f in self.source_dir.glob("*.log") if f.is_file()]

        for src_file in target_files:
            file_size = src_file.stat().st_size
            file_hash = calculate_sha256(src_file)

            # Generate target preserved filename with timestamp prefix for forensic provenance
            dest_filename = f"{self.scenario_id}_{src_file.name}"
            dest_path = self.dest_dir / dest_filename

            if not dry_run:
                shutil.copy2(src_file, dest_path)
                # Verify destination hash matches source
                dest_hash = calculate_sha256(dest_path)
                assert dest_hash == file_hash, "Integrity failure during evidence copy!"

            collected_artifacts.append({
                "source_file": str(src_file),
                "preserved_file": str(dest_path),
                "filename": dest_filename,
                "size_bytes": file_size,
                "sha256": file_hash,
                "acquired_at": timestamp_iso,
            })

        manifest = {
            "scenario_id": self.scenario_id,
            "acquisition_timestamp": timestamp_iso,
            "collector_version": "1.0.0",
            "source_dir": str(self.source_dir),
            "dest_dir": str(self.dest_dir),
            "dry_run": dry_run,
            "artifact_count": len(collected_artifacts),
            "artifacts": collected_artifacts,
        }

        if not dry_run:
            manifest_path = self.dest_dir / f"{self.scenario_id}_acquisition_manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="ForensiWeb Laboratory Log & Evidence Collector")
    parser.add_argument("--source", type=str, help="Source log directory (defaults to lab/fixtures/logs)")
    parser.add_argument("--dest", type=str, help="Destination evidence directory (defaults to data/evidence/original)")
    parser.add_argument("--scenario", type=str, default="WEB-CHAIN-001", help="Scenario ID (default: WEB-CHAIN-001)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate collection without writing files")
    args = parser.parse_args()

    source = Path(args.source) if args.source else None
    dest = Path(args.dest) if args.dest else None

    collector = EvidenceCollector(source_dir=source, dest_dir=dest, scenario_id=args.scenario)
    manifest = collector.collect(dry_run=args.dry_run)

    print(json.dumps(manifest, indent=2))
    return 0 if manifest.get("artifact_count", 0) > 0 or args.dry_run else 1


if __name__ == "__main__":
    sys.exit(main())
