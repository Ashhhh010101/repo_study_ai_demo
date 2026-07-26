/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#070a0f",
        panel: "#0c1118",
        "panel-soft": "#111821",
        line: "#202a36",
        ink: "#e8eef7",
        "ink-soft": "#b7c1cf",
        muted: "#7e8b9d",
        accent: "#9dfc75",
        "accent-bright": "#b5ff96",
        cyan: "#6edcff",
        danger: "#ff7f8d"
      },
      fontFamily: {
        display: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["'SFMono-Regular'", "Consolas", "'Liberation Mono'", "monospace"]
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0, 0, 0, 0.35)",
        glow: "0 0 24px rgba(157, 252, 117, 0.18)"
      },
      keyframes: {
        scan: {
          "0%": { transform: "translateX(-110%)" },
          "50%": { transform: "translateX(210%)" },
          "100%": { transform: "translateX(210%)" }
        }
      }
    }
  },
  plugins: []
};
