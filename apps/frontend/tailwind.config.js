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
        // Core Surface & Background Palette mapped to dynamic CSS variables
        "bg-primary": "var(--bg-primary, #050B14)",
        "bg-secondary": "var(--bg-secondary, #0B1322)",
        "bg-tertiary": "var(--bg-tertiary, #111C30)",
        "surface-primary": "var(--surface-primary, #0E1726)",
        "surface-secondary": "var(--surface-secondary, #142036)",
        "surface-hover": "var(--surface-hover, #1C2B46)",
        "border-default": "var(--border-default, #1E2D4A)",
        "border-active": "var(--border-active, #2F80FF)",

        // Primary Accent Palette
        "accent-blue": "var(--accent-blue, #2F80FF)",
        "accent-blue-light": "var(--accent-blue-light, #5CA0FF)",
        "accent-cyan": "var(--accent-cyan, #22D3EE)",
        "accent-cyan-light": "var(--accent-cyan-light, #67E8F9)",
        "accent-indigo": "var(--accent-indigo, #6366F1)",
        "accent-violet": "var(--accent-violet, #8B5CF6)",

        // Text Palette
        "text-primary": "var(--text-primary, #F8FAFC)",
        "text-secondary": "var(--text-secondary, #94A3B8)",
        "text-muted": "var(--text-muted, #64748B)",
        "text-disabled": "var(--text-disabled, #475569)",
        "text-inverse": "var(--text-inverse, #050B14)",

        // Security State Palette
        "status-critical": "var(--status-critical, #EF4444)",
        "status-high": "var(--status-high, #F97316)",
        "status-medium": "var(--status-medium, #EAB308)",
        "status-low": "var(--status-low, #3B82F6)",
        "status-info": "var(--status-info, #06B6D4)",
        "status-success": "var(--status-success, #10B981)",
        "status-neutral": "var(--status-neutral, #64748B)",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        brand: ["Outfit", "'Plus Jakarta Sans'", "Inter", "-apple-system", "sans-serif"],
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
