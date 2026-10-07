import React, { useState } from "react";
import { AppShell } from "@/layouts/AppShell";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { InvestigationPage } from "@/pages/InvestigationPage";
import { TimelinePage } from "@/pages/TimelinePage";
import { ReportsPage } from "@/pages/ReportsPage";
import { MitigationPage } from "@/pages/MitigationPage";

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>("overview");

  const renderContent = () => {
    switch (currentTab) {
      case "reports":
        return <ReportsPage />;
      case "mitigation":
      case "scenarios":
      case "lab-status":
        return <MitigationPage />;
      case "timeline":
      case "attack-chains":
        return <TimelinePage />;
      case "cases":
      case "evidence":
      case "findings":
      case "events":
      case "detections":
        return <InvestigationPage />;
      case "overview":
      default:
        return <AnalyticsPage />;
    }
  };

  return (
    <AppShell
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      pageTitle={currentTab.toUpperCase().replace("-", " ")}
      activeCase="CASE-001 (LFI PrivEsc Scenario)"
    >
      {renderContent()}
    </AppShell>
  );
};
