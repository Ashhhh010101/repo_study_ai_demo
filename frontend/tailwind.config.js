/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2937",
        sand: "#f5efe6",
        ember: "#b45309",
        moss: "#3f6212",
        slate: "#64748b"
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["'Trebuchet MS'", "sans-serif"]
      },
      boxShadow: {
        panel: "0 12px 40px rgba(15, 23, 42, 0.12)"
      }
    }
  },
  plugins: []
};
