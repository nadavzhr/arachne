/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
    './index.html',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      screens: {
        "xs": "420px",
      },
      colors: {
        "primary": "rgb(var(--arachne-primary) / <alpha-value>)",
        "arachne-bg": "rgb(var(--arachne-bg) / <alpha-value>)",
        "arachne-surface": "rgb(var(--arachne-surface) / <alpha-value>)",
        "arachne-surface-alt": "rgb(var(--arachne-surface-alt) / <alpha-value>)",
        "arachne-text": "rgb(var(--arachne-text) / <alpha-value>)",
        "arachne-muted": "rgb(var(--arachne-muted) / <alpha-value>)",
        "arachne-border": "rgb(var(--arachne-border) / <alpha-value>)",
        "arachne-code-bg": "rgb(var(--arachne-code-bg) / <alpha-value>)",
        "arachne-code-text": "rgb(var(--arachne-code-text) / <alpha-value>)",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
      },
      fontFamily: {
        "display": ["Syne", "sans-serif"],
        "body": ["Geist", "sans-serif"],
        "mono": ["Geist Mono", "monospace"]
      },
      borderRadius: {
        "sm": "4px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
        "2xl": "24px",
      },
    },
  },
  plugins: [],
}

