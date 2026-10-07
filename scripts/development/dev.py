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


def _get_api_env() -> dict:
    import os
    env = os.environ.copy()
    py_paths = [
        str(REPO_ROOT),
        str(REPO_ROOT / "apps" / "api"),
        str(REPO_ROOT / "packages" / "detection-engine"),
        str(REPO_ROOT / "packages" / "forensic-engine"),
        str(REPO_ROOT / "packages" / "report-engine"),
    ]
    env["PYTHONPATH"] = os.pathsep.join(py_paths)
    return env


def cmd_start_lab(args: argparse.Namespace) -> int:
    """Start the vulnerable web target on port 5000."""
    print("Starting Vulnerable Lab Target on http://127.0.0.1:5000 ...")
    return subprocess.run(
        [sys.executable, "-m", "app.main"],
        cwd=str(REPO_ROOT / "apps" / "vulnerable-web-app"),
    ).returncode


def cmd_start_api(args: argparse.Namespace) -> int:
    """Start the FastAPI backend on port 8000."""
    print("Starting ForensiWeb Backend API on http://127.0.0.1:8000 ...")
    return subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(REPO_ROOT),
        env=_get_api_env(),
    ).returncode


def cmd_start_frontend(args: argparse.Namespace) -> int:
    """Start the React Vite frontend on port 5173."""
    print("Starting ForensiWeb Frontend UI on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    return subprocess.run(
        [npm_cmd, "run", "dev"],
        cwd=str(REPO_ROOT / "apps" / "frontend"),
    ).returncode


def cmd_start_all(args: argparse.Namespace) -> int:
    """Start all three local servers concurrently (Lab Target, Backend API, Frontend)."""
    import time
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    processes = []
    try:
        print("[1/3] Starting Vulnerable Lab Target on http://127.0.0.1:5000 ...")
        proc_lab = subprocess.Popen(
            [sys.executable, "-m", "app.main"],
            cwd=str(REPO_ROOT / "apps" / "vulnerable-web-app"),
        )
        processes.append(("Lab Target", proc_lab))

        print("[2/3] Starting ForensiWeb Backend API on http://127.0.0.1:8000 ...")
        proc_api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(REPO_ROOT),
            env=_get_api_env(),
        )
        processes.append(("Backend API", proc_api))

        print("[3/3] Starting ForensiWeb Frontend UI on http://localhost:5173 ...")
        proc_fe = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(REPO_ROOT / "apps" / "frontend"),
        )
        processes.append(("Frontend UI", proc_fe))

        print("\n=== ForensiWeb Services Active ===")
        print("  - Lab Target:  http://127.0.0.1:5000")
        print("  - Backend API: http://127.0.0.1:8000 (OpenAPI Docs: /docs)")
        print("  - Frontend UI: http://localhost:5173")
        print("\nPress Ctrl+C to terminate all services.\n")

        while True:
            for name, p in processes:
                code = p.poll()
                if code is not None:
                    print(f"Service '{name}' exited with code {code}.")
                    return code
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nGracefully stopping ForensiWeb services...")
        for name, p in processes:
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        print("All services stopped.")
        return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    """Execute the end-to-end forensic investigation pipeline."""
    script = REPO_ROOT / "scripts" / "testing" / "run_e2e_pipeline.py"
    return subprocess.run([sys.executable, str(script)]).returncode


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

    # start-all
    subparsers.add_parser("start-all", help="Start all local services (Lab on 5000, API on 8000, Frontend on 5173)")

    # start-lab
    subparsers.add_parser("start-lab", help="Start vulnerable target web application (port 5000)")

    # start-api
    subparsers.add_parser("start-api", help="Start FastAPI backend application (port 8000)")

    # start-frontend
    subparsers.add_parser("start-frontend", help="Start React Vite frontend application (port 5173)")

    # pipeline
    subparsers.add_parser("pipeline", help="Run end-to-end forensic investigation scenario and report generation")

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
        "start-all": cmd_start_all,
        "start-lab": cmd_start_lab,
        "start-api": cmd_start_api,
        "start-frontend": cmd_start_frontend,
        "pipeline": cmd_pipeline,
    }

    handler = dispatch.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
