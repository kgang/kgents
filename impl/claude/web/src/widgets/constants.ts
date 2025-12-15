/**
 * Shared constants for widget components.
 *
 * These constants are extracted from WidgetRenderer to enable reuse
 * across widget components in different directories.
 */

import type { CitizenPhase } from '@/reactive/types';

/**
 * Phase-to-glyph mapping for citizen state visualization.
 */
export const PHASE_GLYPHS: Record<CitizenPhase, string> = {
  IDLE: '○',
  SOCIALIZING: '◉',
  WORKING: '●',
  REFLECTING: '◐',
  RESTING: '◯',
};

/**
 * N-Phase to Tailwind color class mapping.
 */
export const NPHASE_COLORS: Record<string, string> = {
  SENSE: 'text-blue-500',
  ACT: 'text-green-500',
  REFLECT: 'text-purple-500',
};

/**
 * Unicode characters for sparkline rendering.
 * Index maps to value (0.0 = space, 1.0 = full block).
 */
export const SPARK_CHARS = ' ▁▂▃▄▅▆▇█';
