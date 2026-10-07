import { useEffect, useState } from "react";

export type ThemeMode = "dark" | "light";

export function useTheme() {
  const [theme, setTheme] = useState<ThemeMode>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("forensiweb_theme");
      if (saved === "light" || saved === "dark") {
        return saved;
      }
      if (typeof window.matchMedia === "function") {
        return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
      }
      return "dark";
    }
    return "dark";
  });

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute("data-theme", theme);
    if (theme === "dark") {
      root.classList.add("dark");
      root.classList.remove("light");
    } else {
      root.classList.add("light");
      root.classList.remove("dark");
    }
    localStorage.setItem("forensiweb_theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return { theme, toggleTheme, setTheme };
}
