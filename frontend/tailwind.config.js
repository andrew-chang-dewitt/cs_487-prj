/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // "Paper" — warm off-white backgrounds reminiscent of newsprint
        paper: {
          50: "#fbf9f4",
          100: "#f5f1e8",
          200: "#e8e0cf",
        },
        // "Ink" — deep blue-black for text and dark surfaces
        ink: {
          50: "#f3f3f1",
          100: "#d9d8d3",
          400: "#5a5a55",
          600: "#2d2d2a",
          800: "#1a1a18",
          900: "#0d0d0c",
        },
        // Accent — deep moss / forest, the single accent color
        moss: {
          50: "#eef2ec",
          400: "#5a7a52",
          500: "#3f5a37",
          600: "#2d4127",
          700: "#1f2e1a",
        },
        // Signal — terracotta for negative deltas (spending, errors, danger)
        clay: {
          400: "#c87a5e",
          500: "#a85a3e",
          600: "#7e3f29",
        },
      },
      fontFamily: {
        // Display: classical serif for numbers, headings, brand
        display: ['"Cormorant Garamond"', "Georgia", "serif"],
        // Body: humanist sans for UI chrome
        sans: ['"Inter Tight"', "system-ui", "sans-serif"],
        // Mono: tabular figures for ledger/transaction views
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      fontFeatureSettings: {
        // Tabular figures for amounts so columns line up
        tnum: '"tnum"',
      },
      letterSpacing: {
        tightest: "-0.04em",
      },
      boxShadow: {
        // Soft, low-intensity shadows — newspaper feel, not webby
        ledger: "0 1px 0 0 rgb(45 45 42 / 0.08)",
        card: "0 2px 0 0 rgb(45 45 42 / 0.06), 0 0 0 1px rgb(45 45 42 / 0.05)",
      },
    },
  },
  plugins: [],
};
