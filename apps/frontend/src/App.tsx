import React, { useState } from "react";
import { AppShell } from "@/layouts/AppShell";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { InvestigationPage } from "@/pages/InvestigationPage";
import { TimelinePage } from "@/pages/TimelinePage";
import { ReportsPage } from "@/pages/ReportsPage";
import { MitigationPage } from "@/pages/MitigationPage";
import { SystemPage } from "@/pages/SystemPage";
import { LoginPage } from "@/pages/LoginPage";
import { AttackSimulatorModal } from "@/components/simulator/AttackSimulatorModal";

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return localStorage.getItem("forensiweb_auth") === "true";
  });
  const [currentAgent, setCurrentAgent] = useState<{
    id: string;
    name: string;
    role: string;
    clearance: string;
  }>(() => {
    const saved = localStorage.getItem("forensiweb_agent");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        // Fallback
      }
    }
    return {
      id: "AGENT-CYBER-941",
      name: "Agent Lead",
      role: "Lead Forensic Specialist",
      clearance: "LEVEL-4 TOP SECRET (ALPHA)",
    };
  });

  const [currentTab, setCurrentTab] = useState<string>("overview");
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);

  const handleLogin = (agent: { id: string; name: string; role: string; clearance: string }) => {
    setCurrentAgent(agent);
    setIsAuthenticated(true);
    localStorage.setItem("forensiweb_auth", "true");
    localStorage.setItem("forensiweb_agent", JSON.stringify(agent));
    setCurrentTab("overview");
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem("forensiweb_auth");
  };

  const renderContent = () => {
    switch (currentTab) {
      case "reports":
        return <ReportsPage />;
      case "mitigation":
      case "scenarios":
      case "lab-status":
        return <MitigationPage onOpenSimulator={() => setIsSimulatorOpen(true)} />;
      case "timeline":
      case "attack-chains":
        return <TimelinePage onOpenSimulator={() => setIsSimulatorOpen(true)} />;
      case "cases":
      case "evidence":
      case "findings":
      case "events":
      case "detections":
        return (
          <InvestigationPage
            defaultSubTab={currentTab}
            onOpenSimulator={() => setIsSimulatorOpen(true)}
          />
        );
      case "settings":
        return <SystemPage initialSubTab="settings" onOpenSimulator={() => setIsSimulatorOpen(true)} />;
      case "audit-logs":
        return <SystemPage initialSubTab="audit-logs" onOpenSimulator={() => setIsSimulatorOpen(true)} />;
      case "overview":
      default:
        return (
          <AnalyticsPage
            onNavigateTab={setCurrentTab}
            onOpenSimulator={() => setIsSimulatorOpen(true)}
          />
        );
    }
  };

  const handleSelectTab = (tab: string) => {
    setCurrentTab(tab);
    if (tab === "scenarios") {
      setIsSimulatorOpen(true);
    }
  };

  // If unauthenticated, show the cyber-crime thriller login page
  if (!isAuthenticated) {
    return (
      <LoginPage
        onLoginSuccess={handleLogin}
        onNavigateOverviewDirect={() => {
          setIsAuthenticated(true);
          localStorage.setItem("forensiweb_auth", "true");
          setCurrentTab("overview");
        }}
      />
    );
  }

  return (
    <>
      <AppShell
        currentTab={currentTab}
        onSelectTab={handleSelectTab}
        pageTitle={currentTab.toUpperCase().replace("-", " ")}
        activeCase={`CASE-001 • ${currentAgent.role}`}
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        onLogout={handleLogout}
      >
        {renderContent()}
      </AppShell>

      <AttackSimulatorModal
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        onNavigateToTimeline={() => setCurrentTab("timeline")}
        onNavigateToReports={() => setCurrentTab("reports")}
      />
    </>
  );
};
