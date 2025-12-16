/**
 * Forest Theme Constants
 *
 * The organic, plant-like visual language for Gestalt architecture visualization.
 * Transforms the cold "donut in space" into a living, breathing forest ecosystem.
 *
 * Philosophy:
 *   "The codebase is a forest, not a machine.
 *    Each module is a plant. Dependencies are roots reaching for water.
 *    Health is growth. Violations are thorns."
 *
 * @see docs/creative/emergence-principles.md
 * @see plans/_continuations/gestalt-sprint3.md
 */

// =============================================================================
// Color Palettes
// =============================================================================

/**
 * Forest Ground Colors
 *
 * The foundation layer - dark, rich, organic.
 */
export const FOREST_GROUND = {
  /** Deep forest floor */
  floor: '#0D1117',
  /** Moss-covered areas */
  moss: '#1C2526',
  /** Rich soil */
  soil: '#2D3B36',
  /** Decaying leaves */
  loam: '#3D4A45',
  /** Fog/mist */
  mist: '#4A5568',
} as const;

/**
 * Plant Health Colors
 *
 * From thriving to struggling plants.
 */
export const PLANT_HEALTH = {
  // Thriving (health >= 0.9)
  thriving: {
    core: '#22C55E',      // Rich green bulb
    ring: '#166534',      // Deep forest ring
    glow: '#4ADE80',      // Bright glow
    label: 'Thriving',
  },
  // Healthy (health >= 0.7)
  healthy: {
    core: '#84CC16',      // Lime green
    ring: '#365314',      // Dark lime
    glow: '#A3E635',      // Bright lime
    label: 'Healthy',
  },
  // Stressed (health >= 0.5)
  stressed: {
    core: '#FACC15',      // Golden yellow
    ring: '#854D0E',      // Bark brown
    glow: '#FDE047',      // Bright yellow
    label: 'Stressed',
  },
  // Wilting (health >= 0.3)
  wilting: {
    core: '#F97316',      // Orange
    ring: '#9A3412',      // Rust
    glow: '#FB923C',      // Bright orange
    label: 'Wilting',
  },
  // Dying (health < 0.3)
  dying: {
    core: '#EF4444',      // Red
    ring: '#7F1D1D',      // Dark red
    glow: '#FCA5A5',      // Light red
    label: 'Critical',
  },
} as const;

export type PlantHealthLevel = keyof typeof PLANT_HEALTH;

/**
 * Get plant health configuration from score
 */
export function getPlantHealth(score: number): typeof PLANT_HEALTH[PlantHealthLevel] {
  if (score >= 0.9) return PLANT_HEALTH.thriving;
  if (score >= 0.7) return PLANT_HEALTH.healthy;
  if (score >= 0.5) return PLANT_HEALTH.stressed;
  if (score >= 0.3) return PLANT_HEALTH.wilting;
  return PLANT_HEALTH.dying;
}

/**
 * Vine/Connection Colors
 *
 * Dependencies as roots and vines.
 */
export const VINE_COLORS = {
  // Normal dependencies
  normal: {
    base: '#4A5568',        // Muted gray-green
    highlight: '#68D391',   // Bright green when active
    glow: '#48BB78',        // Medium green glow
    particle: '#9AE6B4',    // Light green flow
  },
  // Violations (thorny vines)
  violation: {
    base: '#C53030',        // Dark red
    highlight: '#FC8181',   // Light red when active
    glow: '#F56565',        // Red glow
    particle: '#FEB2B2',    // Light red flow
    thorn: '#991B1B',       // Deep thorn color
  },
  // Selected/Active
  active: {
    base: '#68D391',        // Bright green
    glow: '#4ADE80',        // Bright glow
    particle: '#FFFFFF',    // White particles
  },
} as const;

/**
 * Layer Ring Colors
 *
 * Architectural layers as growth zones in the forest.
 */
export const LAYER_RINGS = {
  // Protocol layer (inner ring)
  protocols: {
    color: '#166534',       // Deep forest green
    opacity: 0.12,
    label: 'Protocols',
  },
  // Agent layer
  agents: {
    color: '#1D4ED8',       // Deep blue
    opacity: 0.10,
    label: 'Agents',
  },
  // Infrastructure layer
  infra: {
    color: '#7C3AED',       // Purple
    opacity: 0.10,
    label: 'Infrastructure',
  },
  // Web layer (outer ring)
  web: {
    color: '#DC2626',       // Red
    opacity: 0.08,
    label: 'Web',
  },
} as const;

// =============================================================================
// Sizing & Layout
// =============================================================================

/**
 * Node Size Configuration
 *
 * Plant sizes based on module metrics.
 */
export const PLANT_SIZING = {
  /** Minimum plant size */
  minSize: 0.12,
  /** Maximum plant size */
  maxSize: 0.45,
  /** Base size by density */
  baseSizes: {
    compact: 0.15,
    comfortable: 0.20,
    spacious: 0.25,
  },
  /** LOC scaling factor (logarithmic) */
  locScaleFactor: 0.12,
  /** Health impact on size (healthier = fuller) */
  healthScaleFactor: 0.3,
} as const;

/**
 * Vine Width Configuration
 */
export const VINE_SIZING = {
  /** Normal edge width */
  normal: 1.5,
  /** Active/highlighted edge width */
  active: 2.5,
  /** Dimmed edge width */
  dimmed: 0.8,
  /** Violation edge width */
  violation: 2.0,
  /** Active violation width */
  violationActive: 3.0,
  /** Curve intensity (0 = straight, 1 = very curved) */
  curveIntensity: 0.15,
} as const;

/**
 * Growth Ring Configuration
 */
export const GROWTH_RINGS = {
  /** Maximum rings per plant */
  maxRings: 4,
  /** Ring spacing factor */
  spacingFactor: 0.15,
  /** Ring thickness factor */
  thicknessFactor: 0.1,
  /** Opacity falloff per ring */
  opacityFalloff: 0.08,
  /** Base opacity for innermost ring */
  baseOpacity: 0.4,
} as const;

// =============================================================================
// Animation
// =============================================================================

/**
 * Breathing Animation
 *
 * Subtle life pulse for all plants.
 */
export const BREATHE_ANIMATION = {
  /** Amplitude of breathing scale */
  amplitude: 0.03,
  /** Frequency multiplier */
  frequency: 1.5,
  /** Phase randomization (each plant gets random start) */
  phaseRange: Math.PI * 2,
} as const;

/**
 * Flow Animation
 *
 * Particles flowing along vines.
 */
export const FLOW_ANIMATION = {
  /** Base flow speed */
  speed: 0.6,
  /** Number of particles per active edge */
  particleCount: 4,
  /** Particle radius */
  particleSize: 0.03,
  /** Glow pulse frequency */
  glowFrequency: 3.0,
  /** Glow intensity variation */
  glowVariation: 0.1,
} as const;

/**
 * Violation Pulse Animation
 */
export const VIOLATION_ANIMATION = {
  /** Pulse frequency */
  pulseFrequency: 2.0,
  /** Base thorn opacity */
  thornOpacity: 0.7,
  /** Thorn size */
  thornSize: 0.04,
} as const;

// =============================================================================
// Labels & Text
// =============================================================================

/**
 * Label Configuration by Density
 */
export const LABEL_CONFIG = {
  compact: {
    fontSize: 0.12,
    offset: 0.2,
    maxLabels: 15,
    outlineWidth: 0.012,
  },
  comfortable: {
    fontSize: 0.16,
    offset: 0.25,
    maxLabels: 30,
    outlineWidth: 0.015,
  },
  spacious: {
    fontSize: 0.20,
    offset: 0.3,
    maxLabels: 50,
    outlineWidth: 0.018,
  },
} as const;

/**
 * Label Colors
 */
export const LABEL_COLORS = {
  text: '#FFFFFF',
  outline: '#1A3A1A',      // Dark forest green
  outlineOpacity: 0.9,
} as const;

// =============================================================================
// Scene
// =============================================================================

/**
 * Forest Scene Configuration
 */
export const FOREST_SCENE = {
  /** Background color */
  background: FOREST_GROUND.floor,
  /** Fog color */
  fogColor: FOREST_GROUND.mist,
  /** Fog near distance */
  fogNear: 30,
  /** Fog far distance */
  fogFar: 80,
  /** Ambient light color */
  ambientLight: '#4A5568',
  /** Ambient light intensity */
  ambientIntensity: 0.4,
  /** Directional light color (sun through canopy) */
  sunColor: '#FDE68A',
  /** Sun intensity */
  sunIntensity: 0.6,
} as const;

// =============================================================================
// Exports
// =============================================================================

export const FOREST_THEME = {
  ground: FOREST_GROUND,
  health: PLANT_HEALTH,
  vines: VINE_COLORS,
  layers: LAYER_RINGS,
  sizing: {
    plant: PLANT_SIZING,
    vine: VINE_SIZING,
    rings: GROWTH_RINGS,
  },
  animation: {
    breathe: BREATHE_ANIMATION,
    flow: FLOW_ANIMATION,
    violation: VIOLATION_ANIMATION,
  },
  labels: {
    config: LABEL_CONFIG,
    colors: LABEL_COLORS,
  },
  scene: FOREST_SCENE,
} as const;
