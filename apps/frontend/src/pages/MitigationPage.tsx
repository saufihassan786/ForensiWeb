import React, { useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RefreshCw,
  Layers,
  FileCheck,
} from "lucide-react";

export const MitigationPage: React.FC = () => {
  const [isMitigated, setIsMitigated] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationTime, setVerificationTime] = useState<string>("2026-10-06T15:30:00Z");

  const handleToggleMitigation = () => {
    setIsVerifying(true);
    setTimeout(() => {
      setIsMitigated((prev) => !prev);
      setVerificationTime(new Date().toISOString());
      setIsVerifying(false);
    }, 600);
  };

  const STAGES = [
    {
      id: "S1",
      name: "LFI Probing & Path Traversal",
      component: "Web App (/document)",
      baseline: { status: "Vulnerable (200 OK)", details: "Returns access.log content via relative traversal" },
      mitigated: { status: "Blocked (403 Forbidden)", details: "Whitelist enforcement rejected ../ traversal" },
      remediation: "Enforce strict basename whitelisting and disallow path traversal tokens in file query parameter.",
    },
    {
      id: "S2",
      name: "Log Poisoning",
      component: "Web Server (access.log)",
      baseline: { status: "Vulnerable (200 OK)", details: "Raw User-Agent recorded without sanitization" },
      mitigated: { status: "Neutralized", details: "Header sanitization strips execution tokens" },
      remediation: "Sanitize HTTP headers prior to disk logging and configure restrictive read-only permissions.",
    },
    {
      id: "S3",
      name: "Log Inclusion RCE",
      component: "Runtime Execution",
      baseline: { status: "Vulnerable (Executed)", details: "Spawned unprivileged child shell process (sh)" },
      mitigated: { status: "Blocked (403 Forbidden)", details: "Log inclusion rejected by security guard" },
      remediation: "Disable allow_url_include and remove execution functions (eval, system, passthru).",
    },
    {
      id: "S4",
      name: "Interactive Web Shell",
      component: "Uploads / Shell (/shell)",
      baseline: { status: "Vulnerable (Active)", details: "Accepts and executes arbitrary shell commands" },
      mitigated: { status: "Disabled (403 Forbidden)", details: "Endpoint disabled by security policy" },
      remediation: "Remove shell interaction endpoints and mount storage directories with 'noexec' flag.",
    },
    {
      id: "S5",
      name: "PATH Privilege Escalation",
      component: "Automation Script",
      baseline: { status: "Vulnerable (Root UID 0)", details: "Executed /tmp/bin hijacked binary as root" },
      mitigated: { status: "Remediated (UID 1000)", details: "Sanitized static PATH /usr/bin:/bin enforced" },
      remediation: "Hardcode absolute binary paths in administrative scripts and drop unnecessary SUID capabilities.",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Mitigation Toggle */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 bg-surface-primary border border-border-default rounded-xl shadow-card">
        <div>
          <div className="flex items-center gap-2">
            {isMitigated ? (
              <span className="p-1.5 rounded-lg bg-status-success/15 text-status-success border border-status-success/30">
                <ShieldCheck className="w-5 h-5" />
              </span>
            ) : (
              <span className="p-1.5 rounded-lg bg-status-critical/15 text-status-critical border border-status-critical/30">
                <ShieldAlert className="w-5 h-5" />
              </span>
            )}
            <h1 className="text-xl font-bold text-text-primary tracking-wide">
              Mitigation & Verification Center
            </h1>
          </div>
          <p className="text-xs text-text-muted mt-1.5">
            Demonstrating before-and-after attack vector neutralization and cryptographic remediation proof.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[10px] font-mono text-text-muted uppercase block">Current Lab State</span>
            <span
              className={`text-xs font-bold font-mono ${
                isMitigated ? "text-status-success" : "text-status-critical"
              }`}
            >
              {isMitigated ? "● SECURE (MITIGATED)" : "○ VULNERABLE (BASELINE)"}
            </span>
          </div>

          <button
            onClick={handleToggleMitigation}
            disabled={isVerifying}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg transition-all duration-150 ${
              isMitigated
                ? "bg-surface-secondary hover:bg-surface-hover border border-border-default text-text-primary"
                : "bg-status-success hover:bg-status-success/90 text-white shadow-glow-cyan"
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? "animate-spin" : ""}`} />
            <span>{isMitigated ? "Switch to Vulnerable Baseline" : "Apply & Verify Mitigations"}</span>
          </button>
        </div>
      </div>

      {/* Before / After Quantitative Comparison Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-surface-primary border border-border-default rounded-xl">
          <span className="text-[10px] font-mono uppercase text-text-muted">Defense Efficacy</span>
          <div className="text-2xl font-bold font-mono text-accent-cyan mt-1">
            {isMitigated ? "100.0%" : "0.0%"}
          </div>
          <span className="text-[11px] text-text-secondary mt-1 block">
            {isMitigated ? "All 5 attack stages blocked" : "All stages executed successfully"}
          </span>
        </div>

        <div className="p-4 bg-surface-primary border border-border-default rounded-xl">
          <span className="text-[10px] font-mono uppercase text-text-muted">Attack Chain Neutralization</span>
          <div className="text-2xl font-bold font-mono text-status-success mt-1">
            {isMitigated ? "Stage S1" : "None"}
          </div>
          <span className="text-[11px] text-text-secondary mt-1 block">
            {isMitigated ? "Broken at LFI reconnaissance" : "Progressed to root compromise"}
          </span>
        </div>

        <div className="p-4 bg-surface-primary border border-border-default rounded-xl">
          <span className="text-[10px] font-mono uppercase text-text-muted">Privilege Elevation Status</span>
          <div className={`text-2xl font-bold font-mono mt-1 ${isMitigated ? "text-status-success" : "text-status-critical"}`}>
            {isMitigated ? "UID 1000" : "UID 0 (ROOT)"}
          </div>
          <span className="text-[11px] text-text-secondary mt-1 block">
            {isMitigated ? "Unprivileged user preserved" : "Full host takeover achieved"}
          </span>
        </div>

        <div className="p-4 bg-surface-primary border border-border-default rounded-xl">
          <span className="text-[10px] font-mono uppercase text-text-muted">Critical Detections</span>
          <div className="text-2xl font-bold font-mono text-text-primary mt-1">
            {isMitigated ? "0 Alerts" : "4 Critical"}
          </div>
          <span className="text-[11px] text-text-secondary mt-1 block">
            {isMitigated ? "No malicious activity detected" : "Multiple high-severity detections"}
          </span>
        </div>
      </div>

      {/* Stage-by-Stage Telemetry Matrix */}
      <div className="bg-surface-primary border border-border-default rounded-xl overflow-hidden shadow-card">
        <div className="p-4 bg-surface-secondary border-b border-border-default flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
            <Layers className="w-4 h-4 text-accent-cyan" />
            Attack Chain Stage Verification Matrix
          </h2>
          <span className="text-[10px] font-mono text-text-muted">
            Verified: {new Date(verificationTime).toLocaleTimeString()}
          </span>
        </div>

        <div className="divide-y divide-border-default">
          {STAGES.map((s) => (
            <div key={s.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-surface-hover/30 transition-colors">
              <div className="max-w-md">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-accent-blue/15 text-accent-cyan border border-accent-blue/30">
                    {s.id}
                  </span>
                  <span className="font-semibold text-xs text-text-primary">{s.name}</span>
                  <span className="text-[10px] font-mono text-text-muted">({s.component})</span>
                </div>
                <p className="text-[11px] text-text-muted mt-1 leading-relaxed">
                  <strong className="text-text-secondary">Remediation:</strong> {s.remediation}
                </p>
              </div>

              <div className="flex items-center gap-4 text-xs font-mono">
                {/* Baseline Column */}
                <div className="p-2.5 rounded-lg bg-surface-secondary border border-border-default min-w-[180px]">
                  <span className="text-[9px] uppercase tracking-wider text-text-muted block">Baseline Run</span>
                  <div className="flex items-center gap-1.5 text-status-critical font-semibold mt-0.5">
                    <XCircle className="w-3.5 h-3.5" />
                    <span>{s.baseline.status}</span>
                  </div>
                </div>

                <ArrowRight className="w-4 h-4 text-text-muted hidden md:block" />

                {/* Mitigated Column */}
                <div className={`p-2.5 rounded-lg border min-w-[180px] ${
                  isMitigated
                    ? "bg-status-success/10 border-status-success/30 text-status-success"
                    : "bg-surface-secondary border-border-default text-text-muted"
                }`}>
                  <span className="text-[9px] uppercase tracking-wider text-text-muted block">Post-Mitigation</span>
                  <div className="flex items-center gap-1.5 font-semibold mt-0.5">
                    {isMitigated ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{s.mitigated.status}</span>
                      </>
                    ) : (
                      <span>Not Active</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Verification Evidence Artifact Card */}
      <div className="p-5 bg-surface-primary border border-border-default rounded-xl shadow-card space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-accent-cyan" />
            <h3 className="font-semibold text-xs text-text-primary">Cryptographic Verification Evidence Artifact</h3>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-status-success/15 text-status-success border border-status-success/30">
            VERIFIED_REMEDIATED
          </span>
        </div>
        <p className="text-xs text-text-secondary leading-relaxed">
          The before-and-after experimental run produces an immutable evaluation manifest confirming that all five identified attack vectors were successfully neutralized without introducing operational regressions.
        </p>
        <div className="p-3 bg-surface-secondary border border-border-default rounded-lg font-mono text-[10px] text-text-muted flex flex-col md:flex-row md:items-center justify-between gap-2">
          <span>ARTIFACT: <code>VERIF-CASE-001-A48F9E2B</code></span>
          <span>SHA-256: <code>d5fe93f8e405e80a0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b9</code></span>
        </div>
      </div>
    </div>
  );
};
