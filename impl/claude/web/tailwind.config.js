/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Agent Town brand colors
        'town-bg': '#1a1a2e',
        'town-surface': '#16213e',
        'town-accent': '#0f3460',
        'town-highlight': '#e94560',
        // Archetype colors
        'archetype-builder': '#3b82f6',
        'archetype-trader': '#f59e0b',
        'archetype-healer': '#22c55e',
        'archetype-scholar': '#8b5cf6',
        'archetype-watcher': '#6b7280',
        // Phase colors
        'phase-morning': '#fbbf24',
        'phase-afternoon': '#fb923c',
        'phase-evening': '#a855f7',
        'phase-night': '#1e3a5f',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
