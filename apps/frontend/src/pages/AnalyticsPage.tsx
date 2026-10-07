import React, { useEffect, useState } from "react";
import { Badge } from "@/components/common/Badge";
import { Card } from "@/components/common/Card";
import { MetricCard } from "@/components/common/MetricCard";
import { apiService } from "@/services/api";
import { DashboardAnalytics } from "@/types/api";
import {
  Activity,
  AlertOctagon,
  Database,
  FileCheck,
} from "lucide-react";

export const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);

  useEffect(() => {
    apiService.getAnalytics().then(setAnalytics);
  }, []);

  if (!analytics) {
    return (
      <div className="py-12 text-center text-xs text-text-muted animate-pulse">
        Aggregating system analytics and calculating risk model...
      </div>
    );
  }

  const {
    case_overview,
    evidence_metrics,
    event_metrics,
    detection_metrics,
    finding_metrics,
    event_trends,
    severity_distribution,
    attack_stage_analytics,
    risk_summary,
  } = analytics;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-card border border-border-default bg-surface-primary shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="verified" dot>ANALYTICS ENGINE (PHASE-13)</Badge>
            <Badge variant="informational">{case_overview.case_id}</Badge>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-text-primary">
            {case_overview.title}
          </h2>
          <p className="text-xs text-text-secondary mt-1">
            Real-time evidence telemetry, attack-stage progression metrics, and deterministic risk score attribution.
          </p>
        </div>
      </div>

      {/* High-Level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Evidence Artifacts"
          value={evidence_metrics.total_artifacts.toString()}
          trend={{ value: `${evidence_metrics.verified_hashes} Verified`, isPositive: true }}
          variant="cyan"
          icon={<Database className="w-5 h-5 text-accent-cyan" />}
        />
        <MetricCard
          label="Normalized Events"
          value={event_metrics.total_events.toString()}
          trend={{ value: "ISO-8601 UTC", isPositive: true }}
          variant="blue"
          icon={<Activity className="w-5 h-5 text-accent-blue" />}
        />
        <MetricCard
          label="Security Detections"
          value={detection_metrics.total_alerts.toString()}
          trend={{ value: `${detection_metrics.by_severity.critical || 0} Critical`, isPositive: false }}
          variant="critical"
          icon={<AlertOctagon className="w-5 h-5 text-status-critical" />}
        />
        <MetricCard
          label="Confirmed Findings"
          value={finding_metrics.total_findings.toString()}
          trend={{ value: `${finding_metrics.mitigated_count} Mitigated`, isPositive: true }}
          variant="violet"
          icon={<FileCheck className="w-5 h-5 text-accent-violet" />}
        />
      </div>

      {/* Explainable Risk Summary Gauge Card */}
      <Card
        title="Explainable Incident Risk Score (PHASE-13-F10)"
        subtitle="Deterministic risk score computed strictly from verified attack stage, critical detections, and unmitigated findings"
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          {/* Risk Score Dial */}
          <div className="p-6 rounded-card bg-surface-secondary border border-border-default flex flex-col items-center justify-center text-center">
            <div className="w-28 h-28 rounded-full border-4 border-status-critical/30 flex flex-col items-center justify-center relative shadow-glow-critical">
              <span className="text-3xl font-bold font-mono text-status-critical">
                {risk_summary.risk_score}
              </span>
              <span className="text-[10px] font-mono text-text-muted uppercase">/ 100</span>
            </div>
            <div className="mt-3">
              <Badge variant="critical" dot>
                {risk_summary.risk_level} RISK LEVEL
              </Badge>
            </div>
            <p className="text-[11px] text-text-muted mt-2 max-w-xs">
              Direct evidence confirms arbitrary code execution and privileged credential compromise.
            </p>
          </div>

          {/* Factor Breakdown */}
          <div className="lg:col-span-2 space-y-2.5">
            <h4 className="text-xs font-mono font-bold uppercase text-text-muted mb-2">
              Contributing Risk Factors & Deductive Attribution
            </h4>
            {risk_summary.explanation_factors.map((factor, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg border border-border-default bg-surface-secondary flex items-center justify-between text-xs gap-3"
              >
                <div>
                  <span className="font-mono font-bold text-text-primary block text-[11px]">
                    {factor.factor}
                  </span>
                  <span className="text-text-secondary text-[11px] mt-0.5 block">
                    {factor.rationale}
                  </span>
                </div>
                <span
                  className={`font-mono font-bold whitespace-nowrap text-xs px-2.5 py-1 rounded ${
                    factor.points > 0
                      ? "bg-status-critical/15 text-status-critical border border-status-critical/30"
                      : "bg-status-success/15 text-status-success border border-status-success/30"
                  }`}
                >
                  {factor.points > 0 ? `+${factor.points} pts` : "0 pts"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Attack Stage Progression & Severity Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stage Progression */}
        <Card title="Attack-Stage Progression Analytics (PHASE-13-F08)">
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-muted font-mono">Chain Completion</span>
              <span className="font-mono font-bold text-accent-cyan">
                {attack_stage_analytics.sequence_completion_percent}%
              </span>
            </div>
            <div className="w-full h-2.5 bg-bg-primary rounded-full overflow-hidden border border-border-default">
              <div
                className="h-full bg-gradient-to-r from-accent-blue via-accent-cyan to-status-critical rounded-full transition-all duration-500"
                style={{ width: `${attack_stage_analytics.sequence_completion_percent}%` }}
              />
            </div>
            <div className="p-3 rounded-lg bg-surface-secondary border border-border-default text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-text-muted">Highest Stage Verified:</span>
                <span className="font-mono font-bold text-status-critical">
                  {attack_stage_analytics.highest_stage_reached}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Verified Progression Stages:</span>
                <span className="font-mono text-accent-cyan">
                  {attack_stage_analytics.stages_detected.length} / 5 Stages
                </span>
              </div>
            </div>
          </div>
        </Card>

        {/* Severity Distribution */}
        <Card title="Severity Distribution (PHASE-13-F07)">
          <div className="space-y-3">
            {Object.entries(severity_distribution.counts).map(([sev, count]) => {
              const pct = severity_distribution.percentages[sev] || 0;
              const colorClass =
                sev === "critical"
                  ? "bg-status-critical"
                  : sev === "high"
                  ? "bg-status-high"
                  : sev === "medium"
                  ? "bg-status-medium"
                  : "bg-status-low";

              return (
                <div key={sev} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="uppercase text-text-primary font-bold">{sev}</span>
                    <span className="text-text-muted">
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-bg-primary rounded-full overflow-hidden border border-border-default">
                    <div className={`h-full ${colorClass}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Temporal Event Trends */}
      <Card title="Temporal Event Trends (PHASE-13-F06)">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {event_trends.map((bucket, idx) => (
            <div
              key={idx}
              className="p-4 rounded-lg border border-border-default bg-surface-secondary flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] font-mono text-text-muted block">
                  Time Window {new Date(bucket.bucket_start).toLocaleTimeString()}
                </span>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-2xl font-bold font-mono text-accent-cyan">{bucket.count}</span>
                  <span className="text-xs text-text-muted">events</span>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-border-default/50 text-[11px] font-mono text-text-muted">
                Stages: {Object.keys(bucket.stages).join(", ")}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
