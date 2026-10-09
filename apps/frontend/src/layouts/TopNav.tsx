import React, { useState } from "react";
import { Bell, Command, Lock, Moon, Search, Sun, User, Zap } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import { useTheme } from "@/hooks/useTheme";

export interface TopNavProps {
  pageTitle: string;
  activeCase?: string;
  onOpenSearch?: () => void;
  onOpenSimulator?: () => void;
  isLabOnline?: boolean;
  onLogout?: () => void;
  onNavigateOverview?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  pageTitle,
  activeCase = "CASE-001 (LFI PrivEsc Chain)",
  onOpenSearch,
  onOpenSimulator,
  isLabOnline = true,
  onLogout,
  onNavigateOverview,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header className="h-16 px-6 bg-bg-secondary/90 backdrop-blur-md border-b border-border-default sticky top-0 z-30 flex items-center justify-between gap-4 transition-colors duration-200">
      {/* Page Title & Case Context */}
      <div className="flex items-center gap-4 min-w-0">
        <div
          onClick={onNavigateOverview}
          className={onNavigateOverview ? "cursor-pointer group" : ""}
          title={onNavigateOverview ? "Jump to Overview Dashboard" : undefined}
        >
          <h1 className="text-base font-bold text-text-primary group-hover:text-accent-cyan transition-colors capitalize tracking-tight flex items-center gap-2">
            {pageTitle}
          </h1>
        </div>
        <div className="hidden md:flex items-center gap-2 pl-4 border-l border-border-default">
          <span className="text-[11px] font-mono text-text-muted">ACTIVE CASE:</span>
          <Badge variant="verified" dot>
            {activeCase}
          </Badge>
        </div>
      </div>

      {/* Global Search & Quick Actions */}
      <div className="flex items-center gap-2.5">
        {/* Cyber Attack Simulator Quick Button */}
        <button
          onClick={onOpenSimulator}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent-blue/15 border border-accent-blue/40 text-accent-cyan hover:bg-accent-blue/25 hover:border-accent-blue transition-all duration-150 text-xs font-semibold shadow-sm group"
          title="Open interactive cyber attack simulator"
          aria-label="Launch cyber attack simulator"
        >
          <Zap className="w-3.5 h-3.5 text-accent-cyan group-hover:scale-110 transition-transform animate-pulse" />
          <span className="hidden sm:inline">Simulate Attack</span>
        </button>

        <button
          onClick={onOpenSearch}
          className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-surface-primary border border-border-default text-text-muted hover:text-text-primary hover:border-border-active transition-all duration-150 text-xs w-56 justify-between group"
          aria-label="Search forensic telemetry"
        >
          <div className="flex items-center gap-2 truncate">
            <Search className="w-3.5 h-3.5 text-text-muted group-hover:text-accent-blue shrink-0" />
            <span className="truncate">Search cases, hashes...</span>
          </div>
          <kbd className="hidden lg:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono font-semibold text-text-muted bg-surface-secondary border border-border-default rounded">
            <Command className="w-2.5 h-2.5" /> K
          </kbd>
        </button>

        {/* Lab Status Pill */}
        <div className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded-full bg-surface-primary border border-border-default text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              isLabOnline ? "bg-status-success animate-pulse" : "bg-status-critical"
            }`}
          />
          <span className="text-[11px] font-mono text-text-secondary">
            LAB: {isLabOnline ? "CONTAINED" : "OFFLINE"}
          </span>
        </div>

        {/* Theme Mode Switcher */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-hover border border-transparent hover:border-border-default transition-all duration-200"
          title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
          aria-label="Toggle color theme"
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4 text-amber-400 hover:rotate-90 transition-transform duration-300" />
          ) : (
            <Moon className="w-4 h-4 text-accent-indigo hover:-rotate-45 transition-transform duration-300" />
          )}
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications((prev) => !prev)}
            className="relative p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-hover transition-colors"
            aria-label="Alerts and notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-status-critical animate-ping" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-status-critical" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 p-3 rounded-xl bg-surface-primary border border-border-default shadow-xl z-50 text-xs space-y-2 animate-fade-in">
              <div className="flex items-center justify-between font-semibold text-text-primary pb-2 border-b border-border-default">
                <span>Recent Forensic Alerts</span>
                <Badge variant="critical">3 Unresolved</Badge>
              </div>
              <div className="space-y-1.5">
                <div className="p-2 rounded bg-surface-secondary border border-border-default">
                  <span className="font-semibold text-status-critical">ALT-S5: Privilege Escalation</span>
                  <p className="text-text-muted text-[11px]">PATH hijack detected via /privesc/run-backup.</p>
                </div>
                <div className="p-2 rounded bg-surface-secondary border border-border-default">
                  <span className="font-semibold text-status-high">ALT-S2: Log Poisoning</span>
                  <p className="text-text-muted text-[11px]">PHP code block detected in Apache access.log.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Analyst Profile Pill & Terminal Lock */}
        <div className="flex items-center gap-2 pl-2 border-l border-border-default">
          <div className="w-8 h-8 rounded-full bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center text-accent-cyan shadow-sm">
            <User className="w-4 h-4 text-accent-cyan" />
          </div>
          <div className="hidden 2xl:flex flex-col">
            <span className="text-xs font-semibold text-text-primary">
              Analyst Lead
            </span>
            <span className="text-[10px] font-mono text-text-muted">
              SEC-OPS-01
            </span>
          </div>

          {onLogout && (
            <button
              onClick={onLogout}
              className="p-1.5 rounded-lg text-text-muted hover:text-status-critical hover:bg-surface-hover border border-transparent hover:border-border-default transition-colors text-xs font-mono flex items-center gap-1.5 ml-1"
              title="Lock Terminal & Return to Login Screen"
              aria-label="Lock terminal"
            >
              <Lock className="w-3.5 h-3.5 text-text-muted hover:text-status-critical transition-colors" />
              <span className="hidden xl:inline text-[11px] font-mono">Lock</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
