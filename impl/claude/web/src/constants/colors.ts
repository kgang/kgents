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
 * Phase Glow Effects
 *
 * Box-shadow glows for polynomial agent states across Town and Park.
 * Used by StateIndicator and phase visualization components.
 *
 * @see plans/park-town-design-overhaul.md - Part III: Design System Additions
 */
export const PHASE_GLOW = {
  idle: '0 0 12px rgba(100, 116, 139, 0.5)', // slate
  active: '0 0 12px rgba(34, 197, 94, 0.5)', // green
  warning: '0 0 12px rgba(245, 158, 11, 0.5)', // amber
  critical: '0 0 12px rgba(239, 68, 68, 0.5)', // red
  success: '0 0 12px rgba(34, 197, 94, 0.5)', // green
  neutral: '0 0 12px rgba(100, 116, 139, 0.3)', // slate (dimmer)
} as const;

export type PhaseGlowType = keyof typeof PHASE_GLOW;

/**
 * Get phase glow for a given state category
 */
export function getPhaseGlow(category: string): string {
  const key = category.toLowerCase() as PhaseGlowType;
  return PHASE_GLOW[key] ?? PHASE_GLOW.neutral;
}

/**
 * Teaching Gradient Backgrounds
 *
 * Gradient backgrounds for teaching callouts, categorized by type.
 * Used with TeachingCallout component across Park and Town.
 *
 * @see plans/park-town-design-overhaul.md - Part III: Design System Additions
 */
export const TEACHING_GRADIENT = {
  /** Blue-purple for categorical explanations (polynomial, operad, sheaf) */
  categorical: 'from-blue-500/20 to-purple-500/20',
  /** Amber-pink for operational explanations (actions, transitions) */
  operational: 'from-amber-500/20 to-pink-500/20',
  /** Green-blue for conceptual explanations (AGENTESE, N-gent) */
  conceptual: 'from-green-500/20 to-blue-500/20',
} as const;

export type TeachingCategory = keyof typeof TEACHING_GRADIENT;

/**
 * Get teaching gradient for a given category
 */
export function getTeachingGradient(category: string): string {
  const key = category.toLowerCase() as TeachingCategory;
  return TEACHING_GRADIENT[key] ?? TEACHING_GRADIENT.conceptual;
}

/**
 * Edge Animation Configuration
 *
 * Consistent animation timing for state transitions and operations.
 *
 * @see plans/park-town-design-overhaul.md - Part III: Design System Additions
 */
export const EDGE_ANIMATION = {
  duration: '300ms',
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)', // Tailwind default ease-in-out
  /** Full CSS transition string */
  transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

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

// =============================================================================
// Living Earth Palette (Crown Jewels Genesis)
// =============================================================================

/**
 * Living Earth Palette
 *
 * Ground-up color system from Crown Jewels Genesis Moodboard.
 * Three families: Warm Earth (primary), Living Green (secondary), Ghibli Glow (accent).
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see docs/creative/crown-jewels-genesis-moodboard.md
 */
export const LIVING_EARTH = {
  // Primary: Warm Earth (soil to sand)
  soil: '#2D1B14', // Deepest background
  bark: '#4A3728', // Card surfaces
  wood: '#6B4E3D', // Elevated surfaces
  clay: '#8B6F5C', // Borders, muted elements
  sand: '#AB9080', // Secondary text

  // Secondary: Living Green (moss to sprout)
  moss: '#1A2E1A', // Deep forest
  fern: '#2E4A2E', // Forest mid-tone
  sage: '#4A6B4A', // Nature accent
  mint: '#6B8B6B', // Available/ready state
  sprout: '#8BAB8B', // Fresh growth

  // Accent: Ghibli Glow (lantern to bronze)
  lantern: '#F5E6D3', // Warm white, highlights
  honey: '#E8C4A0', // Soft glow
  amber: '#D4A574', // Primary accent (collaboration)
  copper: '#C08552', // Warm mid-accent
  bronze: '#8B5A2B', // Deep accent
} as const;

export type LivingEarthColor = keyof typeof LIVING_EARTH;

/**
 * Get Living Earth color with fallback
 */
export function getLivingEarthColor(name: string): string {
  const key = name.toLowerCase() as LivingEarthColor;
  return LIVING_EARTH[key] ?? LIVING_EARTH.bark;
}

/**
 * Crown Jewel Identity Colors
 *
 * Each jewel has a primary identity color derived from Living Earth.
 */
export const JEWEL_IDENTITY_COLORS = {
  town: LIVING_EARTH.amber, // Collaboration, warmth
  atelier: LIVING_EARTH.honey, // Creation, artisan craft
  park: LIVING_EARTH.copper, // Drama, performance
  domain: LIVING_EARTH.bronze, // Integration, grounding
  brain: SEMANTIC_COLORS.knowledge, // Cyan - knowledge
  garden: LIVING_EARTH.sage, // Growth, cultivation
} as const;

export type JewelName = keyof typeof JEWEL_IDENTITY_COLORS;

/**
 * Get jewel identity color with fallback
 */
export function getJewelColor(jewel: string): string {
  const key = jewel.toLowerCase() as JewelName;
  return JEWEL_IDENTITY_COLORS[key] ?? LIVING_EARTH.bark;
}
