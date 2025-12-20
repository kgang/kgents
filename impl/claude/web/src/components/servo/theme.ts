/**
 * Living Earth Theme for Servo Components
 *
 * Maps SceneGraph semantic colors to CSS values and Tailwind classes.
 * This bridges the Python-side PALETTE to the React rendering layer.
 *
 * @see protocols/agentese/projection/warp_converters.py - PALETTE definition
 * @see constants/livingEarth.ts - Full palette definition
 */

import { EARTH, GREEN, GLOW } from '@/constants';

// =============================================================================
// Servo Palette (Maps Python PALETTE semantic names to CSS values)
// =============================================================================

/**
 * Maps SceneGraph semantic color names to hex values.
 * Must match protocols/agentese/projection/warp_converters.py PALETTE_HEX.
 */
export const SERVO_PALETTE = {
  // Earth tones
  copper: GLOW.copper,       // #C08552
  sage: GREEN.sage,          // #4A6B4A
  soil: EARTH.soil,          // #2D1B14
  paper: GLOW.lantern,       // #F5E6D3

  // Living accents
  living_green: GREEN.mint,  // #6B8B6B
  amber_glow: GLOW.amber,    // #D4A574
  twilight: '#5d4e6d',       // Void, mystery

  // Status colors (match warp_converters.py)
  success: '#4ade80',
  warning: '#fbbf24',
  error: '#f87171',
} as const;

export type ServoPaletteColor = keyof typeof SERVO_PALETTE;

/**
 * Get hex value for a palette color name.
 * Falls through to return the input if not found (for custom colors).
 */
export function getServoColor(color: string): string {
  return SERVO_PALETTE[color as ServoPaletteColor] ?? color;
}

// =============================================================================
// Tailwind Class Mappings
// =============================================================================

/**
 * Maps SceneGraph background colors to Tailwind classes.
 */
export const SERVO_BG_CLASSES: Record<string, string> = {
  copper: 'bg-amber-700/80',
  sage: 'bg-emerald-800/70',
  soil: 'bg-stone-900/90',
  paper: 'bg-amber-50/90',
  living_green: 'bg-emerald-600/70',
  amber_glow: 'bg-amber-500/70',
  twilight: 'bg-purple-900/70',
  success: 'bg-green-500/70',
  warning: 'bg-amber-500/70',
  error: 'bg-red-500/70',
};

/**
 * Maps SceneGraph border colors to Tailwind classes.
 */
export const SERVO_BORDER_CLASSES: Record<string, string> = {
  copper: 'border-amber-600/50',
  sage: 'border-emerald-700/50',
  soil: 'border-stone-700/50',
  paper: 'border-amber-200/50',
  living_green: 'border-emerald-500/50',
  amber_glow: 'border-amber-400/50',
  twilight: 'border-purple-700/50',
};

// =============================================================================
// SceneNodeKind → Style Mappings
// =============================================================================

/**
 * Default background color for each SceneNodeKind.
 */
export const KIND_BACKGROUNDS: Record<string, string> = {
  PANEL: 'paper',
  TRACE: 'sage',
  INTENT: 'copper',
  OFFERING: 'amber_glow',
  COVENANT: 'twilight',
  WALK: 'living_green',
  RITUAL: 'copper',
  TEXT: 'paper',
  GROUP: 'transparent',
};

/**
 * Get background class for a node kind, with style override.
 */
export function getNodeBackground(kind: string, styleOverride?: string): string {
  const color = styleOverride ?? KIND_BACKGROUNDS[kind] ?? 'paper';
  return SERVO_BG_CLASSES[color] ?? `bg-[${getServoColor(color)}]`;
}

// =============================================================================
// Living Earth Theme Provider Value
// =============================================================================

/**
 * Theme value for React context (if needed for nested theming).
 */
export interface LivingEarthThemeValue {
  palette: typeof SERVO_PALETTE;
  mode: 'light' | 'dark';
}

export const LivingEarthTheme: LivingEarthThemeValue = {
  palette: SERVO_PALETTE,
  mode: 'dark', // Default to dark mode
};
