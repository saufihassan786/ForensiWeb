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
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  currentTab,
  onSelectTab,
  pageTitle = "Investigation Command Center",
  activeCase,
}) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

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
    <div className="min-h-screen bg-bg-primary text-text-primary flex flex-col antialiased">
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
        />

        <main id="main-content" className="flex-1 p-6 max-w-7xl w-full mx-auto cyber-grid">
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
          <div className="py-6 text-center text-xs text-text-muted">
            {searchQuery ? (
              <p>Searching for telemetry matching &ldquo;{searchQuery}&rdquo;...</p>
            ) : (
              <p>Press <kbd className="px-1.5 py-0.5 rounded bg-surface-secondary border border-border-default font-mono">ESC</kbd> to exit</p>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
};
