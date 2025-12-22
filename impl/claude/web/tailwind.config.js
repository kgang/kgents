/** @type {import('tailwindcss').Config} */

/**
 * kgents Tailwind Configuration
 *
 * Design tokens derived from the visual system.
 * @see docs/creative/visual-system.md
 */

// Crown Jewel Colors (semantic: meaning → hue)
const jewelColors = {
  // Brain: Knowledge (Cyan)
  'jewel-brain': '#06B6D4',
  'jewel-brain-accent': '#0891B2',
  'jewel-brain-bg': '#0E7490',

  // Gestalt: Growth (Green)
  'jewel-gestalt': '#22C55E',
  'jewel-gestalt-accent': '#16A34A',
  'jewel-gestalt-bg': '#15803D',

  // Gardener: Cultivation (Lime)
  'jewel-gardener': '#84CC16',
  'jewel-gardener-accent': '#65A30D',
  'jewel-gardener-bg': '#4D7C0F',

  // Atelier: Creation (Amber)
  'jewel-atelier': '#F59E0B',
  'jewel-atelier-accent': '#D97706',
  'jewel-atelier-bg': '#B45309',

  // Coalition: Collaboration (Violet)
  'jewel-coalition': '#8B5CF6',
  'jewel-coalition-accent': '#7C3AED',
  'jewel-coalition-bg': '#6D28D9',

  // Park: Drama (Pink)
  'jewel-park': '#EC4899',
  'jewel-park-accent': '#DB2777',
  'jewel-park-bg': '#BE185D',

  // Domain: Urgency (Red)
  'jewel-domain': '#EF4444',
  'jewel-domain-accent': '#DC2626',
  'jewel-domain-bg': '#B91C1C',
};

// State Colors (system feedback)
const stateColors = {
  'state-success': '#22C55E',
  'state-warning': '#F59E0B',
  'state-error': '#EF4444',
  'state-info': '#06B6D4',
  'state-pending': '#64748B',
};

// Surface Colors (dark mode first)
const surfaceColors = {
  'surface-canvas': '#0F172A', // gray-900
  'surface-card': '#1E293B', // gray-800
  'surface-elevated': '#334155', // gray-700
};

// Agent Town Colors (legacy, kept for compatibility)
const townColors = {
  'town-bg': '#1a1a2e',
  'town-surface': '#16213e',
  'town-accent': '#0f3460',
  'town-highlight': '#e94560',
};

// Archetype Colors
const archetypeColors = {
  'archetype-builder': '#3B82F6',
  'archetype-trader': '#F59E0B',
  'archetype-healer': '#22C55E',
  'archetype-scholar': '#8B5CF6',
  'archetype-watcher': '#6B7280',
};

// Phase Colors (time of day)
const phaseColors = {
  'phase-morning': '#FBBF24',
  'phase-afternoon': '#FB923C',
  'phase-evening': '#A855F7',
  'phase-night': '#1E3A5F',
};

// Animation keyframes
const keyframes = {
  fadeIn: {
    '0%': { opacity: '0' },
    '100%': { opacity: '1' },
  },
  fadeOut: {
    '0%': { opacity: '1' },
    '100%': { opacity: '0' },
  },
  slideUp: {
    '0%': { opacity: '0', transform: 'translateY(10px)' },
    '100%': { opacity: '1', transform: 'translateY(0)' },
  },
  slideDown: {
    '0%': { opacity: '0', transform: 'translateY(-10px)' },
    '100%': { opacity: '1', transform: 'translateY(0)' },
  },
  scaleIn: {
    '0%': { opacity: '0', transform: 'scale(0.95)' },
    '100%': { opacity: '1', transform: 'scale(1)' },
  },
  pop: {
    '0%': { transform: 'scale(0.8)', opacity: '0' },
    '50%': { transform: 'scale(1.1)' },
    '100%': { transform: 'scale(1)', opacity: '1' },
  },
  shake: {
    '0%, 100%': { transform: 'translateX(0)' },
    '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
    '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
  },
  breathe: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.7' },
  },
  pulse: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.5' },
  },
};

// Animation utilities
const animations = {
  'fade-in': 'fadeIn 300ms cubic-bezier(0, 0, 0.2, 1)',
  'fade-out': 'fadeOut 200ms cubic-bezier(0.4, 0, 1, 1)',
  'slide-up': 'slideUp 300ms cubic-bezier(0, 0, 0.2, 1)',
  'slide-down': 'slideDown 300ms cubic-bezier(0, 0, 0.2, 1)',
  'scale-in': 'scaleIn 300ms cubic-bezier(0, 0, 0.2, 1)',
  pop: 'pop 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  shake: 'shake 500ms cubic-bezier(0.4, 0, 0.2, 1)',
  breathe: 'breathe 3s cubic-bezier(0.4, 0, 0.2, 1) infinite',
  'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
};

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ...jewelColors,
        ...stateColors,
        ...surfaceColors,
        ...townColors,
        ...archetypeColors,
        ...phaseColors,
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      // Spacing: "Tight Frame" semantic tokens
      // Use these for intentionally tighter spacing.
      // Default Tailwind scale preserved for compatibility.
      spacing: {
        'tight-xs': '3px', // Micro gaps
        'tight-sm': '6px', // Tight groupings
        'tight-md': '10px', // Standard tight
        'tight-lg': '16px', // Comfortable tight
        'tight-xl': '24px', // Spacious tight
      },
      animation: animations,
      keyframes: keyframes,
      // Border radius scale: "Bare Edge" philosophy
      // The container is humble; the content glows.
      // Sharp frames make warm elements pop.
      borderRadius: {
        none: '0px', // Panels, canvas — invisible frame
        bare: '2px', // Cards, containers — just enough to not cut
        subtle: '3px', // Interactive surfaces — softened for touch
        DEFAULT: '2px', // Default to bare (was 4px)
        sm: '2px', // Alias for bare
        md: '3px', // Alias for subtle (was 8px)
        lg: '4px', // Slightly softer (was 12px) — use sparingly
        xl: '6px', // Soft accent (was 16px) — rare
        pill: '9999px', // Badges, tags — finite, precious
        full: '9999px', // Alias for pill
      },
      // Transition timing
      transitionDuration: {
        instant: '100ms',
        quick: '200ms',
        standard: '300ms',
        elaborate: '500ms',
      },
      // Transition timing functions
      transitionTimingFunction: {
        standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
        enter: 'cubic-bezier(0, 0, 0.2, 1)',
        exit: 'cubic-bezier(0.4, 0, 1, 1)',
        bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
    },
  },
  plugins: [],
};
