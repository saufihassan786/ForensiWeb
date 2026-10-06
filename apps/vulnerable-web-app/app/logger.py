"""Forensic Telemetry Generator & Logger for Lab Environment."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from app.config import LabConfig
except (ImportError, AttributeError):
    try:
        from vuln_app.config import LabConfig
    except (ImportError, AttributeError):
        from .config import LabConfig


class LabLogger:
    """Writes realistic Apache web logs and Linux auditd log telemetry for forensic analysis."""

    def __init__(self, config: LabConfig) -> None:
        self.config = config
        self._audit_seq = 100

    def log_apache_request(
        self,
        ip: str,
        method: str,
        path: str,
        status: int,
        bytes_sent: int,
        user_agent: str,
        referer: str = "-",
    ) -> str:
        """Append an Apache Combined Log entry."""
        # e.g. [06/Oct/2026:10:31:22 +0000]
        now_dt = datetime.now(timezone.utc)
        ts_str = now_dt.strftime("%d/%b/%Y:%H:%M:%S +0000")
        line = f'{ip} - - [{ts_str}] "{method} {path} HTTP/1.1" {status} {bytes_sent} "{referer}" "{user_agent}"\n'
        with open(self.config.access_log_path, "a", encoding="utf-8") as f:
            f.write(line)
        return line

    def log_auditd_execve(
        self,
        comm: str,
        args: list[str],
        uid: int = 1000,
        euid: int = 1000,
        pid: int = 2450,
        ppid: int = 2400,
    ) -> str:
        """Append Linux auditd EXECVE record sequence."""
        self._audit_seq += 1
        epoch_ts = f"{time.time():.3f}"
        msg_id = f"msg=audit({epoch_ts}:{self._audit_seq})"

        lines = [
            f'type=SYSCALL {msg_id}: arch=c000003e syscall=59 success=yes exit=0 items=2 ppid={ppid} pid={pid} auid=1000 uid={uid} gid={uid} euid={euid} suid={euid} ses=1 comm="{comm}" exe="/bin/{comm}"\n',
            f'type=EXECVE {msg_id}: argc={len(args)} ' + " ".join([f'a{i}="{arg}"' for i, arg in enumerate(args)]) + "\n",
            f'type=PROCTITLE {msg_id}: proctitle=666F72656E736963\n',
        ]
        text_block = "".join(lines)
        with open(self.config.audit_log_path, "a", encoding="utf-8") as f:
            f.write(text_block)
        return text_block

    def clear_logs(self) -> None:
        """Reset all log files to empty baseline."""
        for p in [self.config.access_log_path, self.config.audit_log_path, self.config.error_log_path]:
            if p.exists():
                p.write_text("", encoding="utf-8")
