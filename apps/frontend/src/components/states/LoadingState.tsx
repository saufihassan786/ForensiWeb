import React from "react";
import { Cpu } from "lucide-react";

export interface LoadingStateProps {
  message?: string;
  subMessage?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Processing Forensic Telemetry...",
  subMessage = "Correlating evidence events and security indicators",
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="relative mb-4">
        {/* Outer glowing pulsing ring */}
        <div className="w-14 h-14 rounded-full border-2 border-accent-cyan/30 animate-ping absolute inset-0" />
        <div className="w-14 h-14 rounded-full border-2 border-t-accent-cyan border-r-accent-blue border-b-transparent border-l-transparent animate-spin flex items-center justify-center bg-surface-primary shadow-glow-cyan">
          <Cpu className="w-6 h-6 text-accent-cyan animate-pulse" />
        </div>
      </div>
      <p className="text-sm font-semibold text-text-primary tracking-wide">
        {message}
      </p>
      {subMessage && (
        <p className="text-xs text-text-muted mt-1 max-w-sm">{subMessage}</p>
      )}
    </div>
  );
};
