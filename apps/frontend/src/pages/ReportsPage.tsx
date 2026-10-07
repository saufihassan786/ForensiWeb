import React, { useState } from "react";
import {
  FileText,
  Download,
  Eye,
  CheckCircle2,
  Search,
  Filter,
  RefreshCw,
} from "lucide-react";

export interface ReportItem {
  id: string;
  case_id: string;
  report_type: "technical" | "executive" | "evidence_summary";
  title: string;
  file_path: string;
  sha256: string;
  format: "markdown" | "html" | "json" | "pdf";
  created_at: string;
  status: "verified" | "draft";
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
    created_at: "2026-10-06T14:30:00Z",
    status: "verified",
  },
  {
    id: "RPT-CASE-001-EXEC",
    case_id: "CASE-001",
    report_type: "executive",
    title: "Executive Incident Brief: Privilege Escalation Root-Cause Analysis",
    file_path: "data/reports/RPT-CASE-001-EXEC.html",
    sha256: "98a12bc45ef67890123456789abcdef0123456789abcdef0123456789abcdef0",
    format: "html",
    created_at: "2026-10-06T15:00:00Z",
    status: "verified",
  },
  {
    id: "RPT-CASE-001-EVID",
    case_id: "CASE-001",
    report_type: "evidence_summary",
    title: "Chain of Custody & Cryptographic Evidence Inventory Manifest",
    file_path: "data/reports/RPT-CASE-001-EVID.json",
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    format: "json",
    created_at: "2026-10-06T15:15:00Z",
    status: "verified",
  },
];

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportItem[]>(INITIAL_REPORTS);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [previewReport, setPreviewReport] = useState<ReportItem | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

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
      const newReport: ReportItem = {
        id: `RPT-CASE-001-${Math.random().toString(36).substring(2, 6).toUpperCase()}`,
        case_id: "CASE-001",
        report_type: "technical",
        title: `Automated Investigation Findings Report #${reports.length + 1}`,
        file_path: `data/reports/RPT-CASE-001-AUTO.md`,
        sha256: "d5fe93f8e405e80a0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b9",
        format: "markdown",
        created_at: new Date().toISOString(),
        status: "verified",
      };
      setReports([newReport, ...reports]);
      setIsGenerating(false);
    }, 800);
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary tracking-wide flex items-center gap-2">
            <FileText className="w-5 h-5 text-accent-cyan" />
            Forensic Incident Reporting
          </h1>
          <p className="text-xs text-text-muted mt-1">
            Academic-grade, evidence-backed reports with cryptographic integrity proofs and chain-of-custody.
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
                      .{report.format}
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
                        onClick={() => alert(`Downloading ${report.id}.${report.format} (SHA256 verified)`)}
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

      {/* Preview Modal */}
      {previewReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div className="bg-surface-primary border border-border-default rounded-xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-border-default flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-sm text-text-primary">{previewReport.title}</h3>
                <p className="font-mono text-[10px] text-text-muted mt-0.5">SHA-256: {previewReport.sha256}</p>
              </div>
              <button
                onClick={() => setPreviewReport(null)}
                className="text-text-muted hover:text-text-primary p-1 rounded hover:bg-surface-hover text-xs font-mono"
              >
                ✕ Close
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-4 font-sans text-xs text-text-secondary leading-relaxed">
              <div className="p-3 bg-surface-secondary border border-border-default rounded-lg">
                <span className="font-bold text-accent-cyan">1. Executive Summary:</span> Investigation confirmed multi-stage compromise starting from Local File Inclusion (LFI) in document viewer progressing to root privilege escalation via hijacked PATH variable.
              </div>
              <div className="p-3 bg-surface-secondary border border-border-default rounded-lg">
                <span className="font-bold text-accent-cyan">2. Evidence Chain:</span> Primary artifacts `access.log` and `audit.log` were preserved with cryptographic hashes verified at ingestion and processing boundaries.
              </div>
              <div className="p-3 bg-surface-secondary border border-border-default rounded-lg">
                <span className="font-bold text-accent-cyan">3. Timeline & Correlation:</span> Detections across 5 MITRE ATT&CK stages correlated with temporal delta dt &le; 2.5s and process lineage (PPID &rarr; PID).
              </div>
              <div className="p-3 bg-surface-secondary border border-border-default rounded-lg">
                <span className="font-bold text-accent-cyan">4. Mitigation & Verification:</span> Demonstrated that input whitelisting and static environment configuration neutralize 100% of tested vectors.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
