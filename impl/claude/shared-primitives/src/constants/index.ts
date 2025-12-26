/**
 * Design Constants
 *
 * Shared design tokens for pilots.
 */

/** Living Earth palette - warm earthy tones */
export const LIVING_EARTH = {
  bark: '#1C1917',      // Deep bark background
  lantern: '#FAFAF9',   // Warm white for text
  sand: '#A8A29E',      // Neutral gray
  clay: '#78716C',      // Muted clay
  sage: '#A3E635',      // Living green accent
  amber: '#FBBF24',     // Warm amber accent
  rust: '#C2410C',      // Warm rust for warnings
} as const;

/** Timing constants (ms) */
export const TIMING = {
  instant: 100,
  quick: 200,
  standard: 300,
  emphasized: 500,
} as const;
