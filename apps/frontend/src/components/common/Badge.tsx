import React from "react";
import { SeverityLevel, StatusState } from "@/types/tokens";

export type BadgeVariant =
  | SeverityLevel
  | StatusState
  | "success"
  | "warning"
  | "neutral";

export interface BadgeProps {
  variant?: BadgeVariant;
  label?: string;
  children?: React.ReactNode;
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "neutral",
  label,
  children,
  className = "",
  dot = true,
}) => {
  const variantStyles: Record<string, { bg: string; text: string; border: string; dotColor: string }> = {
    critical: {
      bg: "bg-status-critical/10",
      text: "text-status-critical",
      border: "border-status-critical/30",
      dotColor: "bg-status-critical",
    },
    high: {
      bg: "bg-status-high/10",
      text: "text-status-high",
      border: "border-status-high/30",
      dotColor: "bg-status-high",
    },
    medium: {
      bg: "bg-status-medium/10",
      text: "text-status-medium",
      border: "border-status-medium/30",
      dotColor: "bg-status-medium",
    },
    low: {
      bg: "bg-status-low/10",
      text: "text-status-low",
      border: "border-status-low/30",
      dotColor: "bg-status-low",
    },
    informational: {
      bg: "bg-status-info/10",
      text: "text-status-info",
      border: "border-status-info/30",
      dotColor: "bg-status-info",
    },
    success: {
      bg: "bg-status-success/10",
      text: "text-status-success",
      border: "border-status-success/30",
      dotColor: "bg-status-success",
    },
    completed: {
      bg: "bg-status-success/10",
      text: "text-status-success",
      border: "border-status-success/30",
      dotColor: "bg-status-success",
    },
    verified: {
      bg: "bg-accent-cyan/10",
      text: "text-accent-cyan",
      border: "border-accent-cyan/30",
      dotColor: "bg-accent-cyan",
    },
    active: {
      bg: "bg-accent-blue/10",
      text: "text-accent-blue-light",
      border: "border-accent-blue/30",
      dotColor: "bg-accent-blue animate-pulse",
    },
    processing: {
      bg: "bg-accent-violet/10",
      text: "text-accent-violet",
      border: "border-accent-violet/30",
      dotColor: "bg-accent-violet animate-pulse",
    },
    failed: {
      bg: "bg-status-critical/10",
      text: "text-status-critical",
      border: "border-status-critical/30",
      dotColor: "bg-status-critical",
    },
    neutral: {
      bg: "bg-status-neutral/10",
      text: "text-text-muted",
      border: "border-status-neutral/20",
      dotColor: "bg-status-neutral",
    },
  };

  const style = variantStyles[variant] || variantStyles.neutral;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${style.dotColor}`} />}
      {children || label || variant.toUpperCase()}
    </span>
  );
};
