import React from "react";
import {
  Activity,
  AlertOctagon,
  ChevronLeft,
  ChevronRight,
  Clock,
  Compass,
  Database,
  FileCheck,
  FileText,
  FlaskConical,
  GitBranch,
  Layers,
  Settings,
  Shield,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

export type NavItem = {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeVariant?: "critical" | "high" | "info";
};

export type NavSection = {
  title?: string;
  items: NavItem[];
};

export const NAV_SECTIONS: NavSection[] = [
  {
    items: [{ id: "overview", label: "Overview", icon: Compass }],
  },
  {
    title: "INVESTIGATION",
    items: [
      { id: "cases", label: "Cases", icon: FolderCheckIcon, badge: "3", badgeVariant: "info" },
      { id: "evidence", label: "Evidence", icon: Database },
      { id: "events", label: "Events", icon: Activity },
      { id: "detections", label: "Detections", icon: AlertOctagon, badge: "2", badgeVariant: "critical" },
      { id: "timeline", label: "Timeline", icon: Clock },
      { id: "findings", label: "Findings", icon: FileCheck },
    ],
  },
  {
    title: "ANALYSIS",
    items: [
      { id: "attack-chains", label: "Attack Chains", icon: GitBranch },
      { id: "reports", label: "Reports", icon: FileText },
    ],
  },
  {
    title: "LAB",
    items: [
      { id: "mitigation", label: "Mitigation & Verify", icon: ShieldCheck },
      { id: "scenarios", label: "Scenarios", icon: FlaskConical },
      { id: "lab-status", label: "Lab Status", icon: ShieldAlert },
    ],
  },
  {
    title: "SYSTEM",
    items: [
      { id: "settings", label: "Settings", icon: Settings },
      { id: "audit-logs", label: "Audit Logs", icon: Layers },
    ],
  },
];

function FolderCheckIcon(props: { className?: string }) {
  return <Shield className={props.className} />;
}

export interface SidebarProps {
  currentTab: string;
  onSelectTab: (tabId: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
}) => {
  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-40 bg-bg-secondary border-r border-border-default flex flex-col transition-all duration-300 ease-in-out ${
        isCollapsed ? "w-16" : "w-64"
      }`}
      aria-label="Primary Platform Navigation"
    >
      {/* Brand Header */}
      <div className="h-16 px-4 border-b border-border-default flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center text-accent-cyan shadow-glow-cyan">
              <Shield className="w-4 h-4 text-accent-cyan" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-sm tracking-wider text-text-primary uppercase">
                Forensi<span className="text-accent-cyan">Web</span>
              </span>
              <span className="text-[10px] font-mono text-accent-blue-light tracking-widest uppercase">
                v0.1.0 Command
              </span>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="mx-auto w-8 h-8 rounded-lg bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center text-accent-cyan shadow-glow-cyan">
            <Shield className="w-4 h-4 text-accent-cyan" />
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-6">
        {NAV_SECTIONS.map((section, idx) => (
          <div key={idx}>
            {!isCollapsed && section.title && (
              <p className="px-3 mb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-text-muted">
                {section.title}
              </p>
            )}
            <ul className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = currentTab === item.id;
                return (
                  <li key={item.id}>
                    <button
                      onClick={() => onSelectTab(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 group relative ${
                        isActive
                          ? "bg-accent-blue/15 text-accent-cyan border border-border-active shadow-glow-blue"
                          : "text-text-secondary hover:text-text-primary hover:bg-surface-hover border border-transparent"
                      } ${isCollapsed ? "justify-center" : ""}`}
                      title={isCollapsed ? item.label : undefined}
                    >
                      <Icon
                        className={`w-4 h-4 flex-shrink-0 transition-colors ${
                          isActive
                            ? "text-accent-cyan"
                            : "text-text-muted group-hover:text-text-primary"
                        }`}
                      />
                      {!isCollapsed && (
                        <>
                          <span className="flex-1 text-left truncate">
                            {item.label}
                          </span>
                          {item.badge && (
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                                item.badgeVariant === "critical"
                                  ? "bg-status-critical/20 text-status-critical border border-status-critical/30"
                                  : "bg-accent-blue/20 text-accent-blue-light border border-accent-blue/30"
                              }`}
                            >
                              {item.badge}
                            </span>
                          )}
                        </>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Collapse Toggle Footer */}
      <div className="p-3 border-t border-border-default flex items-center justify-between">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-hover transition-colors"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <div className="flex items-center gap-2 text-xs font-medium">
              <ChevronLeft className="w-4 h-4" />
              <span>Collapse Sidebar</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};
