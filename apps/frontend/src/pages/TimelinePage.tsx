import React, { useEffect, useState } from "react";
import { Badge } from "@/components/common/Badge";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { apiService } from "@/services/api";
import { AttackChainGraph, TimelineEntry } from "@/types/api";
import {
  ArrowRight,
  Clock,
  ExternalLink,
  GitBranch,
  Search,
  Zap,
} from "lucide-react";

export interface TimelinePageProps {
  onOpenSimulator?: () => void;
}

export const TimelinePage: React.FC<TimelinePageProps> = ({ onOpenSimulator }) => {
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [graph, setGraph] = useState<AttackChainGraph | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<TimelineEntry | null>(null);
  const [filterStage, setFilterStage] = useState<string>("ALL");
  const [filterClass, setFilterClass] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [viewMode, setViewMode] = useState<"timeline" | "graph">("timeline");

  useEffect(() => {
    apiService.getTimeline().then(setTimeline);
    apiService.getAttackChainGraph().then(setGraph);
  }, []);

  const filteredEntries = timeline.filter((entry) => {
    if (filterStage !== "ALL" && !entry.attack_stage.includes(filterStage)) {
      return false;
    }
    if (filterClass !== "ALL" && entry.classification !== filterClass) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const match =
        entry.title.toLowerCase().includes(q) ||
        entry.summary.toLowerCase().includes(q) ||
        entry.attack_stage.toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-card border border-border-default bg-surface-primary shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="verified" dot>CHRONOLOGICAL TIMELINE ENGINE</Badge>
            <Badge variant="informational">ISO/IEC 27037 FIDELITY</Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-text-primary">
            Incident Attack Timeline & Progression Graph
          </h2>
          <p className="text-xs text-text-secondary mt-1">
            Reconstruct and trace the sequential attack progression from initial reconnaissance through privilege escalation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === "timeline" ? "primary" : "secondary"}
            size="sm"
            icon={<Clock className="w-3.5 h-3.5" />}
            onClick={() => setViewMode("timeline")}
          >
            Chronological View
          </Button>
          <Button
            variant={viewMode === "graph" ? "primary" : "secondary"}
            size="sm"
            icon={<GitBranch className="w-3.5 h-3.5" />}
            onClick={() => setViewMode("graph")}
          >
            Attack Chain Graph
          </Button>
          {onOpenSimulator && (
            <Button
              variant="primary"
              size="sm"
              icon={<Zap className="w-3.5 h-3.5" />}
              onClick={onOpenSimulator}
            >
              Simulate Attack
            </Button>
          )}
        </div>
      </div>

      {/* Stage Progression Bar */}
      <Card title="Attack Sequence Progression (MITRE ATT&CK Mapping)">
        <div className="flex flex-wrap items-center gap-2">
          {["RECON", "LFI", "LOG_POISONING", "RCE", "PRIVILEGE_ESCALATION"].map((stg, i, arr) => {
            const isActive = filterStage === stg;
            return (
              <React.Fragment key={stg}>
                <button
                  type="button"
                  onClick={() => setFilterStage(filterStage === stg ? "ALL" : stg)}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-medium transition-all flex items-center gap-1.5 ${
                    isActive
                      ? "bg-accent-blue/20 border-accent-blue text-accent-cyan shadow-sm"
                      : "bg-surface-secondary border-border-default text-text-secondary hover:border-border-active hover:text-text-primary"
                  }`}
                >
                  <span className="text-[10px] text-text-muted">0{i + 1}.</span>
                  {stg.replace("_", " ")}
                </button>
                {i < arr.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-text-muted" />}
              </React.Fragment>
            );
          })}
        </div>
      </Card>

      {/* Filter Toolbar */}
      <div className="flex flex-col md:flex-row items-center gap-3">
        <div className="flex-1 w-full">
          <Input
            placeholder="Search milestone headline, payload, or actor IP..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leadingIcon={<Search className="w-4 h-4" />}
          />
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            value={filterClass}
            onChange={(e) => setFilterClass(e.target.value)}
            className="px-3 py-2 rounded-lg bg-surface-primary border border-border-default text-xs text-text-primary focus:outline-none focus:border-accent-blue"
          >
            <option value="ALL">All Classifications</option>
            <option value="Observed">Observed (Direct telemetry)</option>
            <option value="Likely">Likely (Strong rule match)</option>
            <option value="Correlated">Correlated (Cross-source)</option>
            <option value="Inferred">Inferred (Hypothesized)</option>
          </select>
          {(filterStage !== "ALL" || filterClass !== "ALL" || searchQuery) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setFilterStage("ALL");
                setFilterClass("ALL");
                setSearchQuery("");
              }}
            >
              Reset Filters
            </Button>
          )}
        </div>
      </div>

      {/* View Mode: Timeline */}
      {viewMode === "timeline" && (
        <div className="space-y-4">
          {filteredEntries.map((entry) => {
            const classColor =
              entry.classification === "Observed"
                ? "verified"
                : entry.classification === "Likely"
                ? "high"
                : entry.classification === "Correlated"
                ? "informational"
                : "medium";

            return (
              <div
                key={entry.id}
                onClick={() => setSelectedEntry(entry)}
                className="p-5 rounded-card border border-border-default bg-surface-primary hover:border-accent-blue/50 cursor-pointer transition-all shadow-sm group"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-accent-cyan">
                      #{entry.order_index.toString().padStart(2, "0")}
                    </span>
                    <span className="text-xs font-mono text-text-muted flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(entry.timestamp).toISOString().replace("T", " ").replace("Z", " UTC")}
                    </span>
                    <Badge variant={entry.attack_stage.includes("PRIV") || entry.attack_stage.includes("RCE") ? "critical" : "high"}>
                      {entry.attack_stage}
                    </Badge>
                    <Badge variant={classColor as any} dot>
                      {entry.classification.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-text-muted">
                      Confidence: {Math.round(entry.confidence * 100)}%
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<ExternalLink className="w-3 h-3" />}
                      onClick={() => setSelectedEntry(entry)}
                    >
                      Drill Down
                    </Button>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-text-primary">{entry.title}</h3>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">{entry.summary}</p>

                {/* Evidence & Metadata Footer */}
                <div className="mt-3 pt-3 border-t border-border-default/50 flex flex-wrap items-center justify-between text-[11px] font-mono text-text-muted gap-2">
                  <div className="flex items-center gap-3">
                    <span>Evidence: {entry.evidence_references.join(", ") || "manifest_indexed"}</span>
                    <span>Events: {entry.event_ids.join(", ")}</span>
                  </div>
                  {entry.metadata && (
                    <div className="flex items-center gap-2 text-accent-cyan">
                      {Object.entries(entry.metadata).slice(0, 2).map(([k, v]) => (
                        <span key={k}>
                          {k}: {String(v)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* View Mode: Graph */}
      {viewMode === "graph" && graph && (
        <Card title="Directed Attack Chain Graph (Causal & Chronological Flow)">
          <div className="space-y-6">
            <div className="p-4 rounded-lg bg-surface-secondary border border-border-default flex flex-wrap items-center justify-between gap-4 text-xs">
              <div>
                <span className="text-text-muted">Root Cause Entrypoint: </span>
                <span className="font-mono text-accent-cyan font-bold">{graph.root_causes[0]} (Recon/LFI)</span>
              </div>
              <div>
                <span className="text-text-muted">Terminal Impact: </span>
                <span className="font-mono text-status-critical font-bold">{graph.terminal_impacts[0]} (Privilege Escalation)</span>
              </div>
              <div>
                <span className="text-text-muted">Overall Graph Confidence: </span>
                <span className="font-mono text-status-success font-bold">{Math.round(graph.overall_confidence * 100)}%</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
              {graph.nodes.map((node, i) => (
                <div
                  key={node.id}
                  className="p-4 rounded-card border border-border-default bg-surface-primary hover:border-accent-blue transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono text-accent-cyan font-bold">NODE 0{i + 1}</span>
                      <Badge variant={node.classification === "Observed" ? "verified" : "informational"}>
                        {node.classification}
                      </Badge>
                    </div>
                    <h4 className="text-xs font-bold text-text-primary">{node.label}</h4>
                    <p className="text-[11px] text-text-muted mt-1 leading-snug">
                      {new Date(node.timestamp).toLocaleTimeString()} UTC
                    </p>
                  </div>
                  <div className="mt-4 pt-2 border-t border-border-default/50 text-[10px] font-mono text-text-muted">
                    Confidence: {Math.round(node.confidence * 100)}%
                  </div>
                </div>
              ))}
            </div>

            {/* Edge Relationships */}
            <div className="space-y-2 mt-4">
              <h4 className="text-xs font-mono font-bold uppercase text-text-muted">
                Identified Causal & Sequential Edges
              </h4>
              <div className="space-y-2">
                {graph.edges.map((edge, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg border border-border-default bg-surface-secondary flex flex-col md:flex-row md:items-center justify-between text-xs gap-2"
                  >
                    <div className="flex items-center gap-2 font-mono">
                      <span className="text-accent-cyan font-bold">{edge.source_id}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-text-muted" />
                      <span className="text-status-critical font-bold">{edge.target_id}</span>
                      <Badge variant="informational">{edge.relation_type.toUpperCase()}</Badge>
                    </div>
                    <p className="text-text-secondary text-[11px] max-w-xl">{edge.explanation}</p>
                    <span className="text-[10px] font-mono text-text-muted whitespace-nowrap">
                      Conf: {Math.round(edge.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Drill-Down Modal */}
      {selectedEntry && (
        <Modal
          isOpen={!!selectedEntry}
          onClose={() => setSelectedEntry(null)}
          title={`Forensic Drill-Down: ${selectedEntry.id}`}
          description={`Examining supporting normalized events and exact byte offsets for ${selectedEntry.title}`}
          maxWidth="xl"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-text-muted block text-[10px] uppercase font-mono">Timestamp</span>
                <span className="font-mono text-text-primary">{selectedEntry.timestamp}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-text-muted block text-[10px] uppercase font-mono">Attack Stage</span>
                <span className="font-mono text-accent-cyan font-bold">{selectedEntry.attack_stage}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-text-muted block text-[10px] uppercase font-mono">Classification</span>
                <span className="font-mono text-text-primary">{selectedEntry.classification}</span>
              </div>
              <div className="p-3 rounded bg-surface-secondary border border-border-default">
                <span className="text-text-muted block text-[10px] uppercase font-mono">Confidence</span>
                <span className="font-mono text-status-success">{Math.round(selectedEntry.confidence * 100)}%</span>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono font-bold uppercase text-text-muted mb-1.5">
                Analytical Summary
              </h4>
              <p className="text-xs text-text-secondary p-3 rounded bg-surface-secondary border border-border-default leading-relaxed">
                {selectedEntry.summary}
              </p>
            </div>

            <div>
              <h4 className="text-xs font-mono font-bold uppercase text-text-muted mb-1.5">
                Contextual Metadata & Evidence Source
              </h4>
              <pre className="p-3 rounded bg-bg-primary border border-border-default font-mono text-xs text-accent-cyan overflow-x-auto">
                {JSON.stringify(
                  {
                    evidence_files: selectedEntry.evidence_references,
                    event_ids: selectedEntry.event_ids,
                    detections: selectedEntry.detection_ids,
                    context: selectedEntry.metadata,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
