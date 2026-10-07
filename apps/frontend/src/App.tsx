import React, { useState } from "react";
import { AppShell } from "@/layouts/AppShell";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { InvestigationPage } from "@/pages/InvestigationPage";
import { TimelinePage } from "@/pages/TimelinePage";
import { ReportsPage } from "@/pages/ReportsPage";
import { MitigationPage } from "@/pages/MitigationPage";
import { SystemPage } from "@/pages/SystemPage";
import { AttackSimulatorModal } from "@/components/simulator/AttackSimulatorModal";

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>("overview");
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);

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

  return (
    <>
      <AppShell
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        pageTitle={currentTab.toUpperCase().replace("-", " ")}
        activeCase="CASE-001 (LFI PrivEsc Scenario)"
        onOpenSimulator={() => setIsSimulatorOpen(true)}
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
