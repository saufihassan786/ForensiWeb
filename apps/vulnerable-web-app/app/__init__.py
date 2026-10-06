"""ForensiWeb Controlled Vulnerable Application Package."""

from __future__ import annotations

try:
    from app.main import create_app
    from app.config import LabConfig
    from app.logger import LabLogger
except (ImportError, AttributeError):
    try:
        from vuln_app.main import create_app
        from vuln_app.config import LabConfig
        from vuln_app.logger import LabLogger
    except (ImportError, AttributeError):
        from .main import create_app
        from .config import LabConfig
        from .logger import LabLogger

__all__ = ["create_app", "LabConfig", "LabLogger"]
