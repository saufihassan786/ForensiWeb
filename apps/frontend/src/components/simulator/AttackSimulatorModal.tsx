import React, { useEffect, useState } from "react";
import { Modal } from "@/components/common/Modal";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { apiService } from "@/services/api";
import { ScenarioRunResult, SimulationStatus, StageExecutionResult } from "@/types/api";
import {
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  Cpu,
  Flame,
  Globe,
  Play,
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  Terminal,
} from "lucide-react";

export interface AttackSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToTimeline?: () => void;
  onNavigateToReports?: () => void;
}

const DEFAULT_STAGES = [
  {
    id: "S1",
    name: "Local File Inclusion (LFI)",
    description: "Directory traversal probe targeting system and web files.",
    endpoint: "GET /document?file=../../../../etc/passwd",
    mitre: "T1083",
    severity: "medium",
  },
  {
    id: "S2",
    name: "Apache Log Poisoning",
    description: "Injection of PHP evaluation payload into HTTP User-Agent header.",
    endpoint: "GET /document?file=welcome.txt (with injected User-Agent)",
    mitre: "T1059.004",
    severity: "high",
  },
  {
    id: "S3",
    name: "RCE via Log Inclusion",
    description: "Inclusion of poisoned access.log triggering code execution.",
    endpoint: "GET /document?file=../../logs/access.log&cmd=whoami",
    mitre: "T1059.004",
    severity: "critical",
  },
  {
    id: "S4",
    name: "Web Shell Interaction",
    description: "Interactive arbitrary command execution via uploaded web shell.",
    endpoint: "POST /shell (cmd=id; uname -a)",
    mitre: "T1505.003",
    severity: "critical",
  },
  {
    id: "S5",
    name: "Privilege Escalation",
    description: "PATH environment manipulation to hijack binary execution to root.",
    endpoint: "POST /privesc/run-backup",
    mitre: "T1548.001",
    severity: "critical",
  },
];

export const AttackSimulatorModal: React.FC<AttackSimulatorModalProps> = ({
  isOpen,
  onClose,
  onNavigateToTimeline,
  onNavigateToReports,
}) => {
  const [labStatus, setLabStatus] = useState<SimulationStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [currentRunningStage, setCurrentRunningStage] = useState<string | null>(null);
  const [mitigationActive, setMitigationActive] = useState(false);
  const [runResult, setRunResult] = useState<ScenarioRunResult | null>(null);
  const [expandedStage, setExpandedStage] = useState<string | null>("S1");
  const [stageResults, setStageResults] = useState<Record<string, StageExecutionResult>>({});
  const [consoleLogs, setConsoleLogs] = useState<string[]>([
    "[SYSTEM] ForensiWeb Live Attack Simulator ready.",
    "[SYSTEM] Target container: http://127.0.0.1:5000 (Scenario WEB-CHAIN-001).",
  ]);

  useEffect(() => {
    if (isOpen) {
      refreshStatus();
    }
  }, [isOpen]);

  const refreshStatus = async () => {
    try {
      const status = await apiService.getSimulationStatus();
      setLabStatus(status);
      setMitigationActive(status.is_mitigated);
    } catch (_) {}
  };

  const addLog = (msg: string) => {
    setConsoleLogs((prev) => [...prev.slice(-40), `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const handleToggleMitigation = async () => {
    const nextState = !mitigationActive;
    try {
      addLog(`[DEFENSE] Requesting mitigation toggle to ${nextState ? "ACTIVE (Defensive Shield ON)" : "DISABLED (Vulnerable)"}...`);
      const res = await apiService.toggleSimulationMitigation(nextState);
      setMitigationActive(res.mitigation_active);
      addLog(`[DEFENSE] ${res.message}`);
      await refreshStatus();
    } catch (err: any) {
      addLog(`[ERROR] Failed to toggle mitigation: ${err.message}`);
    }
  };

  const handleResetLab = async () => {
    try {
      addLog("[LAB] Resetting laboratory state and clearing log files...");
      await apiService.resetSimulationLab();
      setRunResult(null);
      setStageResults({});
      addLog("[LAB] Target application baseline state successfully restored.");
      await refreshStatus();
    } catch (err: any) {
      addLog(`[ERROR] Reset failed: ${err.message}`);
    }
  };

  const handleRunSingleStage = async (stageId: string) => {
    try {
      setCurrentRunningStage(stageId);
      addLog(`[STAGE ${stageId}] Executing stage test against vulnerable target...`);
      const res = await apiService.runStageSimulation(stageId);
      setStageResults((prev) => ({ ...prev, [stageId]: res }));

      if (res.http_response.blocked) {
        addLog(`[STAGE ${stageId}] DEFENSE BLOCKED: HTTP ${res.http_response.status_code} Forbidden (Input policy rejected traversal).`);
      } else {
        addLog(`[STAGE ${stageId}] COMPROMISED: HTTP ${res.http_response.status_code} - Alert triggered: ${res.detection.rule_name} (${res.detection.mitre_id}).`);
      }
      setExpandedStage(stageId);
      await refreshStatus();
    } catch (err: any) {
      addLog(`[ERROR] Stage ${stageId} execution failed: ${err.message}`);
    } finally {
      setCurrentRunningStage(null);
    }
  };

  const handleRunFullScenario = async () => {
    setIsRunning(true);
    setRunResult(null);
    addLog(`=== STARTING FULL CYBER ATTACK SCENARIO (${mitigationActive ? "DEFENSIVE MITIGATION MODE" : "VULNERABLE BASELINE"}) ===`);

    try {
      const result = await apiService.runFullSimulation(mitigationActive);
      setRunResult(result);

      // Populate stage results
      const mappedStages: Record<string, StageExecutionResult> = {};
      result.stages.forEach((st) => {
        mappedStages[st.stage_id] = st;
      });
      setStageResults(mappedStages);

      result.stages.forEach((st) => {
        if (st.http_response.blocked) {
          addLog(`[${st.stage_id}] BLOCKED (HTTP ${st.http_response.status_code}): ${st.stage_name}`);
        } else {
          addLog(`[${st.stage_id}] EXECUTED (HTTP ${st.http_response.status_code}): ${st.stage_name} -> ${st.detection.severity.toUpperCase()} ALERT`);
        }
      });

      addLog(`[OUTCOME] Scenario Completed: ${result.overall_outcome} (${result.stages_blocked}/${result.stages_executed} stages blocked).`);
      addLog(`[SHA-256] Cryptographic audit receipt: ${result.cryptographic_receipt}`);
      await refreshStatus();
    } catch (err: any) {
      addLog(`[CRITICAL ERROR] Scenario run failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Interactive Cyber Attack Simulator & Defense Verification"
      description="Simulate the complete academic attack chain against the live target, observe real-time detection rule activations, and verify defense mitigation blocking."
      maxWidth="2xl"
    >
      <div className="space-y-5 text-sm">
        {/* Lab Target Control & Status Bar */}
        <div className="p-4 rounded-xl bg-surface-secondary border border-border-default flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-lg ${labStatus?.connected ? "bg-status-success/15 text-status-success" : "bg-status-critical/15 text-status-critical"}`}>
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-text-primary text-sm">Lab Target:</span>
                <span className="font-mono text-xs text-text-secondary">http://127.0.0.1:5000</span>
                <Badge variant={labStatus?.connected ? "verified" : "critical"} dot>
                  {labStatus?.connected ? "ONLINE" : "OFFLINE"}
                </Badge>
              </div>
              <p className="text-xs text-text-muted mt-0.5">
                Scenario WEB-CHAIN-001 • Telemetry: {labStatus?.access_log_lines || 0} access logs, {labStatus?.audit_log_lines || 0} audit records
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={mitigationActive ? "primary" : "secondary"}
              size="sm"
              onClick={handleToggleMitigation}
              className={`flex items-center gap-2 ${mitigationActive ? "border-status-success text-status-success" : ""}`}
            >
              {mitigationActive ? <ShieldCheck className="w-4 h-4 text-status-success" /> : <ShieldAlert className="w-4 h-4 text-status-high" />}
              <span>Shield: {mitigationActive ? "DEFENSE ACTIVE" : "VULNERABLE"}</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={handleResetLab} title="Reset Laboratory Logs">
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-gradient-to-r from-accent-blue/10 via-surface-primary to-accent-indigo/10 border border-border-default">
          <div>
            <h4 className="font-bold text-text-primary text-sm flex items-center gap-2">
              <Flame className="w-4 h-4 text-status-high" /> Complete 5-Stage Kill-Chain Execution
            </h4>
            <p className="text-xs text-text-muted mt-0.5">
              Automated execution of LFI → Log Poisoning → RCE → Web Shell → Privilege Escalation.
            </p>
          </div>

          <Button
            variant="primary"
            onClick={handleRunFullScenario}
            disabled={isRunning}
            className="flex items-center gap-2 px-5 py-2.5 bg-accent-blue hover:bg-accent-blue-light text-white font-semibold shadow-glow-blue transition-all"
          >
            {isRunning ? (
              <>
                <Cpu className="w-4 h-4 animate-spin" />
                <span>Simulating Attack Chain...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Run Full Attack Scenario</span>
              </>
            )}
          </Button>
        </div>

        {/* Outcome Card when Full Scenario Completed */}
        {runResult && (
          <div
            className={`p-4 rounded-xl border animate-fade-in ${
              runResult.overall_outcome === "BLOCKED"
                ? "bg-status-success/10 border-status-success/40 text-text-primary"
                : "bg-status-critical/10 border-status-critical/40 text-text-primary"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                {runResult.overall_outcome === "BLOCKED" ? (
                  <ShieldCheck className="w-6 h-6 text-status-success shrink-0 mt-0.5" />
                ) : (
                  <AlertOctagon className="w-6 h-6 text-status-critical shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base">
                      {runResult.overall_outcome === "BLOCKED" ? "DEFENSES EFFECTIVE (ATTACK BLOCKED)" : "SYSTEM COMPROMISED (FULL CHAIN EXECUTED)"}
                    </span>
                    <Badge variant={runResult.overall_outcome === "BLOCKED" ? "verified" : "critical"}>
                      {runResult.stages_blocked}/{runResult.stages_executed} Stages Blocked
                    </Badge>
                  </div>
                  <p className="text-xs mt-1 text-text-secondary">{runResult.summary}</p>
                  <p className="text-[11px] font-mono text-text-muted mt-2">
                    SHA-256 Verification Receipt: <span className="text-accent-cyan">{runResult.cryptographic_receipt}</span>
                  </p>
                </div>
              </div>

              <div className="flex flex-col gap-2 shrink-0">
                {onNavigateToTimeline && (
                  <Button variant="secondary" size="sm" onClick={() => { onClose(); onNavigateToTimeline(); }}>
                    View in Timeline
                  </Button>
                )}
                {onNavigateToReports && (
                  <Button variant="secondary" size="sm" onClick={() => { onClose(); onNavigateToReports(); }}>
                    Generate Report
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Interactive Attack Stages List */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-text-muted px-1">
            <span>ATTACK CHAIN STAGES (INTERACTIVE DRILLDOWN)</span>
            <span>CLICK TO TEST INDIVIDUALLY</span>
          </div>

          {DEFAULT_STAGES.map((stage) => {
            const isExpanded = expandedStage === stage.id;
            const res = stageResults[stage.id];
            const isStageExecuting = currentRunningStage === stage.id;

            return (
              <div
                key={stage.id}
                className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                  isExpanded ? "border-accent-blue/50 bg-surface-primary" : "border-border-default bg-surface-primary hover:border-border-active"
                }`}
              >
                {/* Header Row */}
                <div
                  className="p-3.5 flex items-center justify-between gap-3 cursor-pointer select-none"
                  onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-8 h-8 rounded-lg bg-surface-secondary border border-border-default flex items-center justify-center font-mono font-bold text-xs text-accent-blue">
                      {stage.id}
                    </span>
                    <div className="truncate">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-text-primary text-xs">{stage.name}</span>
                        <Badge variant="informational" className="text-[10px]">
                          MITRE {stage.mitre}
                        </Badge>
                        {res && (
                          <Badge variant={res.http_response.blocked ? "verified" : "critical"} className="text-[10px]">
                            {res.http_response.blocked ? "BLOCKED 403" : `HTTP ${res.http_response.status_code}`}
                          </Badge>
                        )}
                      </div>
                      <p className="text-[11px] text-text-muted truncate mt-0.5">{stage.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={isStageExecuting || isRunning}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRunSingleStage(stage.id);
                      }}
                      className="text-xs flex items-center gap-1.5"
                    >
                      {isStageExecuting ? <Cpu className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3 fill-current text-accent-blue" />}
                      <span>Execute</span>
                    </Button>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-text-muted" /> : <ChevronDown className="w-4 h-4 text-text-muted" />}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 border-t border-border-default/60 bg-surface-secondary/40 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                      <div>
                        <span className="text-[10px] font-mono text-text-muted uppercase">Target Interaction:</span>
                        <p className="text-xs font-mono bg-bg-primary p-2 rounded border border-border-default text-text-secondary mt-1 break-all">
                          {stage.endpoint}
                        </p>
                      </div>

                      <div>
                        <span className="text-[10px] font-mono text-text-muted uppercase">Forensic Attribution:</span>
                        <div className="mt-1 flex items-center gap-2 text-xs">
                          <Badge variant={stage.severity === "critical" ? "critical" : stage.severity === "high" ? "high" : "medium"}>
                            {stage.severity.toUpperCase()} SEVERITY
                          </Badge>
                          <span className="text-text-muted">• MITRE ATT&CK {stage.mitre}</span>
                        </div>
                      </div>
                    </div>

                    {res && (
                      <div className="p-3 rounded-lg bg-bg-primary border border-border-default space-y-2 animate-fade-in">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-text-primary flex items-center gap-1.5">
                            {res.http_response.blocked ? (
                              <ShieldCheck className="w-4 h-4 text-status-success" />
                            ) : (
                              <ShieldAlert className="w-4 h-4 text-status-critical" />
                            )}
                            {res.detection.rule_name}
                          </span>
                          <span className="font-mono text-[11px] text-text-muted">Status: HTTP {res.http_response.status_code}</span>
                        </div>

                        <p className="text-xs text-text-secondary">{res.detection.explanation}</p>

                        <div className="p-2 rounded bg-surface-primary border border-border-default text-xs">
                          <span className="font-semibold text-accent-cyan">Recommended Mitigation: </span>
                          <span className="text-text-muted">{res.remediation}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Live Simulator Console Output */}
        <div className="rounded-xl border border-border-default bg-bg-primary overflow-hidden">
          <div className="px-3.5 py-2 bg-surface-secondary border-b border-border-default flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 font-mono text-text-muted">
              <Terminal className="w-3.5 h-3.5 text-accent-cyan" />
              <span>LIVE TELEMETRY STREAM</span>
            </div>
            <button
              onClick={() => setConsoleLogs(["[SYSTEM] Log output cleared."])}
              className="text-[10px] text-text-muted hover:text-text-primary transition-colors font-mono"
            >
              Clear Console
            </button>
          </div>
          <div className="p-3 font-mono text-xs text-text-muted max-h-40 overflow-y-auto space-y-1">
            {consoleLogs.map((log, i) => (
              <div
                key={i}
                className={
                  log.includes("COMPROMISED") || log.includes("CRITICAL")
                    ? "text-status-critical"
                    : log.includes("BLOCKED") || log.includes("DEFENSE")
                    ? "text-status-success"
                    : log.includes("STARTING") || log.includes("OUTCOME")
                    ? "text-accent-cyan font-bold"
                    : "text-text-secondary"
                }
              >
                {log}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Modal>
  );
};
