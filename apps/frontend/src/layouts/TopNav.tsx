import React from "react";
import { Bell, Command, Search, User } from "lucide-react";
import { Badge } from "@/components/common/Badge";

export interface TopNavProps {
  pageTitle: string;
  activeCase?: string;
  onOpenSearch?: () => void;
  isLabOnline?: boolean;
}

export const TopNav: React.FC<TopNavProps> = ({
  pageTitle,
  activeCase = "CASE-001 (LFI PrivEsc Chain)",
  onOpenSearch,
  isLabOnline = true,
}) => {
  return (
    <header className="h-16 px-6 bg-bg-secondary/80 backdrop-blur-md border-b border-border-default sticky top-0 z-30 flex items-center justify-between gap-4">
      {/* Page Title & Case Context */}
      <div className="flex items-center gap-4 min-w-0">
        <div>
          <h1 className="text-base font-bold text-text-primary capitalize tracking-tight flex items-center gap-2">
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
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSearch}
          className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-surface-primary border border-border-default text-text-muted hover:text-text-primary hover:border-border-active transition-all duration-150 text-xs w-64 justify-between group"
          aria-label="Search forensic telemetry"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-text-muted group-hover:text-accent-blue" />
            <span className="truncate">Search cases, hashes, IPs...</span>
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

        {/* Notification Bell */}
        <button
          className="relative p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-hover transition-colors"
          aria-label="Alerts and notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-status-critical animate-ping" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-status-critical" />
        </button>

        {/* Analyst Profile Pill */}
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
        </div>
      </div>
    </header>
  );
};
