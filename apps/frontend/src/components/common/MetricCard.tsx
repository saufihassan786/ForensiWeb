import React from "react";
import { Card } from "./Card";

export interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: {
    value: string;
    isPositive?: boolean;
    label?: string;
  };
  icon?: React.ReactNode;
  variant?: "blue" | "cyan" | "violet" | "critical";
  className?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  trend,
  icon,
  variant = "blue",
  className = "",
  onClick,
}) => {
  const accentColors = {
    blue: "text-accent-blue border-accent-blue/20 bg-accent-blue/10",
    cyan: "text-accent-cyan border-accent-cyan/20 bg-accent-cyan/10",
    violet: "text-accent-violet border-accent-violet/20 bg-accent-violet/10",
    critical: "text-status-critical border-status-critical/20 bg-status-critical/10",
  };

  return (
    <Card
      className={`${className} ${
        onClick ? "cursor-pointer interactive-card hover:border-border-active transition-all" : ""
      }`}
      glow={variant === "critical" ? "none" : variant}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            {label}
          </p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono tracking-tight text-text-primary">
              {value}
            </span>
            {trend && (
              <span
                className={`text-xs font-mono font-medium flex items-center ${
                  trend.isPositive ? "text-status-success" : "text-status-critical"
                }`}
              >
                {trend.isPositive ? "↑" : "↓"} {trend.value}
                {trend.label && (
                  <span className="ml-1 text-text-muted font-sans text-[10px]">
                    {trend.label}
                  </span>
                )}
              </span>
            )}
          </div>
        </div>
        {icon && (
          <div className={`p-2.5 rounded-lg border ${accentColors[variant]}`}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};
