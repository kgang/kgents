/**
 * Core Color System
 *
 * The foundational color palette for kgents.
 * All visual decisions derive from semantic meaning.
 *
 * @see docs/creative/visual-system.md
 */

/**
 * Gray Scale
 *
 * Grays form the canvas. Using Tailwind Slate scale for consistency.
 */
export const GRAYS = {
  50: '#F8FAFC', // Near-white backgrounds
  100: '#F1F5F9', // Subtle backgrounds
  200: '#E2E8F0', // Borders, dividers
  300: '#CBD5E1', // Disabled text
  400: '#94A3B8', // Secondary text
  500: '#64748B', // Muted text
  600: '#475569', // Body text (dark mode)
  700: '#334155', // Emphasis
  800: '#1E293B', // Card backgrounds (dark mode)
  900: '#0F172A', // App background (dark mode)
  950: '#020617', // Deep backgrounds
} as const;

export type GrayShade = keyof typeof GRAYS;

/**
 * State Colors
 *
 * System states use consistent colors for immediate recognition.
 */
export const STATE_COLORS = {
  success: '#22C55E', // Green - completed actions, healthy states
  warning: '#F59E0B', // Amber - attention needed, degraded mode
  error: '#EF4444', // Red - failures, critical issues
  info: '#06B6D4', // Cyan - informational, neutral updates
  pending: '#64748B', // Slate - waiting, loading, in-progress
} as const;

export type StateType = keyof typeof STATE_COLORS;

/**
 * Semantic Color Map
 *
 * Maps semantic meanings to their hues.
 */
export const SEMANTIC_COLORS = {
  knowledge: '#06B6D4', // Cyan - brain, memory, understanding
  growth: '#22C55E', // Green - gestalt, health, progress
  cultivation: '#84CC16', // Lime - gardener, nurturing, emergence
  creation: '#F59E0B', // Amber - atelier, creativity, warmth
  collaboration: '#8B5CF6', // Violet - coalition, synthesis, harmony
  drama: '#EC4899', // Pink - park, narrative, performance
  urgency: '#EF4444', // Red - domain, crisis, alert
  neutral: '#64748B', // Slate - structure, chrome, system
} as const;

export type SemanticMeaning = keyof typeof SEMANTIC_COLORS;

/**
 * Dark Mode Surface Colors
 *
 * kgents is dark mode first. These define the layered surfaces.
 */
export const DARK_SURFACES = {
  canvas: GRAYS[900], // #0F172A - App background
  card: GRAYS[800], // #1E293B - Card backgrounds
  elevated: GRAYS[700], // #334155 - Elevated surfaces
  borderBase: GRAYS[700], // Base border (use with opacity)
} as const;

/**
 * Dark Mode Text Colors
 */
export const DARK_TEXT = {
  primary: '#FFFFFF', // Full white for headlines
  body: '#F9FAFB', // gray-50 for body text
  secondary: GRAYS[400], // #94A3B8
  muted: GRAYS[500], // #64748B
  disabled: GRAYS[600], // #475569
} as const;

/**
 * Light Mode Surface Colors
 * (Secondary - dark mode is primary)
 */
export const LIGHT_SURFACES = {
  canvas: GRAYS[50], // #F8FAFC - App background
  card: '#FFFFFF', // White - Card backgrounds
  elevated: GRAYS[100], // #F1F5F9 - Elevated surfaces
  borderBase: GRAYS[200], // #E2E8F0 - Borders
} as const;

/**
 * Light Mode Text Colors
 */
export const LIGHT_TEXT = {
  primary: GRAYS[900], // #0F172A
  body: GRAYS[800], // #1E293B
  secondary: GRAYS[600], // #475569
  muted: GRAYS[500], // #64748B
  disabled: GRAYS[400], // #94A3B8
} as const;

/**
 * Archetype Colors (Agent Town)
 *
 * Used for citizen archetypes in Agent Town.
 */
export const ARCHETYPE_COLORS = {
  builder: '#3B82F6', // Blue
  trader: '#F59E0B', // Amber
  healer: '#22C55E', // Green
  scholar: '#8B5CF6', // Purple
  watcher: '#6B7280', // Gray
} as const;

export type ArchetypeName = keyof typeof ARCHETYPE_COLORS;

/**
 * Phase Colors (Time of Day)
 *
 * Used for Agent Town phase transitions.
 */
export const PHASE_COLORS = {
  morning: '#FBBF24', // Amber-400
  afternoon: '#FB923C', // Orange-400
  evening: '#A855F7', // Purple-500
  night: '#1E3A5F', // Custom blue
} as const;

export type PhaseName = keyof typeof PHASE_COLORS;

/**
 * Garden Season Colors
 *
 * Used for Gardener-Logos season visualization.
 * Each season has a color representing its character.
 */
export const SEASON_COLORS = {
  dormant: '#6B7280', // Gray - rest, potential
  sprouting: '#22C55E', // Green - growth, emergence
  blooming: '#F472B6', // Pink - expression, flourishing
  harvest: '#F59E0B', // Amber - collection, completion
  composting: '#A16207', // Brown - decay, transformation
} as const;

export type SeasonName = keyof typeof SEASON_COLORS;

/**
 * Get season color with fallback
 */
export function getSeasonColor(season: string): string {
  const key = season.toLowerCase() as SeasonName;
  return SEASON_COLORS[key] ?? SEASON_COLORS.dormant;
}

/**
 * Builder Personality Colors (Workshop)
 *
 * Used for workshop builder agent personalities.
 */
export const BUILDER_PERSONALITY_COLORS = {
  scout: '#22C55E', // Green - exploration, discovery
  sage: '#8B5CF6', // Purple - wisdom, architecture
  spark: '#F59E0B', // Amber - creativity, ideas
  steady: '#3B82F6', // Blue - reliability, implementation
  sync: '#EC4899', // Pink - coordination, integration
} as const;

export type BuilderPersonality = keyof typeof BUILDER_PERSONALITY_COLORS;

/**
 * Get builder personality color with fallback
 */
export function getBuilderColor(personality: string): string {
  const key = personality.toLowerCase() as BuilderPersonality;
  return BUILDER_PERSONALITY_COLORS[key] ?? GRAYS[500];
}

/**
 * Health Gradient Colors
 *
 * Used for health-based visualizations (0-1 scale).
 * Order: healthy → degraded → warning → critical
 */
export const HEALTH_COLORS = {
  healthy: '#22C55E', // Green (>= 0.8)
  degraded: '#FACC15', // Yellow (>= 0.6)
  warning: '#F97316', // Orange (>= 0.4)
  critical: '#EF4444', // Red (< 0.4)
} as const;

export type HealthLevel = keyof typeof HEALTH_COLORS;

/**
 * Get health color based on 0-1 health score
 */
export function getHealthColor(health: number): string {
  if (health >= 0.8) return HEALTH_COLORS.healthy;
  if (health >= 0.6) return HEALTH_COLORS.degraded;
  if (health >= 0.4) return HEALTH_COLORS.warning;
  return HEALTH_COLORS.critical;
}

/**
 * Connection Status Colors
 *
 * Used for live connection indicators.
 */
export const CONNECTION_STATUS_COLORS = {
  live: '#22C55E', // Green - connected
  connecting: '#F59E0B', // Amber - establishing
  reconnecting: '#F59E0B', // Amber - reconnecting
  error: '#EF4444', // Red - failed
  offline: '#6B7280', // Gray - disconnected
} as const;

export type ConnectionStatus = keyof typeof CONNECTION_STATUS_COLORS;

/**
 * Get connection status color
 */
export function getConnectionStatusColor(status: string): string {
  const key = status.toLowerCase() as ConnectionStatus;
  return CONNECTION_STATUS_COLORS[key] ?? CONNECTION_STATUS_COLORS.offline;
}

/**
 * Get state color with fallback
 */
export function getStateColor(state: string): string {
  const key = state.toLowerCase() as StateType;
  return STATE_COLORS[key] ?? STATE_COLORS.pending;
}

/**
 * Get semantic color with fallback
 */
export function getSemanticColor(meaning: string): string {
  const key = meaning.toLowerCase() as SemanticMeaning;
  return SEMANTIC_COLORS[key] ?? SEMANTIC_COLORS.neutral;
}

/**
 * Get archetype color with fallback
 */
export function getArchetypeColor(archetype: string): string {
  const key = archetype.toLowerCase() as ArchetypeName;
  return ARCHETYPE_COLORS[key] ?? ARCHETYPE_COLORS.watcher;
}

/**
 * Tailwind-friendly color extensions for theme
 */
export const COLOR_TAILWIND_EXTENSIONS = {
  // State colors
  'state-success': STATE_COLORS.success,
  'state-warning': STATE_COLORS.warning,
  'state-error': STATE_COLORS.error,
  'state-info': STATE_COLORS.info,
  'state-pending': STATE_COLORS.pending,

  // Dark surfaces
  'surface-canvas': DARK_SURFACES.canvas,
  'surface-card': DARK_SURFACES.card,
  'surface-elevated': DARK_SURFACES.elevated,

  // Archetypes
  'archetype-builder': ARCHETYPE_COLORS.builder,
  'archetype-trader': ARCHETYPE_COLORS.trader,
  'archetype-healer': ARCHETYPE_COLORS.healer,
  'archetype-scholar': ARCHETYPE_COLORS.scholar,
  'archetype-watcher': ARCHETYPE_COLORS.watcher,

  // Phases
  'phase-morning': PHASE_COLORS.morning,
  'phase-afternoon': PHASE_COLORS.afternoon,
  'phase-evening': PHASE_COLORS.evening,
  'phase-night': PHASE_COLORS.night,

  // Builder personalities
  'builder-scout': BUILDER_PERSONALITY_COLORS.scout,
  'builder-sage': BUILDER_PERSONALITY_COLORS.sage,
  'builder-spark': BUILDER_PERSONALITY_COLORS.spark,
  'builder-steady': BUILDER_PERSONALITY_COLORS.steady,
  'builder-sync': BUILDER_PERSONALITY_COLORS.sync,
} as const;
