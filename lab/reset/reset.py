"""ForensiWeb — Lab Reset Module.

Re-exports LabResetManager from lab.scripts.reset_lab.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lab.scripts.reset_lab import LabResetManager

__all__ = ["LabResetManager"]
