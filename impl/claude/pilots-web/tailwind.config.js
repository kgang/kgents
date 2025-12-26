/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    // Include shared-primitives components
    '../shared-primitives/src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Living Earth palette from shared-primitives
        bark: '#1C1917',
        lantern: '#FAFAF9',
        sand: '#A8A29E',
        clay: '#78716C',
        sage: '#A3E635',
        amber: '#FBBF24',
        rust: '#C2410C',
      },
      animation: {
        'fade-in': 'fadeIn 200ms ease-out',
        'grow-in': 'growIn 300ms ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        growIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
};
