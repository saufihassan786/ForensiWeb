"""Controlled Vulnerable Web Application (PHASE-04).

Simulates the complete academic attack chain:
- S1: LFI (Path Traversal in /document?file=...)
- S2: Log Poisoning (Attacker-controlled User-Agent recorded in access.log)
- S3: RCE (Inclusion of poisoned access.log triggering execution)
- S4: Web Shell (Persistent execution via /shell?cmd=...)
- S5: Privilege Escalation (PATH environment variable misconfiguration simulation)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request, Response

try:
    from app.config import LabConfig
    from app.logger import LabLogger
except (ImportError, AttributeError):
    try:
        from vuln_app.config import LabConfig
        from vuln_app.logger import LabLogger
    except (ImportError, AttributeError):
        from .config import LabConfig
        from .logger import LabLogger


def create_app(config: Optional[LabConfig] = None) -> Flask:
    """Application factory for the controlled vulnerable target application."""
    app = Flask(__name__)
    lab_cfg = config or LabConfig()
    lab_logger = LabLogger(lab_cfg)

    app.config["LAB_CONFIG"] = lab_cfg
    app.config["LAB_LOGGER"] = lab_logger

    @app.after_request
    def record_access_log(response: Response) -> Response:
        """Record every HTTP interaction to access.log in Apache Combined format."""
        # Avoid self-logging of internal lab control/management endpoints
        if request.path.startswith("/api/"):
            return response

        client_ip = request.remote_addr or "127.0.0.1"
        user_agent = request.headers.get("User-Agent", "-")
        referer = request.headers.get("Referer", "-")
        method = request.method
        full_path = request.full_path if request.query_string else request.path

        lab_logger.log_apache_request(
            ip=client_ip,
            method=method,
            path=full_path,
            status=response.status_code,
            bytes_sent=response.content_length or 0,
            user_agent=user_agent,
            referer=referer,
        )
        return response

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "ForensiWeb Controlled Vulnerable Application",
            "scenario": "WEB-CHAIN-001 (LFI-to-PrivEsc)",
            "status": "ready",
            "stages": [
                {"id": "S1", "name": "LFI Probing", "endpoint": "GET /document?file=welcome.txt"},
                {"id": "S2", "name": "Log Poisoning", "description": "Inject token into User-Agent"},
                {"id": "S3", "name": "RCE Execution", "endpoint": "GET /document?file=../../logs/access.log&cmd=id"},
                {"id": "S4", "name": "Web Shell", "endpoint": "GET /shell?cmd=whoami"},
                {"id": "S4b", "name": "Meterpreter Probe", "endpoint": "POST /post-exploitation/meterpreter"},
                {"id": "S5", "name": "Privilege Escalation", "endpoint": "POST /privesc/run-backup"},
            ],
            "controls": {
                "reset": "POST /api/reset",
                "status": "GET /api/status",
                "view_access_log": "GET /api/logs/access",
                "view_audit_log": "GET /api/logs/audit",
                "mitigation_enable": "POST /api/mitigation/enable",
                "mitigation_disable": "POST /api/mitigation/disable",
                "mitigation_status": "GET /api/mitigation/status",
            },
        })

    def is_mitigation_active() -> bool:
        return lab_cfg.is_mitigated or request.headers.get("X-Lab-Mitigation", "").lower() in ("true", "1")

    @app.route("/document", methods=["GET"])
    def document():
        """Stage S1 (LFI) and Stage S3 (Log Poisoning RCE)."""
        file_param = request.args.get("file", "welcome.txt")
        cmd_param = request.args.get("cmd")

        # Check if security mitigations are enabled (PHASE-15)
        if is_mitigation_active():
            if "../" in file_param or "..\\" in file_param or "access.log" in file_param or "/" in file_param or "\\" in file_param:
                return Response(
                    "[SECURITY_MITIGATION_ACTIVE] Directory traversal and log inclusion blocked by input whitelist policy.\n",
                    status=403,
                    mimetype="text/plain",
                )

        # 1. Check for Log Poisoning RCE Trigger (Stage S3)
        if "access.log" in file_param and cmd_param:
            # Attacker includes poisoned access.log with execution parameter
            lab_logger.log_auditd_execve(
                comm="sh",
                args=["sh", "-c", cmd_param],
                uid=1000,
                euid=1000,
            )
            simulated_output = {
                "whoami": "labuser\n",
                "id": "uid=1000(labuser) gid=1000(labuser) groups=1000(labuser)\n",
                "uname -a": "Linux forensiweb-target 6.1.0-generic x86_64 GNU/Linux\n",
            }.get(cmd_param, f"simulated_output_of_{cmd_param}\n")
            return Response(
                f"[LOG_INCLUSION_EXECUTION]\n{simulated_output}",
                mimetype="text/plain",
            )

        # 2. Check for traversal targeting access.log (Stage S1 reconnaissance)
        if "access.log" in file_param:
            if lab_cfg.access_log_path.exists():
                content = lab_cfg.access_log_path.read_text(encoding="utf-8")
                return Response(content, mimetype="text/plain")
            return Response("access.log is empty\n", mimetype="text/plain")

        # 3. Legitimate document request
        clean_name = os.path.basename(file_param)
        doc_path = lab_cfg.docs_dir / clean_name
        if doc_path.exists() and doc_path.is_file():
            return Response(doc_path.read_text(encoding="utf-8"), mimetype="text/plain")

        # 4. Traversal boundary guard: containment enforced
        if "../" in file_param or "..\\" in file_param:
            return Response(
                f"[CONTAINMENT_GUARD] Traversal pattern recognized ({file_param}). Target file not found in simulated lab scope.\n",
                status=404,
                mimetype="text/plain",
            )

        return Response(f"Document '{file_param}' not found.\n", status=404, mimetype="text/plain")

    @app.route("/shell", methods=["GET", "POST"])
    def web_shell():
        """Stage S4: Controlled Web Shell Interaction."""
        if is_mitigation_active():
            return jsonify({
                "status": "blocked",
                "stage": "WEB_SHELL",
                "message": "[SECURITY_MITIGATION_ACTIVE] Web shell access disabled by security policy.",
            }), 403

        cmd = request.args.get("cmd") or request.form.get("cmd", "id")

        lab_logger.log_auditd_execve(
            comm="sh",
            args=["sh", "-c", cmd],
            uid=1000,
            euid=1000,
        )
        simulated_res = {
            "whoami": "labuser",
            "id": "uid=1000(labuser) gid=1000(labuser) groups=1000(labuser)",
            "pwd": "/var/www/html",
            "ls -la": "total 12\ndrwxr-xr-x 2 labuser labuser 4096 Oct  6 12:00 .\ndrwxr-xr-x 3 root    root    4096 Oct  6 10:00 ..\n-rw-r--r-- 1 labuser labuser   42 Oct  6 12:00 shell.php",
        }.get(cmd, f"Executed: {cmd}")

        return jsonify({
            "status": "executed",
            "command": cmd,
            "output": simulated_res,
            "stage": "WEB_SHELL",
            "user": "labuser",
        })

    @app.route("/post-exploitation/meterpreter", methods=["GET", "POST"])
    def meterpreter_probe():
        """Stage S4b / Post-Exploitation: Controlled Meterpreter Telemetry Simulation."""
        if is_mitigation_active():
            return jsonify({
                "status": "blocked",
                "stage": "METERPRETER_POST_EXPLOITATION",
                "message": "[SECURITY_MITIGATION_ACTIVE] Unauthorized beacon blocked by network egress policy.",
            }), 403

        lhost = request.args.get("lhost") or "10.0.50.5"
        lport = request.args.get("lport") or "4444"
        session_id = request.args.get("session_id", "sess-01")

        lab_logger.log_auditd_execve(
            comm="meterpreter_mock",
            args=["/tmp/.svc_host", "--stage2", f"--lhost={lhost}", f"--lport={lport}"],
            uid=1000,
            euid=1000,
        )

        return jsonify({
            "status": "established",
            "stage": "METERPRETER_POST_EXPLOITATION",
            "session_id": session_id,
            "transport": "reverse_tcp",
            "lhost": lhost,
            "lport": lport,
            "process": "/tmp/.svc_host",
            "user": "labuser",
            "message": "Simulated meterpreter post-exploitation session beacon logged to auditd.",
        })

    @app.route("/privesc/run-backup", methods=["POST"])
    def privesc_backup():
        """Stage S5: Controlled PATH Misconfiguration Execution."""
        if is_mitigation_active():
            # In mitigated state, PATH is strictly hardcoded to trusted bin dirs
            # and executed as unprivileged labuser without elevation
            return jsonify({
                "status": "mitigated",
                "stage": "PRIVILEGE_ESCALATION",
                "effective_uid": 1000,
                "effective_user": "labuser",
                "path_used": "/usr/bin:/bin",
                "message": "[SECURITY_MITIGATION_ACTIVE] Executed with sanitized system PATH; elevation prevented.",
            })

        hijacked_path = request.headers.get("X-Lab-PATH", "/tmp/bin:/usr/local/bin:/usr/bin:/bin")

        # Auditd records elevated execution with root privileges (uid=0, euid=0)
        lab_logger.log_auditd_execve(
            comm="backup_tool",
            args=["/tmp/bin/backup_tool", "--full"],
            uid=0,
            euid=0,
        )

        return jsonify({
            "status": "completed",
            "stage": "PRIVILEGE_ESCALATION",
            "effective_uid": 0,
            "effective_user": "root",
            "path_used": hijacked_path,
            "message": "Elevated backup task executed with hijacked PATH binary.",
        })

    @app.route("/api/mitigation/enable", methods=["POST"])
    def enable_mitigation():
        """Enable secure mitigation mode."""
        lab_cfg.is_mitigated = True
        return jsonify({"status": "enabled", "is_mitigated": True, "message": "Security mitigations active."})

    @app.route("/api/mitigation/disable", methods=["POST"])
    def disable_mitigation():
        """Disable secure mitigation mode."""
        lab_cfg.is_mitigated = False
        return jsonify({"status": "disabled", "is_mitigated": False, "message": "Security mitigations inactive."})

    @app.route("/api/mitigation/status", methods=["GET"])
    def mitigation_status():
        """Check status of security mitigations."""
        return jsonify({
            "is_mitigated": lab_cfg.is_mitigated,
            "active_controls": [
                "path_whitelist_validation",
                "web_shell_disabled",
                "egress_beacon_blocked",
                "sanitized_script_path",
            ] if lab_cfg.is_mitigated else [],
        })

    @app.route("/api/reset", methods=["POST"])
    def reset_scenario():
        """Reset scenario state and clear all generated logs."""
        lab_logger.clear_logs()
        return jsonify({"status": "reset", "message": "Laboratory logs cleared and baseline restored."})

    @app.route("/api/status", methods=["GET"])
    def status():
        """Report current log counts and scenario status."""
        access_lines = 0
        if lab_cfg.access_log_path.exists():
            access_lines = len(lab_cfg.access_log_path.read_text(encoding="utf-8").splitlines())

        audit_lines = 0
        if lab_cfg.audit_log_path.exists():
            audit_lines = len(lab_cfg.audit_log_path.read_text(encoding="utf-8").splitlines())

        return jsonify({
            "scenario": "WEB-CHAIN-001",
            "is_mitigated": lab_cfg.is_mitigated,
            "access_log_lines": access_lines,
            "audit_log_lines": audit_lines,
            "is_poisoned": "SIMULATED_POISON_PAYLOAD" in (
                lab_cfg.access_log_path.read_text(encoding="utf-8")
                if lab_cfg.access_log_path.exists()
                else ""
            ),
        })

    @app.route("/api/logs/access", methods=["GET"])
    def view_access_log():
        content = (
            lab_cfg.access_log_path.read_text(encoding="utf-8")
            if lab_cfg.access_log_path.exists()
            else ""
        )
        return Response(content, mimetype="text/plain")

    @app.route("/api/logs/audit", methods=["GET"])
    def view_audit_log():
        content = (
            lab_cfg.audit_log_path.read_text(encoding="utf-8")
            if lab_cfg.audit_log_path.exists()
            else ""
        )
        return Response(content, mimetype="text/plain")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
