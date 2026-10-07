import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Card } from "../components/common/Card";
import { Input } from "../components/common/Input";
import { MetricCard } from "../components/common/MetricCard";
import { Modal } from "../components/common/Modal";
import { LoadingState } from "../components/states/LoadingState";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { Sidebar } from "../layouts/Sidebar";
import { TopNav } from "../layouts/TopNav";

describe("Core UI Components (PHASE-03-F04)", () => {
  it("renders Button with variant styles and handles click", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Run Analysis</Button>);

    const btn = screen.getByRole("button", { name: /run analysis/i });
    expect(btn).toBeDefined();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("renders Badge with semantic label", () => {
    render(<Badge variant="critical">CRITICAL</Badge>);
    expect(screen.getByText("CRITICAL")).toBeDefined();
  });

  it("renders Card with title and children", () => {
    render(
      <Card title="Attack Chain">
        <p>Chain content</p>
      </Card>
    );
    expect(screen.getByText("Attack Chain")).toBeDefined();
    expect(screen.getByText("Chain content")).toBeDefined();
  });

  it("renders Input with label and error state", () => {
    render(
      <Input label="Target Case" error="Case ID invalid" defaultValue="CASE-01" />
    );
    expect(screen.getByLabelText("Target Case")).toBeDefined();
    expect(screen.getByText("Case ID invalid")).toBeDefined();
  });

  it("renders MetricCard with title, value, and trend", () => {
    render(
      <MetricCard
        label="Active Cases"
        value={12}
        trend={{ value: "10%", isPositive: true }}
      />
    );
    expect(screen.getByText("Active Cases")).toBeDefined();
    expect(screen.getByText("12")).toBeDefined();
    expect(screen.getByText(/10%/)).toBeDefined();
  });

  it("renders Modal when open and handles escape key", () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title="Case Investigation">
        <p>Modal body</p>
      </Modal>
    );
    expect(screen.getByText("Case Investigation")).toBeDefined();
    expect(screen.getByText("Modal body")).toBeDefined();

    fireEvent.keyDown(window, { key: "Escape" });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

describe("State Components (PHASE-03-F08)", () => {
  it("renders LoadingState with message", () => {
    render(<LoadingState message="Analyzing Web Shell..." />);
    expect(screen.getByText("Analyzing Web Shell...")).toBeDefined();
  });

  it("renders EmptyState with action trigger", () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No Evidence Found"
        actionLabel="Register Evidence"
        onAction={handleAction}
      />
    );
    expect(screen.getByText("No Evidence Found")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: /register evidence/i }));
    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it("renders ErrorState with code and retry trigger", () => {
    const handleRetry = vi.fn();
    render(
      <ErrorState
        title="Database Down"
        errorCode="ECONNREFUSED"
        onRetry={handleRetry}
      />
    );
    expect(screen.getByText("Database Down")).toBeDefined();
    expect(screen.getByText("CODE: ECONNREFUSED")).toBeDefined();
    fireEvent.click(screen.getByRole("button", { name: /retry request/i }));
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});

describe("Navigation Layouts (PHASE-03-F06, F07)", () => {
  it("renders Sidebar and handles tab selection", () => {
    const handleSelect = vi.fn();
    render(
      <Sidebar
        currentTab="overview"
        onSelectTab={handleSelect}
        isCollapsed={false}
        onToggleCollapse={() => {}}
      />
    );
    const timelineBtn = screen.getByRole("button", { name: /timeline/i });
    fireEvent.click(timelineBtn);
    expect(handleSelect).toHaveBeenCalledWith("timeline");
  });

  it("renders TopNav with active case indicator", () => {
    render(<TopNav pageTitle="Overview" activeCase="CASE-001" />);
    expect(screen.getByText("Overview")).toBeDefined();
    expect(screen.getByText("CASE-001")).toBeDefined();
  });
});
