/**
 * Motion Timing System
 *
 * Animation durations and easing curves for consistent motion language.
 * Fast is the default. Slow is the exception.
 *
 * @see docs/creative/motion-language.md
 */

/**
 * Animation Durations (milliseconds)
 *
 * Guidelines:
 * - instant (100ms): Micro-feedback, hover states
 * - quick (200ms): Most transitions, state changes
 * - standard (300ms): Modal appearances, page transitions
 * - elaborate (500ms): Complex sequences, celebrations
 */
export const TIMING = {
  instant: 100,
  quick: 200,
  standard: 300,
  elaborate: 500,
} as const;

export type TimingKey = keyof typeof TIMING;

/**
 * CSS Duration Strings (for inline styles)
 */
export const TIMING_CSS = {
  instant: '100ms',
  quick: '200ms',
  standard: '300ms',
  elaborate: '500ms',
} as const;

/**
 * Easing Curves (cubic-bezier values)
 *
 * Guidelines:
 * - standard: Most animations (Material Design standard)
 * - enter: Elements appearing (ease-out-like)
 * - exit: Elements leaving (ease-in-like)
 * - bounce: Celebrations, success states (overshoots)
 */
export const EASING = {
  /** Standard animation curve - gentle ease-in-out */
  standard: [0.4, 0.0, 0.2, 1] as const,
  /** Enter animations - ease-out character */
  enter: [0.0, 0.0, 0.2, 1] as const,
  /** Exit animations - ease-in character */
  exit: [0.4, 0.0, 1, 1] as const,
  /** Bouncy for celebrations */
  bounce: [0.68, -0.55, 0.265, 1.55] as const,
  /** Linear for continuous animations */
  linear: [0, 0, 1, 1] as const,
} as const;

export type EasingKey = keyof typeof EASING;

/**
 * CSS cubic-bezier strings
 */
export const EASING_CSS = {
  standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
  enter: 'cubic-bezier(0, 0, 0.2, 1)',
  exit: 'cubic-bezier(0.4, 0, 1, 1)',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  linear: 'linear',
} as const;

/**
 * Stagger Delays
 *
 * For list item animations. Index-based delays.
 */
export const STAGGER = {
  /** Fast stagger for short lists */
  fast: 30, // ms per item
  /** Standard stagger for medium lists */
  standard: 50,
  /** Slow stagger for dramatic effect */
  slow: 100,
} as const;

/**
 * Calculate stagger delay for an item
 */
export function getStaggerDelay(
  index: number,
  type: keyof typeof STAGGER = 'standard'
): number {
  return index * STAGGER[type];
}

/**
 * Precomposed Transition Strings
 *
 * Common transition combinations ready for use.
 */
export const TRANSITIONS = {
  /** Quick opacity fade */
  fadeQuick: `opacity ${TIMING_CSS.quick} ${EASING_CSS.standard}`,
  /** Standard transform */
  transformStandard: `transform ${TIMING_CSS.standard} ${EASING_CSS.standard}`,
  /** Enter animation (opacity + transform) */
  enter: `opacity ${TIMING_CSS.quick} ${EASING_CSS.enter}, transform ${TIMING_CSS.standard} ${EASING_CSS.enter}`,
  /** Exit animation */
  exit: `opacity ${TIMING_CSS.instant} ${EASING_CSS.exit}, transform ${TIMING_CSS.quick} ${EASING_CSS.exit}`,
  /** Color change */
  colorQuick: `color ${TIMING_CSS.quick} ${EASING_CSS.standard}, background-color ${TIMING_CSS.quick} ${EASING_CSS.standard}`,
  /** All properties */
  all: `all ${TIMING_CSS.standard} ${EASING_CSS.standard}`,
} as const;

/**
 * Keyframe Animation Definitions (for Tailwind or CSS-in-JS)
 */
export const KEYFRAMES = {
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
} as const;

/**
 * Tailwind animation extensions
 */
export const ANIMATION_TAILWIND_EXTENSIONS = {
  animation: {
    'fade-in': `fadeIn ${TIMING_CSS.standard} ${EASING_CSS.enter}`,
    'fade-out': `fadeOut ${TIMING_CSS.quick} ${EASING_CSS.exit}`,
    'slide-up': `slideUp ${TIMING_CSS.standard} ${EASING_CSS.enter}`,
    'slide-down': `slideDown ${TIMING_CSS.standard} ${EASING_CSS.enter}`,
    'scale-in': `scaleIn ${TIMING_CSS.standard} ${EASING_CSS.enter}`,
    pop: `pop ${TIMING_CSS.standard} ${EASING_CSS.bounce}`,
    shake: `shake ${TIMING_CSS.elaborate} ${EASING_CSS.standard}`,
    breathe: `breathe 3s ${EASING_CSS.standard} infinite`,
    'pulse-slow': `pulse 3s ${EASING_CSS.standard} infinite`,
  },
  keyframes: KEYFRAMES,
} as const;
