"""Controlled Scenario Detection Rules (PHASE-09-F04, F05, F06).

Defines deterministic, explainable rules for each stage of the ForensiWeb
academic attack chain: LFI -> Log Poisoning -> RCE -> Web Shell -> PATH Hijack -> PrivEsc.
"""

from __future__ import annotations

import abc
import uuid
from typing import Any, Dict, List, Optional

from models.rule import DetectionAlert, DetectionRuleDefinition
from normalization.schema import AttackStage, CommonEventModel, SeverityLevel


class BaseDetectionRule(abc.ABC):
    """Abstract base detection rule interface."""

    @property
    @abc.abstractmethod
    def definition(self) -> DetectionRuleDefinition:
        """Rule metadata specification."""
        raise NotImplementedError

    @abc.abstractmethod
    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        """Evaluate event; return DetectionAlert if triggered, else None."""
        raise NotImplementedError

    def create_alert(
        self,
        event: CommonEventModel,
        explanation: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectionAlert:
        """Helper to instantiate a standardized, evidence-linked DetectionAlert."""
        evidence_link = f"{event.evidence_ref.artifact_name}#{event.evidence_ref.sha256[:12]}"
        return DetectionAlert(
            detection_id=f"DET-{uuid.uuid4().hex[:8].upper()}",
            case_id=event.case_id,
            rule_id=self.definition.rule_id,
            rule_name=self.definition.name,
            description=self.definition.description,
            severity=self.definition.severity,
            attack_stage=self.definition.attack_stage,
            explanation=explanation,
            matched_event_ids=[event.event_id],
            evidence_references=[evidence_link],
            context=context or {},
        )


class RuleLfiTraversal(BaseDetectionRule):
    """Detects path traversal sequences targeting sensitive filesystem paths."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-01-LFI",
        name="Path Traversal / Local File Inclusion Probe",
        description="Identifies directory traversal patterns (e.g., ../, /etc/passwd) in web and application logs.",
        severity="high",
        attack_stage="stage_01_lfi",
        input_source_types=["web_access_log", "app_log"],
        explanation_template="Directory traversal detected in request path '{path}' originating from actor {actor_ip}.",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        raw = event.raw_content.lower()
        path = event.target.get("path") or event.target.get("message") or ""
        actor_ip = event.actor.get("ip") or "unknown"

        is_lfi_stage = event.attack_stage == AttackStage.STAGE_01_LFI
        has_traversal_pattern = ".." in str(path) or "etc/passwd" in raw or "path_traversal" in event.action

        if is_lfi_stage or has_traversal_pattern:
            explanation = self.definition.format_explanation(path=path or raw[:60], actor_ip=actor_ip)
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"path": path, "actor_ip": actor_ip},
            )
        return None


class RuleLogPoisoning(BaseDetectionRule):
    """Detects server log poisoning code injection payloads."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-02-LOG-POISONING",
        name="Web Server Log Poisoning Injection",
        description="Identifies executable script tags or simulated payloads embedded in User-Agent or HTTP headers.",
        severity="high",
        attack_stage="stage_02_log_poisoning",
        input_source_types=["web_access_log", "app_log"],
        explanation_template="Executable code injection payload identified in client User-Agent: '{payload}' from {actor_ip}.",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        ua = event.actor.get("user_agent") or ""
        actor_ip = event.actor.get("ip") or "unknown"
        is_poison_stage = event.attack_stage == AttackStage.STAGE_02_LOG_POISONING
        has_poison_payload = (
            "<?php" in ua or "system(" in ua or "poison" in ua.lower() or "log_poisoning" in event.action
        )

        if is_poison_stage or has_poison_payload:
            explanation = self.definition.format_explanation(
                payload=ua[:80] or "detected payload", actor_ip=actor_ip
            )
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"user_agent": ua, "actor_ip": actor_ip},
            )
        return None


class RuleRceLogExecution(BaseDetectionRule):
    """Detects execution of poisoned logs via LFI inclusion."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-03-RCE",
        name="Remote Code Execution via Log Inclusion",
        description="Identifies inclusion of web access log files coupled with command execution parameters.",
        severity="critical",
        attack_stage="stage_03_rce",
        input_source_types=["web_access_log", "app_log", "system_audit"],
        explanation_template="Poisoned log file inclusion with command execution detected: '{resource}' with command parameter '{cmd}'.",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        raw = event.raw_content
        qparams = event.target.get("query_params", {})
        has_cmd = "cmd" in qparams or "cmd=" in raw
        has_log_inclusion = "access.log" in raw or "access" in str(event.target.get("path", ""))

        if (event.attack_stage == AttackStage.STAGE_03_RCE) or (has_log_inclusion and has_cmd):
            cmd_val = qparams.get("cmd", "cmd_exec")
            explanation = self.definition.format_explanation(
                resource="access.log", cmd=cmd_val
            )
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"query_params": qparams, "cmd": cmd_val},
            )
        return None


class RuleWebShellInteraction(BaseDetectionRule):
    """Detects interactive web shell interaction commands."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-04-WEBSHELL",
        name="Interactive Web Shell Command Execution",
        description="Identifies administrative and reconnaissance commands executed via HTTP shell interfaces.",
        severity="critical",
        attack_stage="stage_04_web_shell",
        input_source_types=["web_access_log", "system_audit"],
        explanation_template="Web shell command interaction observed: command '{cmd}' executed via web service.",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        qparams = event.target.get("query_params", {})
        cmd = qparams.get("cmd", "")
        comm = event.actor.get("comm", "")

        is_webshell_stage = event.attack_stage == AttackStage.STAGE_04_WEB_SHELL
        has_shell_cmd = cmd in ("id", "whoami", "uname", "cat /etc/passwd") or comm in ("sh", "bash")

        if is_webshell_stage or (cmd and has_shell_cmd):
            explanation = self.definition.format_explanation(cmd=cmd or comm)
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"command": cmd or comm},
            )
        return None


class RuleEnvPathManipulation(BaseDetectionRule):
    """Detects insecure PATH environment variable manipulation."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-05-PATH-HIJACK",
        name="Insecure Environment Variable PATH Hijacking",
        description="Identifies environment modifications where writable directories (e.g. /tmp/bin) precede system PATH.",
        severity="high",
        attack_stage="stage_05_env_manipulation",
        input_source_types=["env_dump"],
        explanation_template="Insecure PATH configuration detected: writable directory '{writable_dir}' placed ahead of system binaries in PATH '{path}'.",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        env_vars = event.target.get("variables", {})
        path_val = env_vars.get("PATH", "")

        is_env_stage = event.attack_stage == AttackStage.STAGE_05_ENV_MANIPULATION
        has_path_hijack = "/tmp" in path_val and (path_val.startswith("/tmp") or ":/tmp" in path_val)

        if is_env_stage or has_path_hijack:
            explanation = self.definition.format_explanation(
                writable_dir="/tmp/bin", path=path_val
            )
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"PATH": path_val},
            )
        return None


class RulePrivilegeEscalation(BaseDetectionRule):
    """Detects execution of hijacked binaries resulting in privilege escalation."""

    _DEF = DetectionRuleDefinition(
        rule_id="RULE-06-PRIV-ESC",
        name="Privilege Escalation via Binary Execution",
        description="Identifies execution of malicious binaries from temporary directories or unauthorized SUID invocation.",
        severity="critical",
        attack_stage="stage_06_priv_esc",
        input_source_types=["system_audit"],
        explanation_template="Privilege escalation binary execution detected: binary '{binary}' executed by process '{comm}' (PID {pid}).",
    )

    @property
    def definition(self) -> DetectionRuleDefinition:
        return self._DEF

    def evaluate(self, event: CommonEventModel) -> Optional[DetectionAlert]:
        exe = event.target.get("exe") or ""
        target_name = event.target.get("target_name") or ""
        comm = event.actor.get("comm") or ""
        pid = event.actor.get("pid") or 0

        is_privesc_stage = event.attack_stage == AttackStage.STAGE_06_PRIV_ESC
        has_hijacked_bin = "/tmp/bin/su" in target_name or "/tmp/bin" in exe

        if is_privesc_stage or has_hijacked_bin:
            explanation = self.definition.format_explanation(
                binary=target_name or exe or "su",
                comm=comm or "process",
                pid=pid,
            )
            return self.create_alert(
                event=event,
                explanation=explanation,
                context={"binary": target_name or exe, "comm": comm, "pid": pid},
            )
        return None
