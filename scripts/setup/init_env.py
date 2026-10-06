#!/usr/bin/env python3
"""
ForensiWeb Environment Initializer.

Safely initializes a local `.env` file from `.env.example` if it does not already exist.
Ensures developers have a valid starting configuration without exposing secrets.
"""

from __future__ import annotations
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_EXAMPLE = REPO_ROOT / ".env.example"
ENV_TARGET = REPO_ROOT / ".env"


def init_environment(force: bool = False) -> bool:
    """Initialize local .env from .env.example."""
    if not ENV_EXAMPLE.is_file():
        print(f"Error: Template file not found: {ENV_EXAMPLE}", file=sys.stderr)
        return False

    if ENV_TARGET.is_file() and not force:
        print(f"Notice: .env already exists at {ENV_TARGET}. Skipping copy (use --force to overwrite).")
        return True

    try:
        shutil.copyfile(ENV_EXAMPLE, ENV_TARGET)
        print(f"SUCCESS: Created local .env from {ENV_EXAMPLE.name}")
        return True
    except OSError as err:
        print(f"Error creating .env: {err}", file=sys.stderr)
        return False


def main() -> int:
    force = "--force" in sys.argv
    success = init_environment(force=force)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
