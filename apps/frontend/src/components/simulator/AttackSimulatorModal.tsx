import React, { useEffect, useRef, useState } from "react";
import { Modal } from "@/components/common/Modal";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { apiService } from "@/services/api";
import { SimulationStatus, StageExecutionResult } from "@/types/api";
import {
  ChevronDown,
  ChevronUp,
  Cpu,
  Flame,
  Play,
  RotateCcw,
  ShieldCheck,
  ShieldOff,
  Square,
  Zap,
} from "lucide-react";

export interface AttackSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToTimeline?: () => void;
  onNavigateToReports?: () => void;
}

// 5 Gamified stages written in simple, clear language for any user
const GAME_STAGES = [
  {
    id: "S1",
    level: 1,
    icon: "🔍",
    title: "1. Probe Hidden Files",
    hackerMove: "The hacker checks if secret system files are locked or accessible.",
    systemDefense: "Radar flags unauthorized directory traversal attempts.",
    endpoint: "GET /document?file=../../../../etc/passwd",
  },
  {
    id: "S2",
    level: 2,
    icon: "💉",
    title: "2. Poison Web Logs",
    hackerMove: "The hacker sends a web request with hidden code inside the visitor name.",
    systemDefense: "Web log inspector spots malicious code injected into access logs.",
    endpoint: "GET /document?file=welcome.txt (with injected header)",
  },
  {
    id: "S3",
    level: 3,
    icon: "💥",
    title: "3. Trigger The Trap",
    hackerMove: "The hacker opens the poisoned log file to execute the planted code.",
    systemDefense: "Intrusion sensor catches unauthorized remote code execution.",
    endpoint: "GET /document?file=../../logs/access.log&cmd=whoami",
  },
  {
    id: "S4",
    level: 4,
    icon: "🕹️",
    title: "4. Remote Control",
    hackerMove: "The hacker opens an interactive command shell to control the server.",
    systemDefense: "Behavioral monitor isolates suspicious command execution.",
    endpoint: "POST /shell (cmd=id; uname -a)",
  },
  {
    id: "S5",
    level: 5,
    icon: "👑",
    title: "5. Admin Takeover",
    hackerMove: "The hacker manipulates system paths to gain supreme administrator (root) power.",
    systemDefense: "Audit shield flags privileged escalation attempt.",
    endpoint: "POST /privesc/run-backup",
  },
];

export const AttackSimulatorModal: React.FC<AttackSimulatorModalProps> = ({
  isOpen,
  onClose,
  onNavigateToTimeline,
  onNavigateToReports,
}) => {
  const [, setLabStatus] = useState<SimulationStatus | null>(null);
  const [isAutoRunning, setIsAutoRunning] = useState(false);
  const [currentRunningStage, setCurrentRunningStage] = useState<string | null>(null);
  const [mitigationActive, setMitigationActive] = useState(false);
  const [expandedStage, setExpandedStage] = useState<string | null>("S1");
  const [stageResults, setStageResults] = useState<Record<string, StageExecutionResult>>({});
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [consoleLogs, setConsoleLogs] = useState<string[]>([
    "Ready. Click 'PLAY ALL STAGES' to watch the attack and defense simulation live.",
  ]);

  const isAutoRunningRef = useRef(false);
  const consoleBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      refreshStatus();
    } else {
      handleStopAutoSimulation();
    }
  }, [isOpen]);

  useEffect(() => {
    consoleBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [consoleLogs]);

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
      addLog(`[SHIELD] Turning Defense Shield: ${nextState ? "ON (Safe Mode)" : "OFF (Vulnerable Mode)"}...`);
      const res = await apiService.toggleSimulationMitigation(nextState);
      setMitigationActive(res.mitigation_active);
      addLog(`[SHIELD] ${res.message}`);
      await refreshStatus();
    } catch (err: any) {
      addLog(`[ERROR] ${err.message}`);
    }
  };

  const handleResetLab = async () => {
    handleStopAutoSimulation();
    try {
      addLog("[RESET] Resetting arena to starting baseline...");
      await apiService.resetSimulationLab();
      setStageResults({});
      setProgressPercent(0);
      setExpandedStage("S1");
      addLog("[READY] Simulation reset. Ready to play.");
      await refreshStatus();
    } catch (err: any) {
      addLog(`[ERROR] Reset failed: ${err.message}`);
    }
  };

  const handleStopAutoSimulation = () => {
    if (isAutoRunningRef.current) {
      isAutoRunningRef.current = false;
      setIsAutoRunning(false);
      setCurrentRunningStage(null);
      addLog("[STOPPED] Simulation paused.");
    }
  };

  const handleRunSingleStage = async (stageId: string) => {
    try {
      setCurrentRunningStage(stageId);
      setExpandedStage(stageId);
      addLog(`[ATTACK] Running Stage ${stageId}...`);

      const res = await apiService.runStageSimulation(stageId);
      setStageResults((prev) => ({ ...prev, [stageId]: res }));

      if (res.http_response.blocked) {
        addLog(`[DEFENSE] 🛡️ Stage ${stageId} BLOCKED (HTTP ${res.http_response.status_code}) - Threat stopped!`);
      } else {
        addLog(`[ALERT] ⚠️ Stage ${stageId} SUCCEEDED (HTTP ${res.http_response.status_code}) - Detection alert triggered!`);
      }
    } catch (err: any) {
      addLog(`[ERROR] Stage ${stageId} failed: ${err.message}`);
    } finally {
      setCurrentRunningStage(null);
    }
  };

  const handleStartAutoSimulation = async () => {
    if (isAutoRunning) return;

    setIsAutoRunning(true);
    isAutoRunningRef.current = true;
    setStageResults({});
    setProgressPercent(0);

    addLog(`[START] Launching 5-stage simulation with Shield: ${mitigationActive ? "ON" : "OFF"}...`);

    const stages = ["S1", "S2", "S3", "S4", "S5"];
    for (let i = 0; i < stages.length; i++) {
      if (!isAutoRunningRef.current) break;

      const stageId = stages[i];
      setCurrentRunningStage(stageId);
      setExpandedStage(stageId);
      setProgressPercent(Math.round(((i + 1) / stages.length) * 100));

      try {
        const res = await apiService.runStageSimulation(stageId);
        setStageResults((prev) => ({ ...prev, [stageId]: res }));

        if (res.http_response.blocked) {
          addLog(`[SHIELD] 🛡️ Stage ${stageId} BLOCKED! The defense shield stopped the attack.`);
        } else {
          addLog(`[BREACH] ⚠️ Stage ${stageId} ALLOWED! Security alert logged.`);
        }
      } catch (err: any) {
        addLog(`[ERROR] Stage ${stageId} failed: ${err.message}`);
      }

      await new Promise((resolve) => setTimeout(resolve, 800));
    }

    if (isAutoRunningRef.current) {
      addLog("[COMPLETE] Simulation finished!");
    }

    setIsAutoRunning(false);
    isAutoRunningRef.current = false;
    setCurrentRunningStage(null);
  };

  // Metrics
  const executedCount = Object.keys(stageResults).length;
  const blockedCount = Object.values(stageResults).filter((r) => r.http_response.blocked).length;
  const isFinished = executedCount === 5;
  const isAllBlocked = isFinished && blockedCount >= 4;

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        handleStopAutoSimulation();
        onClose();
      }}
      title="Attack & Defense Simulator"
      description="Watch the hacker attack in real-time and see how the defense shield catches threats."
      maxWidth="3xl"
    >
      <div className="space-y-4 font-sans select-none">
        {/* Arcade Control Dashboard */}
        <div className="p-4 rounded-xl bg-surface-primary border border-border-default space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            {/* Big Friendly Shield Toggle Button */}
            <button
              onClick={handleToggleMitigation}
              className={`flex items-center gap-2.5 px-4 py-2 rounded-xl font-bold text-xs transition-all ${
                mitigationActive
                  ? "bg-status-success/20 text-status-success border border-status-success/40 shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:bg-status-success/30"
                  : "bg-status-high/15 text-status-high border border-status-high/30 hover:bg-status-high/25"
              }`}
            >
              {mitigationActive ? (
                <>
                  <ShieldCheck className="w-5 h-5 text-status-success" />
                  <div className="text-left">
                    <span className="block font-black">SHIELD IS ON</span>
                    <span className="text-[10px] opacity-80 font-normal">System is protected</span>
                  </div>
                </>
              ) : (
                <>
                  <ShieldOff className="w-5 h-5 text-status-high" />
                  <div className="text-left">
                    <span className="block font-black">SHIELD IS OFF</span>
                    <span className="text-[10px] opacity-80 font-normal">Vulnerable (Click to enable)</span>
                  </div>
                </>
              )}
            </button>

            {/* Big Play / Stop / Reset Buttons */}
            <div className="flex items-center gap-2">
              {isAutoRunning ? (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleStopAutoSimulation}
                  className="flex items-center gap-1.5 font-bold"
                >
                  <Square className="w-4 h-4 fill-current" />
                  <span>Stop</span>
                </Button>
              ) : (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleStartAutoSimulation}
                  className="flex items-center gap-1.5 bg-gradient-to-r from-accent-blue via-accent-cyan to-accent-blue text-slate-950 font-black shadow-glow-cyan hover:scale-[1.02] active:scale-[0.98] transition-all px-4 py-2"
                >
                  <Play className="w-4 h-4 fill-current text-slate-950" />
                  <span>PLAY ALL STAGES</span>
                </Button>
              )}

              <Button
                variant="secondary"
                size="sm"
                onClick={handleResetLab}
                disabled={isAutoRunning}
                className="flex items-center gap-1 text-slate-300"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </Button>
            </div>
          </div>

          {/* Progress Bar (Level 1 to 5) */}
          <div className="space-y-1 pt-1">
            <div className="flex justify-between text-xs text-text-muted">
              <span className="font-semibold text-text-primary">
                {isAutoRunning
                  ? `Simulating Stage ${currentRunningStage}...`
                  : executedCount > 0
                  ? `Completed ${executedCount} of 5 Stages`
                  : "Ready to Start"}
              </span>
              <span className="font-mono font-bold text-accent-cyan">{progressPercent}%</span>
            </div>
            <div className="h-2 w-full bg-surface-secondary rounded-full overflow-hidden border border-border-default">
              <div
                className="h-full bg-gradient-to-r from-accent-blue via-accent-cyan to-status-success transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Victory or Warning Game Banner */}
        {isFinished && (
          <div
            className={`p-4 rounded-xl border animate-fade-in flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
              isAllBlocked
                ? "bg-status-success/15 border-status-success/40 text-text-primary"
                : "bg-status-critical/15 border-status-critical/40 text-text-primary"
            }`}
          >
            <div className="flex items-center gap-3">
              {isAllBlocked ? (
                <ShieldCheck className="w-8 h-8 text-status-success shrink-0" />
              ) : (
                <Flame className="w-8 h-8 text-status-critical shrink-0" />
              )}
              <div>
                <h4 className="font-bold text-sm">
                  {isAllBlocked ? "VICTORY: THREATS BLOCKED!" : "ALERT: ATTACK COMPLETED!"}
                </h4>
                <p className="text-xs text-text-secondary mt-0.5">
                  {isAllBlocked
                    ? "The security shield successfully protected the system from all attacks."
                    : "The attacker gained root power because the shield was off. Turn Shield ON to test protection!"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {onNavigateToTimeline && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    onClose();
                    onNavigateToTimeline();
                  }}
                  className="text-xs"
                >
                  View Timeline
                </Button>
              )}
              {onNavigateToReports && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    onClose();
                    onNavigateToReports();
                  }}
                  className="text-xs"
                >
                  View Report
                </Button>
              )}
            </div>
          </div>
        )}

        {/* 5 Gamified Interactive Stage Cards */}
        <div className="space-y-2.5">
          {GAME_STAGES.map((stage) => {
            const isExpanded = expandedStage === stage.id;
            const res = stageResults[stage.id];
            const isRunning = currentRunningStage === stage.id;

            return (
              <div
                key={stage.id}
                className={`rounded-xl border transition-all overflow-hidden ${
                  isRunning
                    ? "border-accent-cyan ring-2 ring-accent-cyan/30 bg-surface-primary"
                    : res?.http_response.blocked
                    ? "border-status-success/40 bg-surface-primary"
                    : res
                    ? "border-status-critical/40 bg-surface-primary"
                    : "border-border-default bg-surface-primary hover:border-border-active"
                }`}
              >
                {/* Stage Header Line */}
                <div
                  className="p-3 flex items-center justify-between gap-3 cursor-pointer select-none"
                  onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-xl shrink-0">{stage.icon}</span>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-xs sm:text-sm text-text-primary">
                          {stage.title}
                        </span>

                        {/* Status Badges */}
                        {isRunning && (
                          <Badge variant="verified" className="text-[10px] animate-pulse">
                            TESTING...
                          </Badge>
                        )}
                        {res && (
                          <Badge
                            variant={res.http_response.blocked ? "verified" : "critical"}
                            className="text-[10px]"
                          >
                            {res.http_response.blocked ? "🛡️ BLOCKED" : "⚠️ SUCCEEDED"}
                          </Badge>
                        )}
                      </div>
                      <p className="text-[11px] text-text-muted truncate mt-0.5">
                        {stage.hackerMove}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={isRunning || isAutoRunning}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRunSingleStage(stage.id);
                      }}
                      className="text-xs py-1 px-2.5"
                    >
                      {isRunning ? (
                        <Cpu className="w-3.5 h-3.5 animate-spin text-accent-cyan" />
                      ) : (
                        <Play className="w-3 h-3 fill-current text-accent-cyan" />
                      )}
                      <span className="hidden sm:inline">Test</span>
                    </Button>

                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-text-muted" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-text-muted" />
                    )}
                  </div>
                </div>

                {/* Expanded Side-by-Side: Attacker vs Defender */}
                {isExpanded && (
                  <div className="p-3.5 border-t border-border-default/60 bg-surface-secondary/40 space-y-2.5">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      {/* Left: Hacker Move */}
                      <div className="p-3 rounded-lg bg-surface-primary border border-border-default space-y-1.5">
                        <span className="font-bold text-status-critical flex items-center gap-1.5 text-xs">
                          <Flame className="w-3.5 h-3.5" />
                          Hacker Action
                        </span>
                        <p className="text-text-secondary text-xs leading-relaxed">
                          {stage.hackerMove}
                        </p>
                        <div className="pt-1 text-[11px] font-mono text-text-muted truncate">
                          Target: {stage.endpoint}
                        </div>
                      </div>

                      {/* Right: Security Shield */}
                      <div className="p-3 rounded-lg bg-surface-primary border border-border-default space-y-1.5">
                        <span className="font-bold text-accent-cyan flex items-center gap-1.5 text-xs">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Security Shield
                        </span>
                        <p className="text-text-secondary text-xs leading-relaxed">
                          {stage.systemDefense}
                        </p>
                        <div className="pt-1 text-[11px] font-mono">
                          {res?.http_response.blocked ? (
                            <span className="text-status-success font-bold">
                              Result: Blocked with HTTP {res.http_response.status_code}
                            </span>
                          ) : res ? (
                            <span className="text-status-critical font-bold">
                              Result: Caught in logs (Alert fired)
                            </span>
                          ) : (
                            <span className="text-text-muted">Result: Waiting for test</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Streamlined Live Console — Adaptive to White & Dark Theme */}
        <div className="p-3 rounded-xl bg-surface-secondary border border-border-default font-mono text-[11px] space-y-1 max-h-28 overflow-y-auto shadow-inner">
          <div className="text-[10px] text-text-muted uppercase flex items-center gap-1 mb-1 font-semibold">
            <Zap className="w-3 h-3 text-accent-cyan" />
            <span>Live Telemetry Stream</span>
          </div>
          {consoleLogs.map((log, idx) => (
            <div
              key={idx}
              className={
                log.includes("BLOCKED")
                  ? "text-status-success font-semibold"
                  : log.includes("ALLOWED") || log.includes("BREACH")
                  ? "text-status-critical font-semibold"
                  : "text-text-secondary"
              }
            >
              {log}
            </div>
          ))}
          <div ref={consoleBottomRef} />
        </div>
      </div>
    </Modal>
  );
};
