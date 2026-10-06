import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/common/Button";

export interface ErrorStateProps {
  title?: string;
  message?: string;
  errorCode?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Telemetry Acquisition Failure",
  message = "An error occurred while communicating with the forensic API backend or database.",
  errorCode,
  onRetry,
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-10 text-center rounded-card border border-status-critical/30 bg-status-critical/5 ${className}`}
      role="alert"
    >
      <div className="p-3 rounded-full bg-status-critical/15 text-status-critical mb-4 shadow-glow-critical">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h4 className="text-base font-semibold text-text-primary">{title}</h4>
      <p className="text-xs text-text-secondary mt-1.5 max-w-md">{message}</p>
      {errorCode && (
        <span className="mt-2 text-[11px] font-mono px-2 py-0.5 rounded bg-bg-secondary text-status-critical border border-status-critical/20">
          CODE: {errorCode}
        </span>
      )}
      {onRetry && (
        <div className="mt-5">
          <Button
            variant="secondary"
            size="sm"
            onClick={onRetry}
            icon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Retry Request
          </Button>
        </div>
      )}
    </div>
  );
};
