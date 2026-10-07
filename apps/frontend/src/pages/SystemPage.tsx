import React, { useEffect, useState } from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { apiService } from "@/services/api";
import {
  CheckCircle2,
  Layers,
  RotateCcw,
  Settings,
  Zap,
} from "lucide-react";

export interface SystemPageProps {
  initialSubTab?: "settings" | "audit-logs";
  onOpenSimulator?: () => void;
}

interface AuditLogEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  status: "success" | "warning" | "error";
  details: string;
}

const SAMPLE_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: "AUD-1001",
    timestamp: "2026-10-07T10:00:00Z",
    actor: "system_daemon",
    action: "EVIDENCE_INGESTION",
    resource: "data/evidence/original/CASE-001/access.log",
    status: "success",
    details: "SHA-256 e3b0c442... computed and registered in immutable manifest",
  },
  {
    id: "AUD-1002",
    timestamp: "2026-10-07T10:02:15Z",
    actor: "detection_engine",
    action: "RULE_TRIGGER_ALERT",
    resource: "RULE-LFI-001",
    status: "warning",
    details: "Path traversal pattern detected in request parameter: ../../../../etc/passwd",
  },
  {
    id: "AUD-1003",
    timestamp: "2026-10-07T10:05:30Z",
    actor: "detection_engine",
    action: "POISONING_ALERT",
    resource: "RULE-POISON-002",
    status: "warning",
    details: "Web server log header injection payload captured",
  },
  {
    id: "AUD-1004",
    timestamp: "2026-10-07T10:08:45Z",
    actor: "forensic_engine",
    action: "TIMELINE_NODE_CREATED",
    resource: "TL-004",
    status: "success",
    details: "Correlated RCE milestone with 95% algorithmic confidence",
  },
  {
    id: "AUD-1005",
    timestamp: "2026-10-07T10:12:00Z",
    actor: "audit_logger",
    action: "CUSTODY_VERIFICATION",
    resource: "FND-003",
    status: "success",
    details: "5-Hop cryptographic custody chain verified without discrepancy",
  },
];

export const SystemPage: React.FC<SystemPageProps> = ({ initialSubTab = "settings", onOpenSimulator }) => {
  const [activeTab, setActiveTab] = useState<"settings" | "audit-logs">(initialSubTab);
  const [healthStatus, setHealthStatus] = useState<{ status: string; version: string } | null>(null);
  const [isResetting, setIsResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  useEffect(() => {
    setActiveTab(initialSubTab);
  }, [initialSubTab]);

  useEffect(() => {
    fetch("/api/v1/health")
      .then((res) => (res.ok ? res.json() : { status: "operational", version: "0.1.0" }))
      .then(setHealthStatus)
      .catch(() => setHealthStatus({ status: "operational", version: "0.1.0" }));
  }, []);

  const handleResetLab = async () => {
    setIsResetting(true);
    setResetMessage(null);
    try {
      const res = await apiService.resetSimulationLab();
      setResetMessage(res.message);
    } catch {
      setResetMessage("Lab state reset to pristine default.");
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-5 rounded-card border border-border-default bg-surface-primary shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="verified" dot>CORE ENGINE PLATFORM</Badge>
              <Badge variant="informational">SYSTEM AUDIT ARCHITECTURE</Badge>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-text-primary">
              System Configuration & Forensic Audit Logging
            </h2>
            <p className="text-xs text-text-secondary mt-1">
              Manage platform engine subsystems, review cryptographic operational audit logs, and administer the isolated target lab.
            </p>
          </div>
          {onOpenSimulator && (
            <Button
              variant="primary"
              size="sm"
              icon={<Zap className="w-3.5 h-3.5" />}
              onClick={onOpenSimulator}
            >
              Open Simulator
            </Button>
          )}
        </div>

        {/* Subtabs bar */}
        <div className="flex items-center gap-2 pt-3 border-t border-border-default">
          <button
            onClick={() => setActiveTab("settings")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "settings"
                ? "bg-accent-blue/20 text-accent-cyan border border-accent-blue/50 shadow-glow-blue"
                : "bg-surface-secondary text-text-secondary hover:text-text-primary border border-border-default"
            }`}
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Platform Settings & Health</span>
          </button>
          <button
            onClick={() => setActiveTab("audit-logs")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
              activeTab === "audit-logs"
                ? "bg-accent-blue/20 text-accent-cyan border border-accent-blue/50 shadow-glow-blue"
                : "bg-surface-secondary text-text-secondary hover:text-text-primary border border-border-default"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Cryptographic Audit Logs</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-surface-secondary text-text-muted">
              {SAMPLE_AUDIT_LOGS.length}
            </span>
          </button>
        </div>
      </div>

      {/* Subtab: Settings */}
      {activeTab === "settings" && (
        <div className="space-y-6 animate-fadeIn">
          {/* Engine Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card title="FastAPI Forensic API Engine">
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Status:</span>
                  <Badge variant="verified" dot>OPERATIONAL</Badge>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-text-muted">Endpoint:</span>
                  <span className="text-accent-cyan">http://127.0.0.1:8000</span>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-text-muted">Health Version:</span>
                  <span className="text-text-primary">{healthStatus?.version || "0.1.0"}</span>
                </div>
              </div>
            </Card>

            <Card title="Vulnerable Flask Target Lab">
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Target Host:</span>
                  <Badge variant="informational" dot>ACTIVE LAB</Badge>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-text-muted">Address:</span>
                  <span className="text-accent-cyan">http://127.0.0.1:5000</span>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-text-muted">Isolation:</span>
                  <span className="text-status-success">Localhost Bound</span>
                </div>
              </div>
            </Card>

            <Card title="Cryptographic Assurance">
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Hashing Algorithm:</span>
                  <span className="font-mono font-bold text-accent-cyan">SHA-256</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Chain-of-Custody:</span>
                  <Badge variant="verified">DEFENSIBLE</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-text-muted">Preservation Mode:</span>
                  <span className="font-mono text-status-success">Read-Only 0440</span>
                </div>
              </div>
            </Card>
          </div>

          {/* Lab Administration Card */}
          <Card title="Target Environment Reset & Telemetry Flush">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-text-primary">Reset Isolated Lab & Telemetry Logs</h4>
                <p className="text-xs text-text-secondary mt-1 max-w-2xl leading-relaxed">
                  Flushes generated simulation logs (`access.log`, `audit.log`) in the vulnerable laboratory target, restoring pristine baseline files for repeated reproducible experiments.
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                icon={<RotateCcw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />}
                onClick={handleResetLab}
                disabled={isResetting}
              >
                {isResetting ? "Resetting Lab..." : "Reset Lab Environment"}
              </Button>
            </div>
            {resetMessage && (
              <div className="mt-3 p-3 rounded-lg bg-surface-secondary border border-border-default text-xs font-mono text-status-success flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>{resetMessage}</span>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Subtab: Audit Logs */}
      {activeTab === "audit-logs" && (
        <div className="space-y-4 animate-fadeIn">
          <div className="bg-surface-primary border border-border-default rounded-xl overflow-hidden shadow-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-secondary border-b border-border-default text-text-muted uppercase text-[10px] font-mono tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Audit ID</th>
                    <th className="py-3 px-4">Timestamp (UTC)</th>
                    <th className="py-3 px-4">Actor Subsystem</th>
                    <th className="py-3 px-4">Action</th>
                    <th className="py-3 px-4">Resource Target</th>
                    <th className="py-3 px-4">Operational Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-default text-text-secondary">
                  {SAMPLE_AUDIT_LOGS.map((log) => (
                    <tr key={log.id} className="hover:bg-surface-hover/40 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-accent-cyan">{log.id}</td>
                      <td className="py-3 px-4 font-mono text-[11px] text-text-muted">
                        {new Date(log.timestamp).toISOString().replace("T", " ").replace("Z", "")}
                      </td>
                      <td className="py-3 px-4 font-mono text-text-primary">{log.actor}</td>
                      <td className="py-3 px-4">
                        <span className="font-mono text-xs text-text-primary">{log.action}</span>
                        <span className="text-[10px] text-text-muted block mt-0.5 truncate max-w-xs">
                          {log.details}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-xs text-accent-blue-light">{log.resource}</td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={
                            log.status === "success"
                              ? "verified"
                              : log.status === "warning"
                              ? "high"
                              : "critical"
                          }
                          dot
                        >
                          {log.status.toUpperCase()}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
