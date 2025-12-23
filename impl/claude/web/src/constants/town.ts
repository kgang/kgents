/**
 * Town Theme Constants
 *
 * The Town Crown Jewel visual identity from Crown Jewels Genesis Moodboard.
 * Implements "Alive Workshop" creative vision with "Everything Breathes" animation.
 *
 * @see plans/town-visualizer-renaissance.md - Phase 4: Projection Surfaces
 * @see docs/creative/crown-jewels-genesis-moodboard.md
 */

// =============================================================================
// Color Palette: "Living Earth"
// =============================================================================

/**
 * Town Identity Colors
 *
 * Living Earth palette from moodboard:
 * - Warm Earth: Soil, bark, amber
 * - Living Green: Sage, mint, moss
 * - Ghibli Glow: Soft highlights, breathing luminosity
 */
export const TOWN_COLORS = {
  // Primary identity color
  primary: '#D4A574', // Amber - collaboration glow
  secondary: '#4A6B4A', // Sage - nature, growth

  // Surface colors
  background: '#2D1B14', // Soil - deep, grounding
  surface: '#4A3728', // Bark - warm mid-tone
  elevated: '#5C4A3A', // Lighter bark

  // Accent colors
  accent: '#8B6B4D', // Warm bronze
  highlight: '#FFE4B5', // Ghibli glow (moccasin)

  // Text colors
  textPrimary: '#F5F0E8', // Warm white
  textSecondary: '#C4B8A8', // Muted cream
  textMuted: '#8C7B6B', // Bark tone
} as const;

/**
 * Citizen Phase Colors
 *
 * Maps citizen polynomial phases to visual colors.
 */
export const CITIZEN_PHASE_COLORS = {
  IDLE: '#6B8B6B', // Mint - ready, available
  SOCIALIZING: '#D4A574', // Amber - collaboration
  WORKING: '#3B82F6', // Blue - focused activity
  REFLECTING: '#8B5CF6', // Purple - contemplation
  RESTING: '#6B4E3D', // Dormant bark - Right to Rest
} as const;

export type CitizenPhaseName = keyof typeof CITIZEN_PHASE_COLORS;

/**
 * Town Phase Colors (Circadian)
 *
 * Maps town polynomial phases to visual colors.
 */
export const TOWN_PHASE_COLORS = {
  MORNING: '#FBBF24', // Amber - dawn glow
  AFTERNOON: '#FB923C', // Orange - peak activity
  EVENING: '#A855F7', // Purple - twilight
  NIGHT: '#1E3A5F', // Deep blue - rest
} as const;

export type TownPhaseName = keyof typeof TOWN_PHASE_COLORS;

/**
 * Region Colors
 *
 * Each region has a subtle identity color.
 */
export const REGION_COLORS = {
  inn: '#D4A574', // Amber - warmth, gathering
  workshop: '#3B82F6', // Blue - productivity
  plaza: '#22C55E', // Green - public, open
  market: '#F59E0B', // Gold - trade, exchange
  library: '#8B5CF6', // Purple - knowledge
  temple: '#6366F1', // Indigo - reflection
  garden: '#84CC16', // Lime - growth
} as const;

export type RegionName = keyof typeof REGION_COLORS;

// =============================================================================
// Animation: "Everything Breathes"
// =============================================================================

/**
 * Breathing Animation Constants
 *
 * From moodboard: "Everything Breathes"
 * - Period: 3-4 seconds per breath cycle
 * - Amplitude: 2-3% scale variation
 * - Style: Organic, Ghibli-inspired subtle movement
 */
export const BREATHING_ANIMATION = {
  /** Duration of one complete breath cycle in ms (synced with Tailwind breathe: 8.1s) */
  period: 8100,

  /** Scale amplitude — subtle (synced with Tailwind breathe: 1.5% variation) */
  amplitude: 0.015,

  /** Timing function — linear since easing is in the curve shape */
  easing: 'linear',

  /** Calming breath phases (asymmetric: slow exhale) */
  phases: {
    rest: 1.0, // 0-15%: stillness
    inhale: 1.015, // 15-40%: gentle rise
    hold: 1.015, // 40-50%: moment of fullness
    exhale: 1.0, // 50-95%: slow release
  },
} as const;

/**
 * Growing Animation Constants
 *
 * For new elements entering the scene.
 */
export const GROWING_ANIMATION = {
  /** Duration for growing transition */
  duration: 400,

  /** Spring overshoot for organic feel */
  easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',

  /** Stages of growth */
  stages: {
    seed: { scale: 0, opacity: 0 },
    sprout: { scale: 0.5, opacity: 0.5 },
    bloom: { scale: 1, opacity: 1 },
  },
} as const;

/**
 * Flowing Animation Constants
 *
 * For edges, relationships, data flow visualization.
 */
export const FLOWING_ANIMATION = {
  /** Duration for one flow cycle */
  duration: 2000,

  /** Speed of particles along edges (units per second) */
  particleSpeed: 30,

  /** Glow pulse for relationship lines */
  pulseIntensity: 0.5,
} as const;

/**
 * Unfurling Animation Constants
 *
 * For panels, drawers, expanding content.
 */
export const UNFURLING_ANIMATION = {
  /** Duration for unfurl */
  duration: 300,

  /** Tailwind-compatible easing */
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

// =============================================================================
// Density-Aware Constants
// =============================================================================

/**
 * Node Sizing by Density
 *
 * From elastic-ui-patterns.md: Three-mode density pattern.
 */
export const NODE_RADIUS = {
  compact: 12,
  comfortable: 16,
  spacious: 20,
} as const;

export const LABEL_SIZE = {
  compact: 10,
  comfortable: 12,
  spacious: 14,
} as const;

export const MAX_CITIZENS_VISIBLE = {
  compact: 20,
  comfortable: 40,
  spacious: 100,
} as const;

export const EDGE_THICKNESS = {
  compact: 1,
  comfortable: 2,
  spacious: 3,
} as const;

// =============================================================================
// 3D Theme (for TownCanvas3D)
// =============================================================================

/**
 * 3D Town Theme
 *
 * For use with TopologyNode3D primitives.
 * Follows 3d-projection-patterns.md tier system.
 */
/** Tier colors for TopologyNode3D in 3D scene */
const TOWN_3D_TIERS = {
  vivid: { color: '#D4A574', emissive: '#D4A574', emissiveIntensity: 0.3 },
  familiar: { color: '#6B8B6B', emissive: '#6B8B6B', emissiveIntensity: 0.2 },
  hot: { color: '#3B82F6', emissive: '#3B82F6', emissiveIntensity: 0.4 },
  crystal: { color: '#22C55E', emissive: '#22C55E', emissiveIntensity: 0.25 },
  dormant: { color: '#6B4E3D', emissive: '#6B4E3D', emissiveIntensity: 0.1 },
} as const;

/** Archetype to tier mapping */
const ARCHETYPE_TO_TIER: Record<string, keyof typeof TOWN_3D_TIERS> = {
  builder: 'vivid',
  trader: 'familiar',
  healer: 'crystal',
  scholar: 'hot',
  watcher: 'dormant',
} as const;

export const TOWN_THEME_3D = {
  name: 'town',

  /** Tier colors (for TopologyNode3D) */
  tiers: TOWN_3D_TIERS,

  /** Archetype to tier mapping */
  archetypeTiers: ARCHETYPE_TO_TIER,

  /** Scene lighting */
  lighting: {
    ambientIntensity: 0.4,
    directionalIntensity: 0.8,
    directionalPosition: [10, 20, 10] as [number, number, number],
  },

  /** Background color */
  background: 0x2d1b14, // Soil (as hex number for Three.js)
} as const;

// =============================================================================
// Archetype Configuration
// =============================================================================

/**
 * Archetype Visual Config
 *
 * Complete archetype metadata for consistent visualization.
 */
export const ARCHETYPE_CONFIG = {
  builder: {
    color: '#3B82F6',
    emoji: '🔨',
    label: 'Builder',
    tier: 'vivid',
  },
  trader: {
    color: '#F59E0B',
    emoji: '🪙',
    label: 'Trader',
    tier: 'familiar',
  },
  healer: {
    color: '#22C55E',
    emoji: '💚',
    label: 'Healer',
    tier: 'crystal',
  },
  scholar: {
    color: '#8B5CF6',
    emoji: '📚',
    label: 'Scholar',
    tier: 'hot',
  },
  watcher: {
    color: '#6B7280',
    emoji: '👁️',
    label: 'Watcher',
    tier: 'dormant',
  },
} as const;

export type ArchetypeKey = keyof typeof ARCHETYPE_CONFIG;

// =============================================================================
// Full Theme Export
// =============================================================================

/**
 * TOWN_THEME
 *
 * Complete town visualization theme object.
 * Implements "Alive Workshop" creative vision.
 */
export const TOWN_THEME = {
  name: 'town',

  // Color palette
  colors: TOWN_COLORS,
  phases: {
    citizen: CITIZEN_PHASE_COLORS,
    town: TOWN_PHASE_COLORS,
  },
  regions: REGION_COLORS,
  archetypes: ARCHETYPE_CONFIG,

  // Animation (Everything Breathes)
  animation: {
    breathing: BREATHING_ANIMATION,
    growing: GROWING_ANIMATION,
    flowing: FLOWING_ANIMATION,
    unfurling: UNFURLING_ANIMATION,
  },

  // Density-aware sizing
  density: {
    nodeRadius: NODE_RADIUS,
    labelSize: LABEL_SIZE,
    maxCitizens: MAX_CITIZENS_VISIBLE,
    edgeThickness: EDGE_THICKNESS,
  },

  // 3D configuration
  three: TOWN_THEME_3D,
} as const;

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get citizen phase color with fallback
 */
export function getCitizenPhaseColor(phase: string): string {
  const key = phase.toUpperCase() as CitizenPhaseName;
  return CITIZEN_PHASE_COLORS[key] ?? CITIZEN_PHASE_COLORS.IDLE;
}

/**
 * Get town phase color with fallback
 */
export function getTownPhaseColor(phase: string): string {
  const key = phase.toUpperCase() as TownPhaseName;
  return TOWN_PHASE_COLORS[key] ?? TOWN_PHASE_COLORS.MORNING;
}

/**
 * Get region color with fallback
 */
export function getRegionColor(region: string): string {
  const key = region.toLowerCase() as RegionName;
  return REGION_COLORS[key] ?? TOWN_COLORS.secondary;
}

/**
 * Get archetype configuration with fallback
 */
export function getArchetypeConfig(archetype: string) {
  const key = archetype.toLowerCase() as ArchetypeKey;
  return ARCHETYPE_CONFIG[key] ?? ARCHETYPE_CONFIG.watcher;
}

/**
 * Calculate breathing scale at a given time
 *
 * @param timeMs Current time in milliseconds
 * @returns Scale factor (0.97 - 1.03)
 */
export function getBreathingScale(timeMs: number): number {
  const { period, amplitude, phases } = BREATHING_ANIMATION;
  const cyclePosition = (timeMs % period) / period;

  // 4 phases: rest (0-0.25), inhale (0.25-0.5), hold (0.5-0.75), exhale (0.75-1.0)
  if (cyclePosition < 0.25) {
    return phases.rest;
  } else if (cyclePosition < 0.5) {
    // Inhale: interpolate from rest to inhale
    const t = (cyclePosition - 0.25) / 0.25;
    return phases.rest + t * amplitude;
  } else if (cyclePosition < 0.75) {
    // Hold: stay at inhale
    return phases.inhale;
  }
  // Exhale: interpolate from rest down to exhale
  const t = (cyclePosition - 0.75) / 0.25;
  return phases.rest - t * amplitude;
}
