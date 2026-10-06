"""
ForensiWeb Test Fixtures.

Provides utility functions to access synthetic evidence artifacts and mock data
for forensic parsing, normalization, detection, and integration testing.
"""

from pathlib import Path
from typing import Dict

FIXTURES_DIR = Path(__file__).resolve().parent


def get_fixture_path(filename: str) -> Path:
    """Return the absolute path to a fixture file."""
    path = FIXTURES_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Fixture not found: {filename} in {FIXTURES_DIR}")
    return path


def load_fixture_text(filename: str) -> str:
    """Read and return the text content of a fixture file."""
    return get_fixture_path(filename).read_text(encoding="utf-8")


def load_fixture_bytes(filename: str) -> bytes:
    """Read and return the binary content of a fixture file."""
    return get_fixture_path(filename).read_bytes()
