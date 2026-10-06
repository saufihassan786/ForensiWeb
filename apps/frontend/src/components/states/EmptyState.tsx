import React from "react";
import { FolderSearch } from "lucide-react";
import { Button } from "@/components/common/Button";

export interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No Forensic Artifacts Found",
  description = "No items match your active filters or no evidence has been registered yet.",
  icon,
  actionLabel,
  onAction,
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center rounded-card border border-dashed border-border-default bg-surface-primary/50 ${className}`}
    >
      <div className="p-3.5 rounded-full bg-surface-secondary border border-border-default text-text-muted mb-4">
        {icon || <FolderSearch className="w-8 h-8 text-accent-blue" />}
      </div>
      <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
      <p className="text-xs text-text-muted mt-1 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-5">
          <Button variant="secondary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};
