import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        blurple: "#5865F2",
        discord: "#313338",
        "discord-dark": "#2b2d31",
        "discord-darker": "#1e1f22",
        "discord-input": "#1e1f22",
        "safeword-green": "#57F287",
        "safeword-yellow": "#FEE75C",
        "safeword-red": "#ED4245",
        "safeword-pink": "#EB459E",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};

export default config;
