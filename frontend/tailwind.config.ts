import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: "#FFFFFF",
        "surface-muted": "#F1F5F9",
        "surface-dark": "#0F172A",
        border: "#E2E8F0",
        "border-strong": "#CBD5E1",
        primary: "#0F172A",
        "primary-accent": "#1D4ED8",
        "trust-blue": "#2563EB",
        "trust-blue-light": "#EFF6FF",
        "brand-teal": "#0D9488",
        "official-green": "#15803D",
        "platform-slate": "#475569",
        "pdf-amber": "#B45309",
        "refusal-amber": "#92400E",
        "refusal-bg": "#FFFBEB",
        "missing-gray": "#64748B",
        "error-red": "#B91C1C",
        // shadcn compat
        foreground: "#0F172A",
        card: { DEFAULT: "#FFFFFF", foreground: "#0F172A" },
        popover: { DEFAULT: "#FFFFFF", foreground: "#0F172A" },
        secondary: { DEFAULT: "#F1F5F9", foreground: "#0F172A" },
        muted: { DEFAULT: "#F1F5F9", foreground: "#64748B" },
        accent: { DEFAULT: "#EFF6FF", foreground: "#1D4ED8" },
        destructive: { DEFAULT: "#B91C1C", foreground: "#FFFFFF" },
        input: "#E2E8F0",
        ring: "#2563EB",
      },
      fontFamily: {
        sans: ["Inter", "IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      borderRadius: {
        card: "12px",
        source: "10px",
        button: "8px",
        chip: "999px",
        drawer: "16px",
        lg: "10px",
        md: "8px",
        sm: "6px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        source: "0 2px 6px rgba(0,0,0,0.06)",
        drawer: "0 8px 30px rgba(0,0,0,0.12)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.08)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "helix-scroll": {
          "0%": { strokeDashoffset: "0" },
          "100%": { strokeDashoffset: "-200" },
        },
        "ticker-scroll": {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        "ecg-draw": {
          "0%": { strokeDashoffset: "1200" },
          "100%": { strokeDashoffset: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "helix-scroll": "helix-scroll 8s linear infinite",
        "ticker-scroll": "ticker-scroll 20s linear infinite",
        "ecg-draw": "ecg-draw 3s linear infinite",
      },
    },
  },
  plugins: [animate],
};
export default config;
