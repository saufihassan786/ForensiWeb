/**
 * ForensiWeb Design System Tokens & Type Definitions
 * Source of truth: docs/design.md
 */

export const COLOR_TOKENS = {
  // Core Surfaces
  bgPrimary: "#050B14",
  bgSecondary: "#08111F",
  bgTertiary: "#0C1728",
  surfacePrimary: "#0F1B2D",
  surfaceSecondary: "#132238",
  surfaceHover: "#172A43",
  borderDefault: "#1E3552",
  borderActive: "#2B6FFF",

  // Accents
  accentBlue: "#2F80FF",
  accentBlueLight: "#4DA3FF",
  accentCyan: "#22D3EE",
  accentCyanLight: "#67E8F9",
  accentIndigo: "#6366F1",
  accentViolet: "#8B5CF6",

  // Text
  textPrimary: "#F8FAFC",
  textSecondary: "#CBD5E1",
  textMuted: "#94A3B8",
  textDisabled: "#64748B",
  textInverse: "#020617",

  // Status
  statusCritical: "#EF4444",
  statusHigh: "#F97316",
  statusMedium: "#F59E0B",
  statusLow: "#EAB308",
  statusInfo: "#38BDF8",
  statusSuccess: "#22C55E",
  statusNeutral: "#64748B",
} as const;

export type SeverityLevel = "critical" | "high" | "medium" | "low" | "informational";
export type StatusState = "active" | "processing" | "completed" | "failed" | "verified" | "acquired";
export type AttackStage =
  | "RECON"
  | "LFI"
  | "LOG_POISONING"
  | "RCE"
  | "POST_EXPLOITATION"
  | "PRIVILEGE_ESCALATION"
  | "IMPACT";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "destructive";
export type ButtonSize = "sm" | "md" | "lg";
