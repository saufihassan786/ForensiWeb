/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Core Surface & Background Palette
        "bg-primary": "#050B14",
        "bg-secondary": "#08111F",
        "bg-tertiary": "#0C1728",
        "surface-primary": "#0F1B2D",
        "surface-secondary": "#132238",
        "surface-hover": "#172A43",
        "border-default": "#1E3552",
        "border-active": "#2B6FFF",

        // Primary Accent Palette
        "accent-blue": "#2F80FF",
        "accent-blue-light": "#4DA3FF",
        "accent-cyan": "#22D3EE",
        "accent-cyan-light": "#67E8F9",
        "accent-indigo": "#6366F1",
        "accent-violet": "#8B5CF6",

        // Text Palette
        "text-primary": "#F8FAFC",
        "text-secondary": "#CBD5E1",
        "text-muted": "#94A3B8",
        "text-disabled": "#64748B",
        "text-inverse": "#020617",

        // Security State Palette
        "status-critical": "#EF4444",
        "status-high": "#F97316",
        "status-medium": "#F59E0B",
        "status-low": "#EAB308",
        "status-info": "#38BDF8",
        "status-success": "#22C55E",
        "status-neutral": "#64748B",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["'JetBrains Mono'", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      borderRadius: {
        card: "12px",
      },
      boxShadow: {
        "glow-blue": "0 0 15px rgba(47, 128, 255, 0.35)",
        "glow-cyan": "0 0 15px rgba(34, 211, 238, 0.35)",
        "glow-violet": "0 0 15px rgba(139, 92, 246, 0.35)",
        "glow-critical": "0 0 15px rgba(239, 68, 68, 0.45)",
      },
    },
  },
  plugins: [],
};
