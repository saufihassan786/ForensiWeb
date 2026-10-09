import React from "react";

export interface BrandLogoProps {
  /** Size variant */
  size?: "sm" | "md" | "lg" | "xl";
  /** Layout orientation: horizontal (side-by-side) or stacked (centered shield on top) */
  layout?: "horizontal" | "stacked";
  /** Whether to render the brand text beside/under the logo */
  showText?: boolean;
  /** Whether to render the 3-part tagline */
  showTagline?: boolean;
  /** Whether the logo is interactive (clickable, hover glow, cursor pointer) */
  interactive?: boolean;
  /** Callback fired when the logo is clicked */
  onClick?: () => void;
  /** Tooltip hint when hovering */
  title?: string;
  /** Extra class names */
  className?: string;
  /** Optional variant compatibility */
  variant?: "hybrid" | "vector" | "full-image";
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  size = "md",
  layout = "horizontal",
  showText = true,
  showTagline = false,
  interactive = true,
  onClick,
  title = "ForensiWeb — Go to Overview",
  className = "",
  variant: _variant = "vector",
}) => {
  const handleClick = (e: React.MouseEvent) => {
    if (onClick) {
      e.preventDefault();
      onClick();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (interactive && onClick && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onClick();
    }
  };

  // Dimensions for shield SVG — using standard Tailwind dimensions
  const iconDimensions = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-14 h-14",
    xl: "w-20 h-20 sm:w-24 sm:h-24",
  }[size];

  const textSize = {
    sm: "text-sm",
    md: "text-lg",
    lg: "text-2xl",
    xl: "text-3xl sm:text-4xl",
  }[size];

  const taglineSize = {
    sm: "text-[7px] tracking-[0.14em]",
    md: "text-[8px] tracking-[0.16em]",
    lg: "text-[9.5px] tracking-[0.18em]",
    xl: "text-[9px] sm:text-[10.5px] tracking-[0.18em]",
  }[size];

  const isStacked = layout === "stacked";

  return (
    <div
      role={interactive && onClick ? "button" : undefined}
      tabIndex={interactive && onClick ? 0 : undefined}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      title={interactive ? title : undefined}
      aria-label="ForensiWeb Command Center"
      className={`inline-flex ${
        isStacked ? "flex-col items-center text-center gap-2" : "items-center gap-3"
      } select-none group transition-all duration-200 outline-none ${
        interactive
          ? "cursor-pointer hover:opacity-95 focus-visible:ring-2 focus-visible:ring-accent-cyan/60 rounded-lg"
          : ""
      } ${className}`}
    >
      {/* Pure Vector Shield Emblem — 100% Free-standing, Transparent, Zero Square Borders or Boxes */}
      <div className={`relative shrink-0 flex items-center justify-center ${iconDimensions}`}>
        <svg
          viewBox="0 0 100 110"
          className="w-full h-full drop-shadow-[0_0_8px_rgba(34,211,238,0.4)] dark:drop-shadow-[0_0_14px_rgba(34,211,238,0.7)] group-hover:scale-105 transition-transform duration-300"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Dynamic Crest Gradient: Electric Cyan into Vivid Royal Blue */}
            <linearGradient id="forensi_crest" x1="10" y1="4" x2="90" y2="104" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#00F0FF" />
              <stop offset="45%" stopColor="#0091FF" />
              <stop offset="100%" stopColor="#0052FF" />
            </linearGradient>

            {/* F Monogram Gradient */}
            <linearGradient id="forensi_f" x1="30" y1="30" x2="88" y2="86" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="50%" stopColor="#00D2FF" />
              <stop offset="100%" stopColor="#1D4ED8" />
            </linearGradient>

            {/* Lower Dynamic Accent Facet */}
            <linearGradient id="forensi_accent" x1="40" y1="65" x2="84" y2="98" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#00F0FF" />
              <stop offset="100%" stopColor="#2563EB" />
            </linearGradient>
          </defs>

          {/* Left & Upper Shield Outer Crest Wing */}
          <path
            d="M 50 4 L 88 18 V 28 L 50 14 L 20 25 C 18 48 24 72 44 92 L 44 102 C 16 80 10 52 10 18 Z"
            fill="url(#forensi_crest)"
          />

          {/* Stylized 'F' Monogram Core */}
          <path
            d="M 32 32 C 32 30 34 28 36 28 H 88 V 40 H 45 V 50 H 82 V 62 H 45 V 86 H 32 Z"
            fill="url(#forensi_f)"
          />

          {/* Dynamic Lower Right Shield Wing */}
          <path
            d="M 50 104 L 84 70 L 76 70 L 50 96 L 44 88 V 98 Z"
            fill="url(#forensi_accent)"
          />
        </svg>
      </div>

      {/* Brand Typography — Fully responsive to dark and light (white) themes */}
      {showText && (
        <div className={`flex flex-col ${isStacked ? "items-center" : "justify-center"} min-w-0 max-w-full`}>
          <div className="flex items-baseline tracking-tight">
            {/* 'Forensi' is deep charcoal slate in white theme, crisp brilliant white in dark theme */}
            <span
              className={`font-brand font-black text-slate-900 dark:text-white transition-colors tracking-tight ${textSize}`}
            >
              Forensi
            </span>
            {/* 'Web' is rich high-contrast oceanic cyan in white theme, electric neon cyan in dark theme */}
            <span
              className={`font-brand font-black text-[#0284c7] dark:text-[#22d3ee] dark:drop-shadow-[0_0_12px_rgba(34,211,238,0.55)] transition-colors tracking-tight ${textSize}`}
            >
              Web
            </span>
          </div>

          {/* Official Tagline — strictly single line fitting underneath the brand name */}
          {showTagline && (
            <div className="w-full mt-1 flex justify-center overflow-hidden">
              <span
                className={`font-sans font-bold uppercase text-slate-600 dark:text-slate-300 transition-colors whitespace-nowrap overflow-hidden text-ellipsis ${taglineSize}`}
              >
                DIGITAL FORENSICS <span className="text-[#0284c7] dark:text-accent-cyan mx-0.5">|</span> CYBERSECURITY{" "}
                <span className="text-[#0284c7] dark:text-accent-cyan mx-0.5">|</span> INVESTIGATION
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
