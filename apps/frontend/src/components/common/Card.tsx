import React from "react";

export interface CardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerClassName?: string;
  glow?: "blue" | "cyan" | "violet" | "none";
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  action,
  children,
  className = "",
  headerClassName = "",
  glow = "none",
  onClick,
}) => {
  const glowStyles = {
    blue: "hover:border-border-active hover:shadow-glow-blue",
    cyan: "hover:border-accent-cyan/50 hover:shadow-glow-cyan",
    violet: "hover:border-accent-violet/50 hover:shadow-glow-violet",
    none: "hover:border-border-default/80",
  };

  return (
    <div
      onClick={onClick}
      className={`bg-surface-primary border border-border-default rounded-card shadow-sm transition-all duration-200 overflow-hidden ${glowStyles[glow]} ${className}`}
    >
      {(title || action) && (
        <div
          className={`px-5 py-4 border-b border-border-default flex items-center justify-between gap-4 ${headerClassName}`}
        >
          <div>
            {typeof title === "string" ? (
              <h3 className="text-base font-semibold text-text-primary tracking-tight">
                {title}
              </h3>
            ) : (
              title
            )}
            {subtitle && (
              <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
            )}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
};
