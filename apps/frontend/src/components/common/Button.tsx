import React from "react";
import { ButtonVariant, ButtonSize } from "@/types/tokens";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  icon,
  className = "",
  disabled,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue disabled:opacity-50 disabled:cursor-not-allowed select-none";

  const sizeStyles: Record<ButtonSize, string> = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-5 py-2.5 text-base gap-2.5",
  };

  const variantStyles: Record<ButtonVariant, string> = {
    primary:
      "bg-accent-blue hover:bg-accent-blue-light text-white shadow-sm hover:shadow-glow-blue border border-accent-blue/30 active:scale-[0.98]",
    secondary:
      "bg-surface-secondary hover:bg-surface-hover text-text-primary border border-border-default hover:border-border-active active:scale-[0.98]",
    ghost:
      "bg-transparent hover:bg-surface-hover text-text-secondary hover:text-text-primary active:scale-[0.98]",
    destructive:
      "bg-status-critical/15 hover:bg-status-critical/25 text-status-critical border border-status-critical/30 hover:shadow-glow-critical active:scale-[0.98]",
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        icon && <span className="flex-shrink-0">{icon}</span>
      )}
      {children}
    </button>
  );
};
