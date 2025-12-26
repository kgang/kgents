/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../shared-primitives/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bark: '#1C1917',
        lantern: '#FAFAF9',
        sand: '#A8A29E',
        clay: '#78716C',
        sage: '#A3E635',
        amber: '#FBBF24',
        rust: '#C2410C',
      },
    },
  },
  plugins: [],
};
