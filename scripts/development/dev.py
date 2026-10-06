#!/usr/bin/env python3
"""
ForensiWeb Cross-Platform Developer CLI.

Provides unified command dispatching across Windows, macOS, and Linux without
requiring native make or developer-specific tooling.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def cmd_setup(args: argparse.Namespace) -> int:
    """Initialize local environment and validate configuration."""
    print("=== Step 1: Initializing local environment (.env) ===")
    init_script = REPO_ROOT / "scripts" / "setup" / "init_env.py"
    res = subprocess.run([sys.executable, str(init_script)])
    if res.returncode != 0:
        return res.returncode

    print("\n=== Step 2: Validating environment configuration ===")
    val_script = REPO_ROOT / "scripts" / "setup" / "validate_env.py"
    return subprocess.run([sys.executable, str(val_script)]).returncode


def cmd_validate_env(args: argparse.Namespace) -> int:
    """Validate active .env or template .env.example."""
    val_script = REPO_ROOT / "scripts" / "setup" / "validate_env.py"
    cmd = [sys.executable, str(val_script)]
    if getattr(args, "check_example", False):
        cmd.append("--check-example")
    return subprocess.run(cmd).returncode


def cmd_test(args: argparse.Namespace) -> int:
    """Run pytest test suites."""
    cmd = [sys.executable, "-m", "pytest"]
    if getattr(args, "marker", None):
        cmd.extend(["-m", args.marker])
    if getattr(args, "keyword", None):
        cmd.extend(["-k", args.keyword])
    if getattr(args, "extra_args", None):
        cmd.extend(args.extra_args)
    return subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode


def cmd_hygiene(args: argparse.Namespace) -> int:
    """Verify Git ignore rules and repository hygiene."""
    script = REPO_ROOT / "scripts" / "testing" / "check_git_hygiene.py"
    return subprocess.run([sys.executable, str(script)]).returncode


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean Python __pycache__, .pytest_cache, and temporary build files."""
    print("Cleaning cache and temporary files...")
    removed_count = 0

    # Clean directories
    cache_dirs = ["__pycache__", ".pytest_cache", ".coverage", "htmlcov", "dist", "build"]
    for path in REPO_ROOT.rglob("*"):
        if path.is_dir() and path.name in cache_dirs:
            shutil.rmtree(path, ignore_errors=True)
            removed_count += 1
        elif path.is_file() and path.suffix in [".pyc", ".pyo"]:
            path.unlink(missing_ok=True)
            removed_count += 1

    print(f"Clean complete. Removed {removed_count} cache directories/files.")
    return 0


def cmd_lab_reset(args: argparse.Namespace) -> int:
    """Reset working evidence directories and temporary laboratory state."""
    print("Resetting laboratory working state...")
    working_dirs = [
        REPO_ROOT / "data" / "evidence" / "working",
        REPO_ROOT / "data" / "evidence" / "derived",
        REPO_ROOT / "data" / "reports",
    ]
    cleaned = 0
    for directory in working_dirs:
        if directory.is_dir():
            for child in directory.iterdir():
                if child.name != ".gitkeep":
                    if child.is_dir():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
                    cleaned += 1
    print(f"Lab reset complete. Cleaned {cleaned} temporary artifacts.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dev.py",
        description="ForensiWeb Unified Developer CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # setup
    subparsers.add_parser("setup", help="Initialize .env and validate configuration")

    # validate-env
    val_p = subparsers.add_parser("validate-env", help="Validate environment configuration")
    val_p.add_argument("--check-example", action="store_true", help="Validate .env.example template")

    # test
    test_p = subparsers.add_parser("test", help="Execute automated test suite")
    test_p.add_argument("-m", "--marker", help="Run tests matching pytest marker (unit, integration, etc.)")
    test_p.add_argument("-k", "--keyword", help="Run tests matching keyword expression")
    test_p.add_argument("extra_args", nargs="*", help="Additional arguments forwarded to pytest")

    # hygiene
    subparsers.add_parser("hygiene", help="Verify Git ignore rules and secrets hygiene")

    # clean
    subparsers.add_parser("clean", help="Remove caches and temporary artifacts")

    # lab-reset
    subparsers.add_parser("lab-reset", help="Reset working evidence and laboratory state")

    return parser


def main() -> int:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()
    dispatch = {
        "setup": cmd_setup,
        "validate-env": cmd_validate_env,
        "test": cmd_test,
        "hygiene": cmd_hygiene,
        "clean": cmd_clean,
        "lab-reset": cmd_lab_reset,
    }

    handler = dispatch.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
