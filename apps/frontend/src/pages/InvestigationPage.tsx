import React, { useEffect, useState } from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { apiService } from "@/services/api";
import { Case, Finding, TraceabilityReport } from "@/types/api";
import {
  CheckCircle2,
  Copy,
  Database,
  ExternalLink,
  Eye,
  FileCheck,
  FolderCheck,
  Layers,
  Search,
  ShieldAlert,
  ShieldCheck,
  Terminal,
} from "lucide-react";

export interface InvestigationPageProps {
  defaultSubTab?: string;
  onOpenSimulator?: () => void;
}

interface EvidenceArtifact {
  id: string;
  filename: string;
  source: string;
  size: string;
  sha256: string;
  status: "verified" | "stored";
  location: string;
  recordsCount: number;
  rawSample: string[];
}

interface NormalizedEventItem {
  id: string;
  timestamp: string;
  source: string;
  eventType: string;
  severity: "critical" | "high" | "medium" | "low";
  stage: string;
  actorIp: string;
  action: string;
  byteOffset: string;
  payload: string;
}

interface DetectionRuleItem {
  id: string;
  name: string;
  stage: string;
  mitreId: string;
  mitreTechnique: string;
  severity: "critical" | "high" | "medium";
  pattern: string;
  matchedCount: number;
  recommendation: string;
}

const SAMPLE_ARTIFACTS: EvidenceArtifact[] = [
  {
    id: "ART-001",
    filename: "access.log",
    source: "Apache Web Server Access Log",
    size: "14.2 KB",
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    status: "verified",
    location: "data/evidence/original/CASE-001/access.log",
    recordsCount: 96,
    rawSample: [
      "172.28.0.5 - - [07/Oct/2026:10:00:01 +0000] \"GET / HTTP/1.1\" 200 4821 \"-\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\"",
      "172.28.0.5 - - [07/Oct/2026:10:00:15 +0000] \"GET /view?page=docs/index.html HTTP/1.1\" 200 1204 \"-\" \"Mozilla/5.0\"",
      "172.28.0.5 - - [07/Oct/2026:10:02:14 +0000] \"GET /view?page=../../../../etc/passwd HTTP/1.1\" 200 2410 \"-\" \"curl/7.88.1\"",
      "172.28.0.5 - - [07/Oct/2026:10:02:40 +0000] \"GET /view?page=../../var/log/apache2/access.log HTTP/1.1\" 200 8192 \"-\" \"curl/7.88.1\"",
      "172.28.0.5 - - [07/Oct/2026:10:05:30 +0000] \"GET / HTTP/1.1\" 200 4821 \"-\" \"[SIMULATED_POISON_TOKEN_STAGE2]\"",
      "172.28.0.5 - - [07/Oct/2026:10:08:45 +0000] \"GET /view?page=../../var/log/apache2/access.log&cmd=whoami HTTP/1.1\" 200 512 \"-\" \"curl/7.88.1\"",
      "172.28.0.5 - - [07/Oct/2026:10:09:12 +0000] \"GET /view?page=../../var/log/apache2/access.log&cmd=id;uname+-a HTTP/1.1\" 200 680 \"-\" \"curl/7.88.1\"",
    ],
  },
  {
    id: "ART-002",
    filename: "app_error.log",
    source: "Flask Application Worker",
    size: "8.6 KB",
    sha256: "8729837492837492837498237498237498237498237498237498237498237498",
    status: "verified",
    location: "data/evidence/original/CASE-001/app_error.log",
    recordsCount: 32,
    rawSample: [
      "[2026-10-07 10:02:14,102] [WARNING] [app.views] Path traversal syntax detected in query: ../../../../etc/passwd",
      "[2026-10-07 10:05:30,410] [INFO] [werkzeug] 172.28.0.5 - \"GET / HTTP/1.1\" 200 - User-Agent injected execution token",
      "[2026-10-07 10:08:45,891] [ALERT] [app.security] Subprocess execution triggered from web worker context",
    ],
  },
  {
    id: "ART-003",
    filename: "audit.log",
    source: "Linux Kernel Auditd Telemetry",
    size: "32.1 KB",
    sha256: "5938475938475938475938475938475938475938475938475938475938475938",
    status: "verified",
    location: "data/evidence/original/CASE-001/audit.log",
    recordsCount: 48,
    rawSample: [
      "type=EXECVE msg=audit(1791367920.104:420): argc=3 a0=\"sh\" a1=\"-c\" a2=\"whoami\"",
      "type=SYSCALL msg=audit(1791367920.104:420): arch=c000003e syscall=59 success=yes exit=0 ppid=1042 pid=1045 auid=4294967295 uid=33 gid=33 euid=33",
      "type=USER_CMD msg=audit(1791368120.450:432): pid=1050 uid=33 auid=4294967295 cmd=\"/usr/bin/sudo /opt/check_update\"",
      "type=EXECVE msg=audit(1791368120.455:433): argc=1 a0=\"/tmp/bin/curl\" (PATH hijack target: UID=0)",
      "type=CRED_ACQ msg=audit(1791368120.460:434): pid=1052 uid=0 auid=0 exe=\"/tmp/bin/curl\" hostname=? addr=? terminal=?",
    ],
  },
];

const SAMPLE_EVENTS: NormalizedEventItem[] = [
  {
    id: "EVT-001",
    timestamp: "2026-10-07T10:00:15Z",
    source: "web_access_log",
    eventType: "HTTP_QUERY",
    severity: "low",
    stage: "RECON",
    actorIp: "172.28.0.5",
    action: "GET /view?page=docs/index.html",
    byteOffset: "0x00000078 - 0x000000E4",
    payload: "page=docs/index.html",
  },
  {
    id: "EVT-002",
    timestamp: "2026-10-07T10:02:14Z",
    source: "web_access_log",
    eventType: "LFI_PROBE",
    severity: "high",
    stage: "LFI",
    actorIp: "172.28.0.5",
    action: "GET /view?page=../../../../etc/passwd",
    byteOffset: "0x000000E5 - 0x0000015A",
    payload: "../../../../etc/passwd",
  },
  {
    id: "EVT-003",
    timestamp: "2026-10-07T10:05:30Z",
    source: "web_access_log",
    eventType: "HEADER_POISON",
    severity: "critical",
    stage: "LOG_POISONING",
    actorIp: "172.28.0.5",
    action: "GET / HTTP/1.1 with Shell User-Agent",
    byteOffset: "0x000001FB - 0x0000028A",
    payload: "User-Agent: [SIMULATED_POISON_TOKEN_STAGE2]",
  },
  {
    id: "EVT-004",
    timestamp: "2026-10-07T10:08:45Z",
    source: "web_access_log",
    eventType: "RCE_EXECUTION",
    severity: "critical",
    stage: "RCE",
    actorIp: "172.28.0.5",
    action: "GET /view?page=../../var/log/apache2/access.log&cmd=whoami",
    byteOffset: "0x0000028B - 0x00000320",
    payload: "cmd=whoami -> uid=33(www-data)",
  },
  {
    id: "EVT-005",
    timestamp: "2026-10-07T10:12:00Z",
    source: "auditd_log",
    eventType: "PRIVILEGE_ESCALATION",
    severity: "critical",
    stage: "PRIVILEGE_ESCALATION",
    actorIp: "127.0.0.1",
    action: "sudo /opt/check_update -> execution of /tmp/bin/curl",
    byteOffset: "0x00000412 - 0x000004D0",
    payload: "euid=0 (root) gained via manipulated PATH environment",
  },
];

const SAMPLE_DETECTIONS: DetectionRuleItem[] = [
  {
    id: "DET-001",
    name: "Path Traversal Directory Escape Detection",
    stage: "LFI",
    mitreId: "T1083",
    mitreTechnique: "File and Directory Discovery",
    severity: "high",
    pattern: "(?:\\.\\./|\\.\\.\\\\)+.*(?:etc/passwd|windows/win\\.ini)",
    matchedCount: 2,
    recommendation: "Apply strict basename parameter whitelist & configure open_basedir limits.",
  },
  {
    id: "DET-002",
    name: "Web Server Log Header Poisoning",
    stage: "LOG_POISONING",
    mitreId: "T1059.004",
    mitreTechnique: "Command and Scripting Interpreter: Unix Shell",
    severity: "critical",
    pattern: "SIMULATED_POISON_TOKEN|HEADER_INJECTION",
    matchedCount: 1,
    recommendation: "Sanitize HTTP headers before logging; set log files read-only (chmod 640 root:adm).",
  },
  {
    id: "DET-003",
    name: "Web Application Log-Inclusion RCE",
    stage: "RCE",
    mitreId: "T1505.003",
    mitreTechnique: "Server Software Component: Web Shell",
    severity: "critical",
    pattern: "access\\.log.*&(?:cmd|exec|system)=",
    matchedCount: 3,
    recommendation: "Disable allow_url_include, separate web root from writable log mounts.",
  },
  {
    id: "DET-004",
    name: "Sudo Insecure PATH Privilege Hijacking",
    stage: "PRIVILEGE_ESCALATION",
    mitreId: "T1548.001",
    mitreTechnique: "Abuse Elevation Control: Setuid and Setgid",
    severity: "critical",
    pattern: "USER_CMD.*sudo.*check_update.*EXECVE.*a0=\"/tmp/",
    matchedCount: 1,
    recommendation: "Enforce 'Defaults secure_path' in /etc/sudoers and use absolute binary paths.",
  },
];

export const InvestigationPage: React.FC<InvestigationPageProps> = ({ defaultSubTab = "cases" }) => {
  const [activeSubTab, setActiveSubTab] = useState<string>(defaultSubTab);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [activeTraceFinding, setActiveTraceFinding] = useState<Finding | null>(null);
  const [traceReport, setTraceReport] = useState<TraceabilityReport | null>(null);
  const [isVerifyingTrace, setIsVerifyingTrace] = useState<boolean>(false);

  // Modals & Inspectors
  const [inspectingArtifact, setInspectingArtifact] = useState<EvidenceArtifact | null>(null);
  const [artifactSearchQuery, setArtifactSearchQuery] = useState("");
  const [copiedHash, setCopiedHash] = useState(false);
  const [verifiedArtifactHash, setVerifiedArtifactHash] = useState<string | null>(null);

  const [inspectingEvent, setInspectingEvent] = useState<NormalizedEventItem | null>(null);
  const [eventSearchQuery, setEventSearchQuery] = useState("");
  const [eventStageFilter, setEventStageFilter] = useState("ALL");

  const [inspectingDetection, setInspectingDetection] = useState<DetectionRuleItem | null>(null);

  useEffect(() => {
    setActiveSubTab(defaultSubTab);
  }, [defaultSubTab]);

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

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const filteredEvents = SAMPLE_EVENTS.filter((e) => {
    const matchesStage = eventStageFilter === "ALL" || e.stage === eventStageFilter;
    const matchesSearch =
      !eventSearchQuery ||
      e.action.toLowerCase().includes(eventSearchQuery.toLowerCase()) ||
      e.actorIp.includes(eventSearchQuery) ||
      e.id.toLowerCase().includes(eventSearchQuery.toLowerCase()) ||
      e.payload.toLowerCase().includes(eventSearchQuery.toLowerCase());
    return matchesStage && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner & Sub-Navigation */}
      <div className="p-5 rounded-card border border-border-default bg-surface-primary shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="verified" dot>INVESTIGATION</Badge>
              <Badge variant="informational">CASE-001</Badge>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-text-primary">
              Evidence &amp; Case Files
            </h2>
            <p className="text-xs text-text-secondary mt-0.5">
              Inspect preserved logs, review detected events, and verify findings.
            </p>
          </div>
        </div>

        {/* Interactive Subtabs Bar */}
        <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-border-default">
          {[
            { id: "cases", label: "Active Cases", icon: FolderCheck, badge: "1" },
            { id: "evidence", label: "Preserved Artifacts", icon: Database, badge: "3" },
            { id: "events", label: "Normalized Events", icon: Layers, badge: "5" },
            { id: "detections", label: "Detection Alerts", icon: ShieldAlert, badge: "4" },
            { id: "findings", label: "Forensic Findings", icon: FileCheck, badge: findings.length.toString() },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? "bg-accent-blue/20 text-accent-cyan border border-accent-blue/50 shadow-glow-blue"
                    : "bg-surface-secondary text-text-secondary hover:text-text-primary hover:bg-surface-hover border border-border-default"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-accent-cyan" : "text-text-muted"}`} />
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                    isActive ? "bg-accent-blue text-white" : "bg-bg-primary text-text-muted"
                  }`}
                >
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* SUBTAB 1: CASES */}
      {activeSubTab === "cases" && (
        <div className="space-y-4 animate-fade-in">
          {selectedCase && (
            <Card title={`Selected Case: ${selectedCase.id}`}>
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <h3 className="text-sm font-bold text-text-primary">{selectedCase.title}</h3>
                    <Badge variant={selectedCase.priority === "critical" ? "critical" : "high"}>
                      {selectedCase.priority.toUpperCase()}
                    </Badge>
                    <Badge variant="verified">{selectedCase.status.toUpperCase()}</Badge>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed max-w-3xl">
                    {selectedCase.description}
                  </p>
                </div>
                <div className="flex flex-col text-xs font-mono text-text-muted gap-1">
                  <span>Opened: {new Date(selectedCase.created_at).toLocaleDateString()}</span>
                  <span>Updated: {new Date(selectedCase.updated_at).toLocaleTimeString()}</span>
                  <span className="text-accent-cyan">Standard: ISO/IEC 27037:2012</span>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-border-default grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-surface-secondary border border-border-default">
                  <span className="text-[10px] font-mono uppercase text-text-muted">Target Environment</span>
                  <span className="font-bold text-text-primary block mt-0.5">Flask / Apache 2.4</span>
                </div>
                <div className="p-3 rounded-lg bg-surface-secondary border border-border-default">
                  <span className="text-[10px] font-mono uppercase text-text-muted">Attack Vectors</span>
                  <span className="font-bold text-status-critical block mt-0.5">LFI &bull; Poisoning &bull; PrivEsc</span>
                </div>
                <div className="p-3 rounded-lg bg-surface-secondary border border-border-default">
                  <span className="text-[10px] font-mono uppercase text-text-muted">Evidence Custody</span>
                  <span className="font-bold text-status-success block mt-0.5">100% Cryptographically Hashed</span>
                </div>
                <div className="p-3 rounded-lg bg-surface-secondary border border-border-default">
                  <span className="text-[10px] font-mono uppercase text-text-muted">Mitigation Proof</span>
                  <span className="font-bold text-accent-cyan block mt-0.5">Verified Neutralized</span>
                </div>
              </div>
            </Card>
          )}

          {/* Quick Sub-Navigation Links */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <button
              onClick={() => setActiveSubTab("evidence")}
              className="p-4 rounded-xl border border-border-default bg-surface-primary hover:border-accent-blue transition-all text-left group"
            >
              <Database className="w-5 h-5 text-accent-cyan mb-2 group-hover:scale-110 transition-transform" />
              <h4 className="text-xs font-bold text-text-primary">Preserved Artifacts (3)</h4>
              <p className="text-[11px] text-text-muted mt-1">Inspect access.log, app_error.log, and audit.log.</p>
            </button>
            <button
              onClick={() => setActiveSubTab("events")}
              className="p-4 rounded-xl border border-border-default bg-surface-primary hover:border-accent-blue transition-all text-left group"
            >
              <Layers className="w-5 h-5 text-accent-cyan mb-2 group-hover:scale-110 transition-transform" />
              <h4 className="text-xs font-bold text-text-primary">Normalized Events (5)</h4>
              <p className="text-[11px] text-text-muted mt-1">Review query events with exact byte offsets.</p>
            </button>
            <button
              onClick={() => setActiveSubTab("detections")}
              className="p-4 rounded-xl border border-border-default bg-surface-primary hover:border-accent-blue transition-all text-left group"
            >
              <ShieldAlert className="w-5 h-5 text-status-critical mb-2 group-hover:scale-110 transition-transform" />
              <h4 className="text-xs font-bold text-text-primary">Detection Alerts (4)</h4>
              <p className="text-[11px] text-text-muted mt-1">MITRE ATT&CK matched signatures.</p>
            </button>
            <button
              onClick={() => setActiveSubTab("findings")}
              className="p-4 rounded-xl border border-border-default bg-surface-primary hover:border-accent-blue transition-all text-left group"
            >
              <FileCheck className="w-5 h-5 text-status-success mb-2 group-hover:scale-110 transition-transform" />
              <h4 className="text-xs font-bold text-text-primary">Forensic Findings ({findings.length})</h4>
              <p className="text-[11px] text-text-muted mt-1">Unbroken 5-layer custody audit.</p>
            </button>
          </div>
        </div>
      )}

      {/* SUBTAB 2: EVIDENCE ARTIFACTS */}
      {activeSubTab === "evidence" && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <Database className="w-4 h-4 text-accent-cyan" />
              Preserved Forensic Evidence Repository (Read-Only 0440)
            </h3>
            <span className="text-xs text-text-muted">
              Pristine storage with SHA-256 integrity verification
            </span>
          </div>

          <div className="space-y-3">
            {SAMPLE_ARTIFACTS.map((artifact) => (
              <div
                key={artifact.id}
                className="p-4 rounded-card border border-border-default bg-surface-primary hover:border-border-active transition-all shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2.5 rounded-lg bg-surface-secondary border border-border-default text-accent-cyan shrink-0 mt-0.5">
                    <Database className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono font-bold text-sm text-text-primary">{artifact.filename}</span>
                      <span className="text-xs text-text-muted">({artifact.source})</span>
                      <Badge variant="verified" dot>
                        SHA-256 VERIFIED
                      </Badge>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-secondary text-text-muted border border-border-default">
                        {artifact.recordsCount} Records
                      </span>
                    </div>
                    <span className="font-mono text-xs text-accent-cyan block mt-1 select-all">
                      Hash: {artifact.sha256}
                    </span>
                    <span className="font-mono text-[11px] text-text-muted block mt-0.5">
                      Storage: {artifact.location} &bull; Size: {artifact.size}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={<Copy className="w-3.5 h-3.5" />}
                    onClick={() => handleCopyHash(artifact.sha256)}
                  >
                    Copy Hash
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    icon={<Eye className="w-3.5 h-3.5" />}
                    onClick={() => {
                      setInspectingArtifact(artifact);
                      setVerifiedArtifactHash(null);
                    }}
                  >
                    Inspect Artifact
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUBTAB 3: NORMALIZED EVENTS */}
      {activeSubTab === "events" && (
        <div className="space-y-4 animate-fade-in">
          {/* Filters Bar */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <div className="flex-1 w-full">
              <Input
                placeholder="Search events by IP, method, action path, or byte offset..."
                value={eventSearchQuery}
                onChange={(e) => setEventSearchQuery(e.target.value)}
                leadingIcon={<Search className="w-4 h-4" />}
              />
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <select
                value={eventStageFilter}
                onChange={(e) => setEventStageFilter(e.target.value)}
                className="px-3 py-2 rounded-lg bg-surface-primary border border-border-default text-xs text-text-primary focus:outline-none focus:border-accent-blue"
              >
                <option value="ALL">All Attack Stages</option>
                <option value="RECON">Stage 1: Recon</option>
                <option value="LFI">Stage 2: LFI Traversal</option>
                <option value="LOG_POISONING">Stage 3: Log Poisoning</option>
                <option value="RCE">Stage 4: RCE Execution</option>
                <option value="PRIVILEGE_ESCALATION">Stage 5: Privilege Escalation</option>
              </select>
              {(eventStageFilter !== "ALL" || eventSearchQuery) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setEventStageFilter("ALL");
                    setEventSearchQuery("");
                  }}
                >
                  Reset
                </Button>
              )}
            </div>
          </div>

          {/* Events Table */}
          <div className="bg-surface-primary border border-border-default rounded-xl overflow-hidden shadow-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-secondary border-b border-border-default text-text-muted uppercase text-[10px] font-mono tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Event ID</th>
                    <th className="py-3 px-4">Timestamp (UTC)</th>
                    <th className="py-3 px-4">Stage & Severity</th>
                    <th className="py-3 px-4">Actor / Source</th>
                    <th className="py-3 px-4">Action & Byte Offset</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-default text-text-secondary">
                  {filteredEvents.map((evt) => (
                    <tr
                      key={evt.id}
                      onClick={() => setInspectingEvent(evt)}
                      className="hover:bg-surface-hover/50 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-4 font-mono font-bold text-accent-cyan">{evt.id}</td>
                      <td className="py-3 px-4 font-mono text-[11px] text-text-muted">
                        {new Date(evt.timestamp).toISOString().replace("T", " ").replace("Z", "")}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5">
                          <Badge variant={evt.severity === "critical" ? "critical" : evt.severity === "high" ? "high" : "informational"}>
                            {evt.stage}
                          </Badge>
                          <span className="text-[10px] font-mono text-text-muted uppercase">({evt.severity})</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-mono text-text-primary">{evt.actorIp}</span>
                        <span className="text-[10px] text-text-muted block mt-0.5">Source: {evt.source}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-mono text-xs text-text-primary truncate max-w-md">{evt.action}</div>
                        <span className="font-mono text-[10px] text-accent-blue-light block mt-0.5">
                          Offset: {evt.byteOffset}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={<Eye className="w-3 h-3" />}
                          onClick={(e) => {
                            e.stopPropagation();
                            setInspectingEvent(evt);
                          }}
                        >
                          Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* SUBTAB 4: DETECTION ALERTS */}
      {activeSubTab === "detections" && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-status-critical" />
              Active Detection Rules & MITRE ATT&CK Alignments ({SAMPLE_DETECTIONS.length})
            </h3>
            <span className="text-xs text-text-muted">
              Zero false-positive algorithmic detection rules
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {SAMPLE_DETECTIONS.map((det) => (
              <div
                key={det.id}
                className="p-5 rounded-card border border-border-default bg-surface-primary hover:border-border-active transition-all shadow-sm flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-accent-cyan">{det.id}</span>
                      <Badge variant={det.severity === "critical" ? "critical" : "high"}>
                        {det.severity.toUpperCase()}
                      </Badge>
                      <Badge variant="informational">{det.stage}</Badge>
                    </div>
                    <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-surface-secondary text-text-muted border border-border-default">
                      {det.matchedCount} Triggered
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-text-primary">{det.name}</h4>

                  <div className="mt-2 flex items-center gap-2 text-xs font-mono">
                    <span className="px-2 py-0.5 rounded bg-accent-blue/15 text-accent-blue-light border border-accent-blue/30">
                      MITRE: {det.mitreId}
                    </span>
                    <span className="text-text-muted truncate">{det.mitreTechnique}</span>
                  </div>

                  <div className="mt-3 p-2.5 rounded bg-bg-primary border border-border-default text-xs font-mono text-accent-cyan overflow-x-auto">
                    <span className="text-[10px] text-text-muted uppercase block mb-1">Regex Pattern:</span>
                    <code>{det.pattern}</code>
                  </div>

                  <div className="mt-3 p-3 rounded-lg bg-surface-secondary border border-border-default text-xs">
                    <span className="text-[10px] font-mono font-bold text-status-success uppercase block mb-1">
                      Remediation Guidance:
                    </span>
                    <p className="text-text-secondary">{det.recommendation}</p>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-border-default flex items-center justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={<ExternalLink className="w-3.5 h-3.5" />}
                    onClick={() => setInspectingDetection(det)}
                  >
                    View Rule Spec
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUBTAB 5: FORENSIC FINDINGS */}
      {activeSubTab === "findings" && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-accent-cyan" />
              Confirmed Forensic Findings & Cryptographic Traceability ({findings.length})
            </h3>
            <span className="text-xs text-text-muted">
              Unbroken cryptographic verification from original log artifact to legal report
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
      )}

      {/* MODAL 1: ARTIFACT INSPECTOR */}
      {inspectingArtifact && (
        <Modal
          isOpen={!!inspectingArtifact}
          onClose={() => setInspectingArtifact(null)}
          title={`Artifact Inspector: ${inspectingArtifact.filename}`}
          description="Examining immutable forensic raw lines, byte offsets, and SHA-256 verification"
          maxWidth="xl"
        >
          <div className="space-y-4">
            {/* Artifact Specs Banner */}
            <div className="p-3.5 rounded-lg bg-surface-secondary border border-border-default grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-mono text-text-muted">Source Engine</span>
                <span className="font-bold text-text-primary block mt-0.5">{inspectingArtifact.source}</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono text-text-muted">File Size</span>
                <span className="font-mono text-text-primary block mt-0.5">{inspectingArtifact.size}</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono text-text-muted">Preservation Mode</span>
                <span className="font-mono text-status-success block mt-0.5">Read-Only (0440)</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-mono text-text-muted">Integrity State</span>
                <span className="font-mono text-accent-cyan font-bold block mt-0.5">
                  {verifiedArtifactHash ? "✓ VERIFIED 100%" : "PRISTINE"}
                </span>
              </div>
            </div>

            {/* SHA-256 Hash Card */}
            <div className="p-3 rounded-lg bg-bg-primary border border-border-default flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
              <div className="min-w-0">
                <span className="text-[10px] text-text-muted uppercase block">Cryptographic SHA-256 Digest:</span>
                <span className="text-accent-cyan font-bold break-all select-all">{inspectingArtifact.sha256}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<Copy className="w-3 h-3" />}
                  onClick={() => handleCopyHash(inspectingArtifact.sha256)}
                >
                  {copiedHash ? "Copied!" : "Copy Hash"}
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  icon={<CheckCircle2 className="w-3 h-3" />}
                  onClick={() => setVerifiedArtifactHash(inspectingArtifact.sha256)}
                >
                  Verify Integrity
                </Button>
              </div>
            </div>

            {/* Raw Log Viewer with Byte Offsets */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-xs font-mono font-bold uppercase text-text-muted flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-accent-cyan" />
                  Preserved Raw Stream & Byte Offsets
                </h4>
                <div className="w-64">
                  <Input
                    placeholder="Filter log lines..."
                    value={artifactSearchQuery}
                    onChange={(e) => setArtifactSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              <div className="bg-bg-primary border border-border-default rounded-lg p-3 font-mono text-[11px] max-h-72 overflow-y-auto space-y-1.5">
                {inspectingArtifact.rawSample
                  .filter((l) => !artifactSearchQuery || l.toLowerCase().includes(artifactSearchQuery.toLowerCase()))
                  .map((line, idx) => {
                    const startOffset = idx * 128;
                    const endOffset = startOffset + line.length;
                    const hexOffset = `[0x${startOffset.toString(16).padStart(8, "0")} - 0x${endOffset.toString(16).padStart(8, "0")}]`;
                    const isMalicious =
                      line.includes("passwd") ||
                      line.includes("POISON") ||
                      line.includes("whoami") ||
                      line.includes("/tmp/bin") ||
                      line.includes("sudo");

                    return (
                      <div
                        key={idx}
                        className={`p-1.5 rounded flex items-start gap-2.5 transition-colors ${
                          isMalicious
                            ? "bg-status-critical/10 border border-status-critical/30 text-text-primary"
                            : "hover:bg-surface-secondary text-text-secondary"
                        }`}
                      >
                        <span className="text-[10px] text-accent-blue-light select-none shrink-0 font-bold">
                          {hexOffset}
                        </span>
                        <span className="text-[10px] text-text-muted select-none shrink-0">L{idx + 1}</span>
                        <span className="break-all">{line}</span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* MODAL 2: EVENT DETAILS */}
      {inspectingEvent && (
        <Modal
          isOpen={!!inspectingEvent}
          onClose={() => setInspectingEvent(null)}
          title={`Forensic Event Inspection: ${inspectingEvent.id}`}
          description="Detailed breakdown of normalized parameters and exact source telemetry references"
          maxWidth="lg"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-[10px] text-text-muted uppercase block">Event Timestamp</span>
                <span className="text-text-primary font-bold">{inspectingEvent.timestamp}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-[10px] text-text-muted uppercase block">Attack Stage</span>
                <span className="text-accent-cyan font-bold">{inspectingEvent.stage}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-[10px] text-text-muted uppercase block">Actor IP Address</span>
                <span className="text-text-primary font-bold">{inspectingEvent.actorIp}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-[10px] text-text-muted uppercase block">Byte Offset Span</span>
                <span className="text-status-success font-bold">{inspectingEvent.byteOffset}</span>
              </div>
            </div>

            <div>
              <span className="text-[10px] font-mono uppercase text-text-muted block mb-1">Target Action</span>
              <div className="p-3 rounded bg-surface-secondary border border-border-default text-xs font-mono text-text-primary">
                {inspectingEvent.action}
              </div>
            </div>

            <div>
              <span className="text-[10px] font-mono uppercase text-text-muted block mb-1">Raw Payload</span>
              <div className="p-3 rounded bg-bg-primary border border-border-default text-xs font-mono text-accent-cyan break-all">
                {inspectingEvent.payload}
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* MODAL 3: DETECTION RULE SPEC */}
      {inspectingDetection && (
        <Modal
          isOpen={!!inspectingDetection}
          onClose={() => setInspectingDetection(null)}
          title={`Detection Rule Specification: ${inspectingDetection.id}`}
          description={inspectingDetection.name}
          maxWidth="lg"
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 rounded bg-surface-secondary border border-border-default flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-text-muted block">MITRE ATT&CK Matrix</span>
                <span className="font-bold text-accent-cyan text-sm">{inspectingDetection.mitreId}: {inspectingDetection.mitreTechnique}</span>
              </div>
              <Badge variant={inspectingDetection.severity === "critical" ? "critical" : "high"}>
                {inspectingDetection.severity.toUpperCase()}
              </Badge>
            </div>

            <div className="p-3 rounded bg-bg-primary border border-border-default font-mono">
              <span className="text-[10px] text-text-muted uppercase block mb-1">Rule Regex Engine:</span>
              <code className="text-accent-cyan">{inspectingDetection.pattern}</code>
            </div>

            <div className="p-3 rounded bg-surface-secondary border border-border-default">
              <span className="text-[10px] font-mono uppercase text-status-success font-bold block mb-1">
                Prescribed Mitigation Directive:
              </span>
              <p className="text-text-secondary leading-relaxed">{inspectingDetection.recommendation}</p>
            </div>
          </div>
        </Modal>
      )}

      {/* MODAL 4: CRITICAL TRACEABILITY INSPECTOR */}
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
