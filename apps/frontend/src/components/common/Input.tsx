import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  leadingIcon,
  trailingIcon,
  className = "",
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-xs font-medium text-text-secondary mb-1.5"
        >
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {leadingIcon && (
          <div className="absolute left-3 flex items-center pointer-events-none text-text-muted">
            {leadingIcon}
          </div>
        )}
        <input
          id={inputId}
          className={`w-full bg-bg-secondary text-text-primary text-sm rounded-lg border transition-colors duration-200 placeholder:text-text-disabled focus:outline-none focus:border-border-active focus:ring-1 focus:ring-border-active disabled:opacity-50 disabled:cursor-not-allowed ${
            leadingIcon ? "pl-9" : "pl-3.5"
          } ${trailingIcon ? "pr-9" : "pr-3.5"} py-2 ${
            error
              ? "border-status-critical focus:border-status-critical focus:ring-status-critical"
              : "border-border-default hover:border-border-default/80"
          } ${className}`}
          {...props}
        />
        {trailingIcon && (
          <div className="absolute right-3 flex items-center text-text-muted">
            {trailingIcon}
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-xs text-status-critical">{error}</p>}
      {!error && helperText && (
        <p className="mt-1 text-xs text-text-muted">{helperText}</p>
      )}
    </div>
  );
};
