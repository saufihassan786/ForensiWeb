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
  FileText,
  Gamepad2,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { Button } from "@/components/common/Button";
import { BrandLogo } from "@/components/common/BrandLogo";

export interface AnalyticsPageProps {
  onNavigateTab?: (tab: string) => void;
  onOpenSimulator?: () => void;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({
  onNavigateTab,
  onOpenSimulator,
}) => {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);

  useEffect(() => {
    apiService.getAnalytics().then(setAnalytics);
  }, []);

  if (!analytics) {
    return (
      <div className="py-12 text-center text-xs text-text-muted animate-pulse">
        Loading system overview...
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
      {/* Top Banner with Brand Identity & Quick Actions — Free-standing, no square borders */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 pb-1">
        <div className="flex flex-col sm:flex-row sm:items-center gap-5 min-w-0">
          <BrandLogo
            size="lg"
            layout="horizontal"
            showText={true}
            showTagline={true}
            interactive={true}
            onClick={() => onNavigateTab?.("overview")}
            title="ForensiWeb — Investigation Command Center"
          />
          <div className="hidden sm:block h-10 w-px bg-border-default" />
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <Badge variant="verified" dot>COMMAND CENTER</Badge>
              <Badge variant="informational">{case_overview.case_id}</Badge>
            </div>
            <h2 className="text-sm font-semibold tracking-tight text-text-secondary truncate">
              {case_overview.title} • Security Telemetry & Live Analysis
            </h2>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <Button
            variant="primary"
            size="sm"
            onClick={onOpenSimulator}
            className="flex items-center gap-1.5 bg-gradient-to-r from-accent-blue to-accent-cyan text-slate-950 font-bold shadow-glow-cyan hover:scale-[1.02] transition-transform"
          >
            <Zap className="w-4 h-4 fill-current text-slate-950" />
            <span>Play Simulation</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => onNavigateTab?.("reports")}
            className="flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-accent-cyan" />
            <span>Reports</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => onNavigateTab?.("mitigation")}
            className="flex items-center gap-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-status-success" />
            <span>Defense Shield</span>
          </Button>
        </div>
      </div>

      {/* Gamified Attack Simulator Invitation Card — Adaptive across Light & Dark themes */}
      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-surface-primary via-surface-secondary to-accent-blue/10 dark:to-accent-blue/20 border border-border-default dark:border-accent-blue/40 shadow-sm dark:shadow-glow-blue flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center text-accent-blue dark:text-accent-cyan shrink-0 shadow-sm">
            <Gamepad2 className="w-6 h-6 text-accent-blue dark:text-accent-cyan" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
              <span>Interactive Attack &amp; Defense Simulator</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-status-critical/15 text-status-critical font-mono font-bold">
                5 STAGES
              </span>
            </h3>
            <p className="text-xs text-text-secondary mt-0.5">
              Launch a live hacker simulation to watch attacks and simultaneous detection in real time.
            </p>
          </div>
        </div>

        <button
          onClick={onOpenSimulator}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-accent-blue to-accent-cyan text-slate-950 text-xs font-black uppercase tracking-wider shadow-glow-cyan hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2 shrink-0"
        >
          <span>Launch Simulator</span>
          <Zap className="w-3.5 h-3.5 fill-current" />
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Evidence Files"
          value={evidence_metrics.total_artifacts.toString()}
          trend={{ value: `${evidence_metrics.verified_hashes} Verified`, isPositive: true }}
          variant="cyan"
          icon={<Database className="w-5 h-5 text-accent-cyan" />}
          onClick={() => onNavigateTab?.("evidence")}
          className="hover:scale-[1.02] transition-transform"
        />
        <MetricCard
          label="Logged Events"
          value={event_metrics.total_events.toString()}
          trend={{ value: "Live stream", isPositive: true }}
          variant="blue"
          icon={<Activity className="w-5 h-5 text-accent-blue" />}
          onClick={() => onNavigateTab?.("events")}
          className="hover:scale-[1.02] transition-transform"
        />
        <MetricCard
          label="Active Alerts"
          value={detection_metrics.total_alerts.toString()}
          trend={{ value: `${detection_metrics.by_severity.critical || 0} Critical`, isPositive: false }}
          variant="critical"
          icon={<AlertOctagon className="w-5 h-5 text-status-critical" />}
          onClick={() => onNavigateTab?.("detections")}
          className="hover:scale-[1.02] transition-transform"
        />
        <MetricCard
          label="Security Findings"
          value={finding_metrics.total_findings.toString()}
          trend={{ value: `${finding_metrics.mitigated_count} Protected`, isPositive: true }}
          variant="violet"
          icon={<FileCheck className="w-5 h-5 text-accent-violet" />}
          onClick={() => onNavigateTab?.("findings")}
          className="hover:scale-[1.02] transition-transform"
        />
      </div>

      {/* System Risk Score */}
      <Card
        title="System Risk Level"
        subtitle="Calculated from detected threats and system vulnerabilities."
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
                {risk_summary.risk_level} RISK
              </Badge>
            </div>
            <p className="text-[11px] text-text-muted mt-2 max-w-xs">
              System requires defense shields to prevent unauthorized root privilege escalation.
            </p>
          </div>

          {/* Factor Breakdown */}
          <div className="lg:col-span-2 space-y-2.5">
            <h4 className="text-xs font-mono font-bold uppercase text-text-muted mb-2">
              Key Risk Factors
            </h4>
            {risk_summary.explanation_factors.map((factor, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg border border-border-default bg-surface-secondary flex items-center justify-between text-xs gap-3"
              >
                <div>
                  <span className="font-bold text-text-primary block text-xs">
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

      {/* Attack Progression & Severity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stage Progression */}
        <Card title="Attack Progression" subtitle="5 stages from initial probe to administrator access.">
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="text-text-muted">Chain Completion</span>
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
                <span className="text-text-muted">Highest Stage Reached:</span>
                <span className="font-mono font-bold text-status-critical">
                  {attack_stage_analytics.highest_stage_reached}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Verified Stages:</span>
                <span className="font-mono text-accent-cyan">
                  {attack_stage_analytics.stages_detected.length} / 5 Stages
                </span>
              </div>
            </div>
          </div>
        </Card>

        {/* Severity Breakdown */}
        <Card title="Threat Severity" subtitle="Breakdown of detected security issues.">
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

      {/* Recent Activity */}
      <Card title="Recent Activity" subtitle="Events recorded during attack and defense testing.">
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
                Active Stages: {Object.keys(bucket.stages).join(", ")}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
