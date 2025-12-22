/** @type {import('tailwindcss').Config} */

/**
 * kgents Tailwind Configuration — STARK BIOME EDITION
 *
 * "The frame is humble. The content glows."
 * 90% Steel (cool industrial) / 10% Life (organic accents)
 *
 * Design tokens derived from the visual system.
 * @see docs/creative/visual-system.md
 * @see creative/crown-jewels-genesis-moodboard.md
 * @see plans/stark-biome-refactor.md
 */

// =============================================================================
// STARK BIOME COLOR SYSTEM
// =============================================================================

// Steel Foundation (backgrounds, frames, containers — the 90%)
const steelColors = {
  'steel-obsidian': '#0A0A0C', // Deepest background
  'steel-carbon': '#141418', // Card backgrounds
  'steel-slate': '#1C1C22', // Elevated surfaces
  'steel-gunmetal': '#28282F', // Borders, dividers
  'steel-zinc': '#3A3A44', // Muted text, inactive states
};

// Soil Undertones (warm secondary surfaces)
const soilColors = {
  'soil-loam': '#1A1512',
  'soil-humus': '#2D221A',
  'soil-peat': '#3D3028',
  'soil-earth': '#524436',
  'soil-clay': '#685844',
};

// Living Accent (success, growth, life emerging — part of the 10%)
const lifeColors = {
  'life-moss': '#1A2E1A',
  'life-fern': '#2E4A2E',
  'life-sage': '#4A6B4A',
  'life-mint': '#6B8B6B',
  'life-sprout': '#8BAB8B',
};

// Bioluminescent (highlights, focus, precious moments — the earned glow)
const glowColors = {
  'glow-spore': '#C4A77D',
  'glow-amber': '#D4B88C',
  'glow-light': '#E5C99D',
  'glow-lichen': '#8BA98B',
  'glow-bloom': '#9CBDA0',
};

// Jewel Identities (MUTED for Stark Biome — earned, not given)
const jewelColors = {
  'jewel-brain': '#4A6B6B', // Teal Moss — knowledge growing quietly
  'jewel-witness': '#6B6B4A', // Olive — memory preserved in amber
  'jewel-atelier': '#8B7355', // Umber — creative warmth, earned glow
  'jewel-liminal': '#5A5A6B', // Pewter — threshold between states
  // Legacy mappings (backwards compat)
  'jewel-brain-accent': '#5A7B7B',
  'jewel-brain-bg': '#3A5B5B',
  'jewel-gestalt': '#4A6B4A',
  'jewel-gestalt-accent': '#5A7B5A',
  'jewel-gestalt-bg': '#3A5B3A',
  'jewel-gardener': '#6B8B6B',
  'jewel-gardener-accent': '#7B9B7B',
  'jewel-gardener-bg': '#5A7B5A',
  'jewel-atelier-accent': '#9B8365',
  'jewel-atelier-bg': '#7B6345',
  'jewel-coalition': '#6B5A7B',
  'jewel-coalition-accent': '#7B6A8B',
  'jewel-coalition-bg': '#5B4A6B',
  'jewel-park': '#7B5A6B',
  'jewel-park-accent': '#8B6A7B',
  'jewel-park-bg': '#6B4A5B',
  'jewel-domain': '#8B5A4A',
  'jewel-domain-accent': '#9B6A5A',
  'jewel-domain-bg': '#7B4A3A',
};

// State Colors (Stark Biome: constrained to 4, muted)
const stateColors = {
  'state-healthy': '#4A6B4A', // life-sage
  'state-pending': '#C4A77D', // glow-spore
  'state-alert': '#A65D4A', // Muted rust
  'state-dormant': '#3A3A44', // steel-zinc
  // Legacy mappings
  'state-success': '#4A6B4A',
  'state-warning': '#C4A77D',
  'state-error': '#A65D4A',
  'state-info': '#4A6B6B',
};

// Surface Colors (Stark Biome steel foundation)
const surfaceColors = {
  'surface-canvas': '#0A0A0C', // steel-obsidian
  'surface-card': '#141418', // steel-carbon
  'surface-elevated': '#1C1C22', // steel-slate
};

// Agent Town Colors (legacy → redirect to steel)
const townColors = {
  'town-bg': '#0A0A0C', // → steel-obsidian
  'town-surface': '#141418', // → steel-carbon
  'town-accent': '#1C1C22', // → steel-slate
  'town-highlight': '#C4A77D', // → glow-spore (earned highlight)
};

// Archetype Colors (muted for Stark Biome)
const archetypeColors = {
  'archetype-builder': '#5A6B8B', // Muted blue-gray
  'archetype-trader': '#8B7355', // Umber
  'archetype-healer': '#4A6B4A', // life-sage
  'archetype-scholar': '#6B5A7B', // Muted violet
  'archetype-watcher': '#4A4A54', // Steel gray
};

// Phase Colors (muted for Stark Biome)
const phaseColors = {
  'phase-morning': '#8B7355', // Warm umber
  'phase-afternoon': '#7B6345', // Darker umber
  'phase-evening': '#5A5A6B', // Pewter
  'phase-night': '#1C1C22', // steel-slate
};

// =============================================================================
// STARK BIOME ANIMATION SYSTEM
// "Stillness, then life" — Motion is earned, not decorative
// =============================================================================

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
  // STARK: Emergence (fade-in, no bounce overshoot)
  emerge: {
    '0%': { opacity: '0', transform: 'scale(0.98)' },
    '100%': { opacity: '1', transform: 'scale(1)' },
  },
  // STARK: Pop simplified (no bounce, mechanical precision)
  pop: {
    '0%': { opacity: '0', transform: 'scale(0.95)' },
    '100%': { opacity: '1', transform: 'scale(1)' },
  },
  shake: {
    '0%, 100%': { transform: 'translateX(0)' },
    '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
    '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
  },
  // STARK: Breathe subtle (2% amplitude, 5s period — barely perceptible)
  breathe: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.98' },
  },
  // STARK: Breathe for living elements only (slightly more visible)
  breatheAlive: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.92' },
  },
  pulse: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.7' },
  },
  // STARK: Data pulse (single pulse on event)
  dataPulse: {
    '0%': { opacity: '0.5', transform: 'scale(0.95)' },
    '50%': { opacity: '1', transform: 'scale(1.02)' },
    '100%': { opacity: '0.5', transform: 'scale(0.95)' },
  },
};

// Animation utilities (Stark Biome: mechanical precision, no spring bounce)
const animations = {
  'fade-in': 'fadeIn 250ms ease-out',
  'fade-out': 'fadeOut 200ms ease-in',
  'slide-up': 'slideUp 250ms ease-out',
  'slide-down': 'slideDown 250ms ease-out',
  'scale-in': 'scaleIn 250ms ease-out',
  emerge: 'emerge 250ms ease-out',
  pop: 'pop 200ms ease-out',
  shake: 'shake 500ms ease-in-out',
  breathe: 'breathe 5s ease-in-out infinite',
  'breathe-alive': 'breatheAlive 4s ease-in-out infinite',
  'pulse-slow': 'pulse 3s ease-in-out infinite',
  'data-pulse': 'dataPulse 600ms ease-out',
};

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // STARK BIOME: Primary palettes
        ...steelColors,
        ...soilColors,
        ...lifeColors,
        ...glowColors,
        // Legacy/semantic (redirect to Stark equivalents)
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
      spacing: {
        'tight-xs': '3px',
        'tight-sm': '6px',
        'tight-md': '10px',
        'tight-lg': '16px',
        'tight-xl': '24px',
      },
      animation: animations,
      keyframes: keyframes,
      // Border radius scale: "Bare Edge" philosophy
      borderRadius: {
        none: '0px',
        bare: '2px',
        subtle: '3px',
        DEFAULT: '2px',
        sm: '2px',
        md: '3px',
        lg: '4px',
        xl: '6px',
        pill: '9999px',
        full: '9999px',
      },
      // Transition timing
      transitionDuration: {
        instant: '100ms',
        quick: '200ms',
        standard: '300ms',
        elaborate: '500ms',
      },
      // Transition timing functions (Stark Biome: no bounce/spring)
      transitionTimingFunction: {
        standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
        enter: 'cubic-bezier(0, 0, 0.2, 1)',
        exit: 'cubic-bezier(0.4, 0, 1, 1)',
        // NOTE: bounce removed for Stark Biome
      },
    },
  },
  plugins: [],
};
