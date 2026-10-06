import React, { useState } from "react";
import { AppShell } from "@/layouts/AppShell";
import { Card } from "@/components/common/Card";
import { Button } from "@/components/common/Button";
import { Badge } from "@/components/common/Badge";
import { Input } from "@/components/common/Input";
import { MetricCard } from "@/components/common/MetricCard";
import { LoadingState } from "@/components/states/LoadingState";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import {
  Activity,
  AlertOctagon,
  Database,
  FolderPlus,
  Play,
  Shield,
} from "lucide-react";

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState("overview");
  const [demoState, setDemoState] = useState<"normal" | "loading" | "empty" | "error">("normal");

  return (
    <AppShell
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      pageTitle={currentTab.toUpperCase().replace("-", " ")}
      activeCase="CASE-001 (LFI PrivEsc Scenario)"
    >
      <div className="space-y-6">
        {/* Top Hero Banner */}
        <div className="relative overflow-hidden rounded-card border border-border-default bg-surface-primary p-6 shadow-sm">
          <div className="absolute top-0 right-0 w-96 h-96 bg-accent-blue/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="verified" dot>
                  FORENSIC COMMAND ACTIVE
                </Badge>
                <Badge variant="informational">SCENARIO WEB-CHAIN-001</Badge>
              </div>
              <h2 className="text-xl lg:text-2xl font-bold tracking-tight text-text-primary">
                Controlled LFI-to-Privilege-Escalation Investigation
              </h2>
              <p className="text-xs text-text-secondary mt-1.5 max-w-2xl leading-relaxed">
                Reproducible forensic examination of Apache log poisoning, PHP webshell deployment, and PATH misconfiguration exploitation in an isolated container environment.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="primary"
                size="sm"
                icon={<Play className="w-3.5 h-3.5" />}
                onClick={() => setDemoState("loading")}
              >
                Run Analysis
              </Button>
              <Button
                variant="secondary"
                size="sm"
                icon={<FolderPlus className="w-3.5 h-3.5" />}
                onClick={() => setDemoState("normal")}
              >
                Ingest Evidence
              </Button>
            </div>
          </div>
        </div>

        {/* High-Level Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Active Investigations"
            value="3"
            trend={{ value: "100%", isPositive: true, label: "isolated" }}
            variant="blue"
            icon={<Shield className="w-5 h-5 text-accent-blue" />}
          />
          <MetricCard
            label="Evidence Artifacts"
            value="14"
            trend={{ value: "SHA-256", isPositive: true, label: "verified" }}
            variant="cyan"
            icon={<Database className="w-5 h-5 text-accent-cyan" />}
          />
          <MetricCard
            label="Security Detections"
            value="6"
            trend={{ value: "2 Critical", isPositive: false }}
            variant="critical"
            icon={<AlertOctagon className="w-5 h-5 text-status-critical" />}
          />
          <MetricCard
            label="Normalized Events"
            value="1,428"
            trend={{ value: "UTC Normalized", isPositive: true }}
            variant="violet"
            icon={<Activity className="w-5 h-5 text-accent-violet" />}
          />
        </div>

        {/* Attack Stage Chain Overview */}
        <Card title="Attack Progression Chain (WEB-CHAIN-001)">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            {[
              { stage: "LFI", desc: "Local File Traversal Probing", status: "critical", active: true },
              { stage: "LOG POISONING", desc: "User-Agent Header Injection", status: "critical", active: true },
              { stage: "RCE", desc: "Web Log Inclusion Execution", status: "high", active: true },
              { stage: "WEB SHELL", desc: "Persistent Command Payload", status: "high", active: true },
              { stage: "PRIV ESC", desc: "PATH Environmental Hijacking", status: "medium", active: false },
            ].map((node, i) => (
              <div
                key={i}
                className={`p-3.5 rounded-lg border flex flex-col justify-between transition-all ${
                  node.active
                    ? "bg-surface-secondary border-border-active shadow-sm"
                    : "bg-bg-secondary/40 border-border-default/50 opacity-70"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-mono font-bold text-accent-cyan">
                    STAGE 0{i + 1}
                  </span>
                  <Badge variant={node.status as any} dot={node.active}>
                    {node.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-text-primary tracking-wide">
                    {node.stage}
                  </h4>
                  <p className="text-[11px] text-text-muted mt-0.5 leading-snug">
                    {node.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Interactive State Demonstrator */}
        <Card
          title="Component States & Design Verification"
          subtitle="Test loading, empty, and error fallback states required by PHASE-03-F08"
          action={
            <div className="flex items-center gap-2">
              <Button
                variant={demoState === "normal" ? "primary" : "ghost"}
                size="sm"
                onClick={() => setDemoState("normal")}
              >
                Normal
              </Button>
              <Button
                variant={demoState === "loading" ? "primary" : "ghost"}
                size="sm"
                onClick={() => setDemoState("loading")}
              >
                Loading
              </Button>
              <Button
                variant={demoState === "empty" ? "primary" : "ghost"}
                size="sm"
                onClick={() => setDemoState("empty")}
              >
                Empty
              </Button>
              <Button
                variant={demoState === "error" ? "primary" : "ghost"}
                size="sm"
                onClick={() => setDemoState("error")}
              >
                Error
              </Button>
            </div>
          }
        >
          {demoState === "loading" && <LoadingState />}
          {demoState === "empty" && (
            <EmptyState
              title="No Evidence Ingested"
              description="Please upload raw log files or connect the isolated laboratory container."
              actionLabel="Switch to Normal"
              onAction={() => setDemoState("normal")}
            />
          )}
          {demoState === "error" && (
            <ErrorState
              title="Failed to Connect to Forensic Engine"
              message="The engine could not connect to PostgreSQL on 127.0.0.1:5432. Please ensure Docker Compose service is healthy."
              errorCode="DB_CONNECTION_REFUSED"
              onRetry={() => setDemoState("normal")}
            />
          )}
          {demoState === "normal" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Badges and Buttons */}
              <div className="space-y-4">
                <h4 className="text-xs font-mono font-semibold uppercase text-text-muted tracking-wider">
                  Semantic Status Badges
                </h4>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="critical">CRITICAL</Badge>
                  <Badge variant="high">HIGH</Badge>
                  <Badge variant="medium">MEDIUM</Badge>
                  <Badge variant="low">LOW</Badge>
                  <Badge variant="informational">INFO</Badge>
                  <Badge variant="success">SUCCESS</Badge>
                  <Badge variant="verified">VERIFIED</Badge>
                </div>

                <h4 className="text-xs font-mono font-semibold uppercase text-text-muted tracking-wider pt-2">
                  Button Hierarchy
                </h4>
                <div className="flex flex-wrap gap-2">
                  <Button variant="primary" size="sm">
                    Primary CTA
                  </Button>
                  <Button variant="secondary" size="sm">
                    Secondary
                  </Button>
                  <Button variant="ghost" size="sm">
                    Ghost
                  </Button>
                  <Button variant="destructive" size="sm">
                    Destructive Action
                  </Button>
                </div>
              </div>

              {/* Input Samples */}
              <div className="space-y-4">
                <h4 className="text-xs font-mono font-semibold uppercase text-text-muted tracking-wider">
                  Analyst Input Controls
                </h4>
                <Input
                  label="Target Case Reference"
                  placeholder="e.g. CASE-2026-001"
                  defaultValue="CASE-001"
                  helperText="Unique identifier conforming to forensic custody log"
                />
                <Input
                  label="Filter by Event Source"
                  placeholder="e.g. /var/log/apache2/access.log"
                  error="File path traversal pattern detected in query"
                />
              </div>
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  );
};
