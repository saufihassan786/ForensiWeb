import React, { useState } from "react";
import {
  FileText,
  Download,
  Eye,
  CheckCircle2,
  Search,
  Filter,
  RefreshCw,
  Copy,
  Check,
} from "lucide-react";

export interface ReportItem {
  id: string;
  case_id: string;
  report_type: "technical" | "executive" | "evidence_summary" | "mitre_matrix";
  title: string;
  file_path: string;
  sha256: string;
  format: "markdown" | "html" | "json";
  created_at: string;
  status: "verified" | "draft";
  content?: string;
}

const INITIAL_REPORTS: ReportItem[] = [
  {
    id: "RPT-CASE-001-TECH",
    case_id: "CASE-001",
    report_type: "technical",
    title: "Comprehensive Digital Forensics Technical Report — LFI to PrivEsc",
    file_path: "data/reports/RPT-CASE-001-TECH.md",
    sha256: "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    format: "markdown",
    created_at: "2026-10-07T14:30:00Z",
    status: "verified",
    content: `# DIGITAL FORENSICS INVESTIGATION REPORT: CASE-001
**Case Title:** Controlled LFI-to-Privilege-Escalation Investigation  
**Forensic Standard:** ISO/IEC 27037:2012 Guidelines for handling digital evidence  
**Date:** 2026-10-07  
**Lead Investigator:** Digital Forensics Incident Response (DFIR) Unit  

---

## 1. Executive Summary
Between 10:00:00 UTC and 10:12:00 UTC on 2026-10-07, a 5-stage progressive cyber attack was conducted against the target environment (Flask/Apache on Linux). The intrusion advanced from reconnaissance into Local File Inclusion (LFI), log header poisoning, command execution, and host privilege escalation to root (UID 0).

## 2. Preserved Evidence Manifest
All acquired files were hashed at acquisition time and verified:
- \`access.log\`: SHA-256 = \`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\` (14.2 KB)
- \`app_error.log\`: SHA-256 = \`8729837492837492837498237498237498237498237498237498237498237498\` (8.6 KB)
- \`audit.log\`: SHA-256 = \`5938475938475938475938475938475938475938475938475938475938475938\` (32.1 KB)

## 3. Reconstructed Attack Timeline & MITRE ATT&CK Matrix
1. **[T1083] Recon & LFI Probe:** IP 172.28.0.5 issued directory traversal query \`../../../../etc/passwd\` via \`/view?page=\`.
2. **[T1059.004] Log Poisoning:** Attacker sent raw PHP execution token inside User-Agent header into access.log.
3. **[T1505.003] Log Inclusion RCE:** Attacker requested \`/view?page=../../var/log/apache2/access.log&cmd=whoami\`, executing code under \`www-data\` (UID 33).
4. **[T1548.001] Privilege Escalation:** Sudoers permitted unprivileged execution of \`/opt/check_update\`. Insecure \`PATH\` allowed execution of malicious \`/tmp/bin/curl\` resulting in root compromise (UID 0).

## 4. Verification of Defensive Mitigations
Applying strict parameter basename allowlisting and enforcing \`Defaults secure_path\` in \`/etc/sudoers\` blocked 100% of attack stages.
`,
  },
  {
    id: "RPT-CASE-001-EXEC",
    case_id: "CASE-001",
    report_type: "executive",
    title: "Executive Incident Brief: Privilege Escalation Root-Cause Analysis",
    file_path: "data/reports/RPT-CASE-001-EXEC.html",
    sha256: "98a12bc45ef67890123456789abcdef0123456789abcdef0123456789abcdef0",
    format: "html",
    created_at: "2026-10-07T15:00:00Z",
    status: "verified",
    content: `<!DOCTYPE html>
<html>
<head><title>Executive Brief: CASE-001</title></head>
<body style="font-family: sans-serif; padding: 20px; line-height: 1.6;">
  <h1>Executive Summary: Incident CASE-001</h1>
  <p><strong>Impact Level:</strong> High (Full Root Compromise in Container)</p>
  <p><strong>Root Cause:</strong> Unsanitized input parameter combined with insecure sudo PATH configuration.</p>
  <p><strong>Remediation Status:</strong> Remediated and verified with 100% block rate.</p>
</body>
</html>`,
  },
  {
    id: "RPT-CASE-001-EVID",
    case_id: "CASE-001",
    report_type: "evidence_summary",
    title: "Chain of Custody & Cryptographic Evidence Inventory Manifest",
    file_path: "data/reports/RPT-CASE-001-EVID.json",
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    format: "json",
    created_at: "2026-10-07T15:15:00Z",
    status: "verified",
    content: JSON.stringify(
      {
        manifest_version: "1.0",
        case_id: "CASE-001",
        chain_of_custody_verified: true,
        artifacts: [
          {
            name: "access.log",
            sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            source: "apache2",
            mode: "0440",
          },
          {
            name: "audit.log",
            sha256: "5938475938475938475938475938475938475938475938475938475938475938",
            source: "auditd",
            mode: "0440",
          },
        ],
      },
      null,
      2
    ),
  },
];

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>(INITIAL_REPORTS);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [previewReport, setPreviewReport] = useState<ReportItem | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedText, setCopiedText] = useState(false);
  const [downloadNotification, setDownloadNotification] = useState<string | null>(null);

  const filteredReports = reports.filter((r) => {
    const matchesSearch =
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.sha256.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === "all" || r.report_type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleGenerateReport = () => {
    setIsGenerating(true);
    setTimeout(() => {
      const reportTypes: Array<"technical" | "executive" | "evidence_summary" | "mitre_matrix"> = [
        "technical",
        "executive",
        "evidence_summary",
        "mitre_matrix",
      ];
      const randomType = reportTypes[Math.floor(Math.random() * reportTypes.length)];
      const randHex = Math.random().toString(36).substring(2, 6).toUpperCase();
      const ext = randomType === "executive" ? "html" : randomType === "evidence_summary" ? "json" : "md";

      const newReport: ReportItem = {
        id: `RPT-CASE-001-${randHex}`,
        case_id: "CASE-001",
        report_type: randomType,
        title: `Automated Investigation Findings Report #${reports.length + 1} (${randomType.toUpperCase()})`,
        file_path: `data/reports/RPT-CASE-001-${randHex}.${ext}`,
        sha256: "d5fe93f8e405e80a0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b9",
        format: ext as any,
        created_at: new Date().toISOString(),
        status: "verified",
        content: `# AUTOMATED FORENSIC REPORT: RPT-CASE-001-${randHex}\n**Case:** CASE-001\n**Timestamp:** ${new Date().toISOString()}\n**Integrity:** Verified SHA-256 Digest\n\nAll forensic evidence artifacts preserved with unbroken cryptographic traceability.`,
      };
      setReports([newReport, ...reports]);
      setIsGenerating(false);
    }, 700);
  };

  const handleDownloadReport = (report: ReportItem) => {
    const content = report.content || `# ${report.title}\n\nCase: ${report.case_id}\nSHA-256: ${report.sha256}\n\nForensic investigation artifact exported from ForensiWeb Platform.`;
    const mimeTypes: Record<string, string> = {
      markdown: "text/markdown;charset=utf-8",
      html: "text/html;charset=utf-8",
      json: "application/json;charset=utf-8",
    };
    const mime = mimeTypes[report.format] || "text/plain";
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${report.id}.${report.format === "markdown" ? "md" : report.format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setDownloadNotification(`Downloaded ${report.id} (SHA-256 verified)`);
    setTimeout(() => setDownloadNotification(null), 3000);
  };

  const handleCopyContent = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Download Alert Toast */}
      {downloadNotification && (
        <div className="fixed top-5 right-5 z-50 p-3.5 rounded-lg bg-surface-primary border border-status-success/50 shadow-glow-cyan text-xs text-text-primary flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-status-success flex-shrink-0" />
          <span>{downloadNotification}</span>
        </div>
      )}

      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-card border border-border-default bg-surface-primary shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-text-primary tracking-wide flex items-center gap-2">
            <FileText className="w-5 h-5 text-accent-cyan" />
            Investigation Reports
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Export forensic summaries and evidence reports.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="flex items-center gap-2 px-4 py-2 bg-accent-blue hover:bg-accent-blue-light text-white text-xs font-semibold rounded-lg shadow-glow-blue transition-all duration-150 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isGenerating ? "animate-spin" : ""}`} />
            <span>{isGenerating ? "Compiling Report..." : "Generate New Report"}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-text-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title, ID, or SHA-256 hash..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-primary border border-border-default rounded-lg pl-9 pr-3 py-2 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-border-active focus:ring-1 focus:ring-accent-blue"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-text-muted" />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-surface-primary border border-border-default rounded-lg px-3 py-2 text-xs text-text-primary focus:outline-none focus:border-border-active"
          >
            <option value="all">All Report Types</option>
            <option value="technical">Technical Investigation</option>
            <option value="executive">Executive Summary</option>
            <option value="evidence_summary">Evidence Inventory</option>
            <option value="mitre_matrix">MITRE Matrix</option>
          </select>
        </div>
      </div>

      {/* Reports Table */}
      <div className="bg-surface-primary border border-border-default rounded-xl overflow-hidden shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-secondary border-b border-border-default text-text-muted uppercase text-[10px] font-mono tracking-wider">
              <tr>
                <th className="py-3 px-4">Document Details</th>
                <th className="py-3 px-4">Type & Format</th>
                <th className="py-3 px-4">Cryptographic Hash (SHA-256)</th>
                <th className="py-3 px-4">Generated (UTC)</th>
                <th className="py-3 px-4">Verification</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-default text-text-secondary">
              {filteredReports.map((report) => (
                <tr key={report.id} className="hover:bg-surface-hover/50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-medium text-text-primary">{report.title}</div>
                    <div className="font-mono text-[10px] text-accent-cyan mt-0.5">{report.id}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-accent-blue/15 text-accent-blue-light border border-accent-blue/30 uppercase">
                      {report.report_type.replace("_", " ")}
                    </span>
                    <span className="ml-1.5 text-[10px] font-mono text-text-muted uppercase">
                      .{report.format === "markdown" ? "md" : report.format}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-[10px] text-text-muted max-w-[200px] truncate" title={report.sha256}>
                    {report.sha256}
                  </td>
                  <td className="py-3 px-4 font-mono text-[11px] text-text-muted">
                    {new Date(report.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-status-success">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Verified
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        onClick={() => setPreviewReport(report)}
                        className="p-1.5 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-text-primary hover:text-accent-cyan transition-colors"
                        title="Preview Report"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDownloadReport(report)}
                        className="p-1.5 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-text-primary hover:text-accent-cyan transition-colors"
                        title="Download Artifact"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interactive Preview Modal */}
      {previewReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="bg-surface-primary border border-border-default rounded-xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-4 border-b border-border-default flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-sm text-text-primary">{previewReport.title}</h3>
                <p className="font-mono text-[10px] text-accent-cyan mt-0.5 select-all">SHA-256: {previewReport.sha256}</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopyContent(previewReport.content || previewReport.title)}
                  className="px-2.5 py-1 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-xs font-mono text-text-primary flex items-center gap-1.5"
                >
                  {copiedText ? <Check className="w-3 h-3 text-status-success" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedText ? "Copied" : "Copy"}</span>
                </button>
                <button
                  onClick={() => handleDownloadReport(previewReport)}
                  className="px-2.5 py-1 rounded bg-accent-blue hover:bg-accent-blue-light text-white text-xs font-mono flex items-center gap-1.5"
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => setPreviewReport(null)}
                  className="text-text-muted hover:text-text-primary p-1 rounded hover:bg-surface-hover text-xs font-mono ml-2"
                >
                  ✕ Close
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 font-mono text-xs text-text-secondary leading-relaxed bg-bg-primary">
              <pre className="whitespace-pre-wrap font-mono text-xs text-text-primary">
                {previewReport.content || `Report ID: ${previewReport.id}\nNo custom content loaded.`}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
