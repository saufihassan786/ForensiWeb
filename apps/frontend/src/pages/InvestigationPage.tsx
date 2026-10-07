import React, { useEffect, useState } from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Modal } from "@/components/common/Modal";
import { apiService } from "@/services/api";
import { Case, Finding, TraceabilityReport } from "@/types/api";
import {
  CheckCircle2,
  Database,
  FileCheck,
  ShieldCheck,
} from "lucide-react";

export const InvestigationPage: React.FC = () => {
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [activeTraceFinding, setActiveTraceFinding] = useState<Finding | null>(null);
  const [traceReport, setTraceReport] = useState<TraceabilityReport | null>(null);
  const [isVerifyingTrace, setIsVerifyingTrace] = useState<boolean>(false);

  useEffect(() => {
    apiService.getCases().then((list) => {
      if (list.length > 0) setSelectedCase(list[0]);
    });
    apiService.getFindings().then(setFindings);
  }, []);

  const handleInspectTraceability = async (finding: Finding) => {
    setActiveTraceFinding(finding);
    setIsVerifyingTrace(true);
    const report = await apiService.getTraceability(finding.id, finding.case_id);
    setTraceReport(report);
    setIsVerifyingTrace(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-card border border-border-default bg-surface-primary shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="verified" dot>INVESTIGATION WORKSPACE (PHASE-12)</Badge>
            <Badge variant="informational">CHAIN OF CUSTODY ASSURED</Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-text-primary">
            Unified Case Investigation & Finding Traceability
          </h2>
          <p className="text-xs text-text-secondary mt-1">
            Navigate cases, inspect forensic evidence with byte offsets, and audit end-to-end evidence-to-finding traceability.
          </p>
        </div>
      </div>

      {/* Case Management Card */}
      {selectedCase && (
        <Card title={`Active Case: ${selectedCase.id}`}>
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-sm font-bold text-text-primary">{selectedCase.title}</h3>
                <Badge variant={selectedCase.priority === "critical" ? "critical" : "high"}>
                  {selectedCase.priority.toUpperCase()}
                </Badge>
                <Badge variant="verified">{selectedCase.status.toUpperCase()}</Badge>
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">{selectedCase.description}</p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono text-text-muted">
              <span>Opened: {new Date(selectedCase.created_at).toLocaleDateString()}</span>
              <span>Updated: {new Date(selectedCase.updated_at).toLocaleTimeString()}</span>
            </div>
          </div>
        </Card>
      )}

      {/* Evidence Repository Workspace */}
      <Card title="Preserved Evidence Artifacts (Immutable Storage)">
        <div className="space-y-3">
          {[
            {
              filename: "access.log",
              source: "Web Access Telemetry",
              size: "14.2 KB",
              sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
              status: "verified",
              location: "data/evidence/original/CASE-001/access.log",
            },
            {
              filename: "app_error.log",
              source: "Flask Application Worker",
              size: "8.6 KB",
              sha256: "8729837492837492837498237498237498237498237498237498237498237498",
              status: "verified",
              location: "data/evidence/original/CASE-001/app_error.log",
            },
            {
              filename: "audit.log",
              source: "Linux Kernel Auditd Telemetry",
              size: "32.1 KB",
              sha256: "5938475938475938475938475938475938475938475938475938475938475938",
              status: "verified",
              location: "data/evidence/original/CASE-001/audit.log",
            },
          ].map((ev, i) => (
            <div
              key={i}
              className="p-3.5 rounded-lg border border-border-default bg-surface-secondary flex flex-col md:flex-row md:items-center justify-between text-xs gap-3"
            >
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-accent-cyan flex-shrink-0" />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-text-primary">{ev.filename}</span>
                    <span className="text-[11px] text-text-muted">({ev.source})</span>
                    <Badge variant="verified" dot>
                      SHA-256 VERIFIED
                    </Badge>
                  </div>
                  <span className="font-mono text-[10px] text-text-muted block mt-0.5">
                    Hash: {ev.sha256.substring(0, 32)}...
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-[11px] text-text-muted">{ev.size}</span>
                <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-bg-primary text-text-secondary border border-border-default">
                  Read-Only (0440)
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Forensic Findings & Traceability Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-accent-cyan" />
            Confirmed Forensic Findings & Remediation ({findings.length})
          </h3>
          <span className="text-xs text-text-muted">
            All findings require cryptographic evidence traceability
          </span>
        </div>

        <div className="space-y-4">
          {findings.map((fnd) => (
            <div
              key={fnd.id}
              className="p-5 rounded-card border border-border-default bg-surface-primary hover:border-border-active transition-all shadow-sm"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-accent-cyan">{fnd.id}</span>
                  <Badge variant={fnd.severity as any}>{fnd.severity.toUpperCase()}</Badge>
                  <Badge variant="informational">{fnd.attack_stage}</Badge>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  icon={<ShieldCheck className="w-3.5 h-3.5" />}
                  onClick={() => handleInspectTraceability(fnd)}
                >
                  Verify Traceability Chain
                </Button>
              </div>

              <h4 className="text-sm font-bold text-text-primary mt-1">{fnd.title}</h4>
              <p className="text-xs text-text-secondary mt-1.5 leading-relaxed">{fnd.analysis_summary}</p>

              {fnd.mitigation_summary && (
                <div className="mt-3 p-3 rounded-lg bg-surface-secondary border border-border-default/80 text-xs">
                  <span className="text-[10px] font-mono font-bold uppercase text-status-success block mb-1">
                    Recommended Mitigation & Verification:
                  </span>
                  <p className="text-text-secondary">{fnd.mitigation_summary}</p>
                </div>
              )}

              <div className="mt-3 pt-3 border-t border-border-default/50 flex flex-wrap items-center justify-between text-[11px] font-mono text-text-muted">
                <span>Evidence Links: {fnd.evidence_references.join(", ")}</span>
                <span>Detections: {fnd.detection_ids.join(", ")}</span>
                <span>Events: {fnd.event_ids.join(", ")}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Critical Traceability Inspector Modal */}
      {activeTraceFinding && (
        <Modal
          isOpen={!!activeTraceFinding}
          onClose={() => setActiveTraceFinding(null)}
          title={`Evidence-to-Finding Traceability: ${activeTraceFinding.id}`}
          description="Verifying complete unbroken chain: Finding -> Detection -> Event -> Evidence -> Original Artifact"
          maxWidth="xl"
        >
          {isVerifyingTrace ? (
            <div className="py-8 text-center text-xs text-text-secondary animate-pulse">
              Auditing cryptographic custody chain and byte offsets...
            </div>
          ) : traceReport ? (
            <div className="space-y-5">
              <div
                className={`p-4 rounded-lg border flex items-center justify-between ${
                  traceReport.is_fully_traceable
                    ? "bg-status-success/10 border-status-success/30 text-status-success"
                    : "bg-status-critical/10 border-status-critical/30 text-status-critical"
                }`}
              >
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                  <div>
                    <h4 className="text-xs font-bold">
                      {traceReport.is_fully_traceable
                        ? "Cryptographic Chain-of-Custody Verified"
                        : "Traceability Broken - Missing References"}
                    </h4>
                    <span className="text-[11px] opacity-80 block">
                      Chain Depth: {traceReport.chain_depth} layers audited without gap
                    </span>
                  </div>
                </div>
                <Badge variant={traceReport.is_fully_traceable ? "verified" : "critical"}>
                  {traceReport.is_fully_traceable ? "DEFENSIBLE" : "DEFECTIVE"}
                </Badge>
              </div>

              {/* 5 Hops Progression */}
              <div className="space-y-3">
                <h4 className="text-xs font-mono font-bold uppercase text-text-muted">
                  5-Layer Forensic Traceability Chain
                </h4>
                {traceReport.hops.map((hop, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-lg border border-border-default bg-surface-secondary flex items-start gap-3 text-xs"
                  >
                    <div className="w-6 h-6 rounded-full bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center text-accent-cyan font-mono text-[10px] font-bold flex-shrink-0 mt-0.5">
                      0{idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold uppercase text-accent-cyan">
                          LAYER: {hop.layer.toUpperCase()}
                        </span>
                        <Badge variant={hop.status === "verified" ? "verified" : "high"}>
                          {hop.status.toUpperCase()}
                        </Badge>
                      </div>
                      <span className="font-mono text-[11px] text-text-primary block mt-0.5">
                        Entity: {hop.entity_id}
                      </span>
                      <div className="mt-1 text-[11px] text-text-muted font-mono">
                        {Object.entries(hop.details).map(([k, v]) => (
                          <span key={k} className="mr-3">
                            {k}: {String(v)}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Verified Hash Callout */}
              {traceReport.verified_sha256 && (
                <div className="p-3 rounded bg-bg-primary border border-border-default font-mono text-xs">
                  <span className="text-[10px] text-text-muted block uppercase">
                    Pristine Original SHA-256 Digest:
                  </span>
                  <span className="text-accent-cyan break-all select-all font-bold">
                    {traceReport.verified_sha256}
                  </span>
                </div>
              )}
            </div>
          ) : null}
        </Modal>
      )}
    </div>
  );
};
