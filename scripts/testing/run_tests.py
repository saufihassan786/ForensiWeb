#!/usr/bin/env python3
"""
ForensiWeb Automated Test Suite Runner.

Executes tests across the testing pyramid (unit, integration, e2e, lab, regression)
with standard reporting and exit-code forwarding for CI/CD pipelines.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_tests.py",
        description="ForensiWeb Test Suite Runner"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="Run only tests marked as 'unit'")
    group.add_argument("--integration", action="store_true", help="Run only tests marked as 'integration'")
    group.add_argument("--e2e", action="store_true", help="Run only tests marked as 'e2e'")
    group.add_argument("--lab", action="store_true", help="Run only tests marked as 'lab'")
    group.add_argument("--regression", action="store_true", help="Run only tests marked as 'regression'")
    group.add_argument("--hygiene", action="store_true", help="Run Git hygiene and ignore validation")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose pytest output")
    parser.add_argument("-x", "--failfast", action="store_true", help="Stop execution on first failure")
    parser.add_argument("-k", "--keyword", help="Filter tests by keyword expression")
    parser.add_argument("target", nargs="?", default=None, help="Optional test file or directory target")

    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    # Hygiene check mode
    if args.hygiene:
        print("=== Running Git Hygiene Checks ===")
        hygiene_script = REPO_ROOT / "scripts" / "testing" / "check_git_hygiene.py"
        return subprocess.run([sys.executable, str(hygiene_script)]).returncode

    # Build pytest invocation
    cmd = [sys.executable, "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.failfast:
        cmd.append("-x")

    if args.keyword:
        cmd.extend(["-k", args.keyword])

    # Marker dispatch
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.e2e:
        cmd.extend(["-m", "e2e"])
    elif args.lab:
        cmd.extend(["-m", "lab"])
    elif args.regression:
        cmd.extend(["-m", "regression"])

    if args.target:
        cmd.append(args.target)

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
