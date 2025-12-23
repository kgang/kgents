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
  // ==========================================================================
  // STARK BIOME: BIOLUMINESCENT BREATHING
  // "Sustained glow with ripple" — 70% peak, whisper fluctuations
  // Amplitude -65% total (almost imperceptible)
  // ==========================================================================

  // ==========================================================================
  // CALMING BREATH: Asymmetric timing inspired by 4-7-8 breathing
  // Pattern: gentle rise (25%) → brief hold (10%) → slow fall (50%) → rest (15%)
  // Subtler amplitude, organic rhythm
  // ==========================================================================

  // Breathe subtle (ambient elements — whisper-quiet presence)
  // Opacity: 0.985 ↔ 1.0 (1.5% variation — barely perceptible)
  breathe: {
    // Rest (0-15%): stillness before inhale
    '0%': { opacity: '0.985' },
    '5%': { opacity: '0.985' },
    '10%': { opacity: '0.986' },
    '15%': { opacity: '0.987' },
    // Gentle rise (15-40%): soft inhale
    '20%': { opacity: '0.990' },
    '25%': { opacity: '0.994' },
    '30%': { opacity: '0.997' },
    '35%': { opacity: '0.999' },
    '40%': { opacity: '1' },
    // Brief hold (40-50%): moment of fullness
    '45%': { opacity: '1' },
    '50%': { opacity: '1' },
    // Slow release (50-95%): long, calming exhale
    '55%': { opacity: '0.999' },
    '60%': { opacity: '0.997' },
    '65%': { opacity: '0.995' },
    '70%': { opacity: '0.993' },
    '75%': { opacity: '0.991' },
    '80%': { opacity: '0.989' },
    '85%': { opacity: '0.987' },
    '90%': { opacity: '0.986' },
    '95%': { opacity: '0.985' },
    // Return to rest
    '100%': { opacity: '0.985' },
  },

  // Breathe for living elements (visible but calming)
  // Opacity: 0.94 ↔ 1.0 (6% variation — noticeable but gentle)
  breatheAlive: {
    // Rest
    '0%': { opacity: '0.94' },
    '5%': { opacity: '0.94' },
    '10%': { opacity: '0.942' },
    '15%': { opacity: '0.946' },
    // Gentle rise
    '20%': { opacity: '0.955' },
    '25%': { opacity: '0.970' },
    '30%': { opacity: '0.985' },
    '35%': { opacity: '0.995' },
    '40%': { opacity: '1' },
    // Brief hold
    '45%': { opacity: '1' },
    '50%': { opacity: '1' },
    // Slow release
    '55%': { opacity: '0.995' },
    '60%': { opacity: '0.988' },
    '65%': { opacity: '0.980' },
    '70%': { opacity: '0.972' },
    '75%': { opacity: '0.963' },
    '80%': { opacity: '0.955' },
    '85%': { opacity: '0.948' },
    '90%': { opacity: '0.943' },
    '95%': { opacity: '0.940' },
    '100%': { opacity: '0.94' },
  },

  // Glow pulse (earned moments — warmth emerging, then gently fading)
  // Opacity: 0.96 ↔ 1.0, brightness: 1.0 ↔ 1.012 (subtle warmth)
  glowPulse: {
    // Rest
    '0%': { opacity: '0.96', filter: 'brightness(1)' },
    '5%': { opacity: '0.96', filter: 'brightness(1)' },
    '10%': { opacity: '0.962', filter: 'brightness(1.001)' },
    '15%': { opacity: '0.966', filter: 'brightness(1.002)' },
    // Gentle rise
    '20%': { opacity: '0.974', filter: 'brightness(1.004)' },
    '25%': { opacity: '0.984', filter: 'brightness(1.007)' },
    '30%': { opacity: '0.993', filter: 'brightness(1.010)' },
    '35%': { opacity: '0.998', filter: 'brightness(1.011)' },
    '40%': { opacity: '1', filter: 'brightness(1.012)' },
    // Brief hold — moment of warmth
    '45%': { opacity: '1', filter: 'brightness(1.012)' },
    '50%': { opacity: '1', filter: 'brightness(1.012)' },
    // Slow release
    '55%': { opacity: '0.998', filter: 'brightness(1.011)' },
    '60%': { opacity: '0.993', filter: 'brightness(1.009)' },
    '65%': { opacity: '0.986', filter: 'brightness(1.007)' },
    '70%': { opacity: '0.979', filter: 'brightness(1.005)' },
    '75%': { opacity: '0.973', filter: 'brightness(1.004)' },
    '80%': { opacity: '0.968', filter: 'brightness(1.002)' },
    '85%': { opacity: '0.964', filter: 'brightness(1.001)' },
    '90%': { opacity: '0.961', filter: 'brightness(1.0005)' },
    '95%': { opacity: '0.96', filter: 'brightness(1)' },
    '100%': { opacity: '0.96', filter: 'brightness(1)' },
  },

  pulse: {
    '0%, 100%': { opacity: '1' },
    '50%': { opacity: '0.7' },
  },

  // Data pulse (single pulse on event — not looping)
  dataPulse: {
    '0%': { opacity: '0.5', transform: 'scale(0.98)' },
    '40%': { opacity: '1', transform: 'scale(1.01)' },
    '100%': { opacity: '0.5', transform: 'scale(0.98)' },
  },
};

// =============================================================================
// ANIMATION UTILITIES
// Stark Biome: mechanical precision for transitions, organic for breathing
// =============================================================================

// Custom timing function for 90/10 breathing:
// Slow start, brief peak, gentle settle — like moss exhaling
const BIOME_BREATHE = 'cubic-bezier(0.4, 0, 0.1, 1)';

const animations = {
  // Mechanical transitions (instant, no organic feel)
  'fade-in': 'fadeIn 250ms ease-out',
  'fade-out': 'fadeOut 200ms ease-in',
  'slide-up': 'slideUp 250ms ease-out',
  'slide-down': 'slideDown 250ms ease-out',
  'scale-in': 'scaleIn 250ms ease-out',
  emerge: 'emerge 250ms ease-out',
  pop: 'pop 200ms ease-out',
  shake: 'shake 500ms ease-in-out',

  // Calming breath animations
  // Linear timing since easing is baked into keyframes
  breathe: `breathe 8.1s linear infinite`,
  'breathe-alive': `breatheAlive 6.75s linear infinite`,
  'glow-pulse': `glowPulse 5.4s linear infinite`,
  'pulse-slow': 'pulse 5.3s ease-in-out infinite',

  // Single-shot data pulse (not looping)
  'data-pulse': 'dataPulse 1.1s ease-out',
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
        // STARK: Organic breathing — slow start, brief peak, gentle settle
        biome: 'cubic-bezier(0.4, 0, 0.1, 1)',
        // NOTE: bounce removed for Stark Biome
      },
    },
  },
  plugins: [],
};
