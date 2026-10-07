import React, { useEffect, useState } from "react";
import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";
import { Modal } from "@/components/common/Modal";
import { Input } from "@/components/common/Input";
import { Search } from "lucide-react";

export interface AppShellProps {
  children: React.ReactNode;
  currentTab: string;
  onSelectTab: (tabId: string) => void;
  pageTitle?: string;
  activeCase?: string;
  onOpenSimulator?: () => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  currentTab,
  onSelectTab,
  pageTitle = "Investigation Command Center",
  activeCase,
  onOpenSimulator,
}) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Search items catalog
  const searchableItems = [
    { id: "s1", title: "LFI Directory Traversal Vulnerability", category: "Finding", tab: "investigation", hint: "FND-001 • MITRE T1083" },
    { id: "s2", title: "Apache Access Log Poisoning", category: "Detection", tab: "timeline", hint: "RULE-002 • MITRE T1059.004" },
    { id: "s3", title: "Remote Code Execution via Log Inclusion", category: "Finding", tab: "investigation", hint: "FND-002 • Critical Severity" },
    { id: "s4", title: "PATH Environment Variable Misconfiguration", category: "Finding", tab: "mitigation", hint: "FND-003 • Privilege Escalation" },
    { id: "s5", title: "Pristine Evidence: access.log", category: "Evidence", tab: "investigation", hint: "SHA-256 Verified • Apache Combined" },
    { id: "s6", title: "Pristine Evidence: audit.log", category: "Evidence", tab: "investigation", hint: "SHA-256 Verified • Linux Auditd" },
    { id: "s7", title: "Attack Chain Chronological Timeline", category: "Workspace", tab: "timeline", hint: "5 Attack Stages Reconstructed" },
    { id: "s8", title: "Forensic Technical Report Generator", category: "Report", tab: "reports", hint: "Cryptographic Integrity Export" },
    { id: "s9", title: "Defensive Mitigations & Telemetry Diff", category: "Defense", tab: "mitigation", hint: "Before / After Comparative Model" },
  ];

  const filteredItems = searchQuery.trim()
    ? searchableItems.filter(
        (item) =>
          item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.hint.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : searchableItems.slice(0, 5);

  // Global Ctrl + K listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary flex flex-col antialiased transition-colors duration-200">
      {/* Accessibility Skip Link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 z-50 px-4 py-2 bg-accent-blue text-white font-medium rounded-lg shadow-lg"
      >
        Skip to main content
      </a>

      {/* Primary Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={onSelectTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          isSidebarCollapsed ? "pl-16" : "pl-64"
        }`}
      >
        <TopNav
          pageTitle={pageTitle}
          activeCase={activeCase}
          onOpenSearch={() => setIsSearchOpen(true)}
          onOpenSimulator={onOpenSimulator}
        />

        <main id="main-content" className="flex-1 p-6 max-w-7xl w-full mx-auto cyber-grid animate-fade-in">
          {children}
        </main>
      </div>

      {/* Global Search Modal */}
      <Modal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        title="Global Forensic Search"
        description="Search across normalized events, cryptographic hashes, IPs, and investigation findings."
        maxWidth="lg"
      >
        <div className="space-y-4">
          <Input
            placeholder="Type query (e.g. 192.168.1.100, access.log, LFI, SHA256)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leadingIcon={<Search className="w-4 h-4" />}
            autoFocus
          />

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {filteredItems.length > 0 ? (
              filteredItems.map((item) => (
                <div
                  key={item.id}
                  onClick={() => {
                    onSelectTab(item.tab);
                    setIsSearchOpen(false);
                    setSearchQuery("");
                  }}
                  className="p-3 rounded-lg bg-surface-primary hover:bg-surface-hover border border-border-default hover:border-border-active cursor-pointer transition-all duration-150 flex items-center justify-between gap-3 group"
                >
                  <div className="min-w-0">
                    <span className="font-semibold text-xs text-text-primary group-hover:text-accent-blue transition-colors">
                      {item.title}
                    </span>
                    <p className="text-[11px] text-text-muted mt-0.5 truncate">{item.hint}</p>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-secondary text-accent-cyan border border-border-default shrink-0">
                    {item.category}
                  </span>
                </div>
              ))
            ) : (
              <div className="py-6 text-center text-xs text-text-muted">
                No matching telemetry or findings found for &ldquo;{searchQuery}&rdquo;.
              </div>
            )}
          </div>

          <div className="pt-2 border-t border-border-default flex items-center justify-between text-[11px] text-text-muted">
            <span>Click any result to jump to that workspace view.</span>
            <span>
              Press <kbd className="px-1.5 py-0.5 rounded bg-surface-secondary border border-border-default font-mono">ESC</kbd> to exit
            </span>
          </div>
        </div>
      </Modal>
    </div>
  );
};
