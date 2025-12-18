/**
 * Animation Presets for 3D Projections
 *
 * Unified animation constants for consistent behavior across all 3D primitives.
 * These presets ensure that crystals and plants "breathe" with the same rhythm.
 *
 * Philosophy:
 *   "Animation is not decoration—it is life. But life has a rhythm."
 *
 * @see plans/3d-projection-consolidation.md
 */

// =============================================================================
// Breathing Animation (Node Life)
// =============================================================================

/**
 * Breathing animation for nodes.
 * Creates the "alive" feeling of organic 3D elements.
 */
export const BREATHING = {
  /** Base breathing speed (cycles per second) */
  speed: 1.5,
  /** Scale amplitude (1.0 = no change, 1.03 = 3% expansion at peak) */
  amplitude: 0.03,
  /** Glow pulse amplitude for inner cores */
  glowAmplitude: 0.1,
  /** Speed variation factor based on data (e.g., resolution affects crystal breathing) */
  variationFactor: 0.4,
} as const;

// =============================================================================
// Flow Particles (Edge Life)
// =============================================================================

/**
 * Flow particle animation for edges.
 * Creates the sense of data/memory flowing between nodes.
 */
export const FLOW_PARTICLES = {
  /** Particle movement speed (0-1 progress per second) */
  speed: 0.5,
  /** Number of particles per active edge */
  count: 4,
  /** Particle sphere radius */
  size: 0.025,
  /** Particle opacity */
  opacity: 0.85,
  /** Geometry segments (lower = better performance) */
  segments: 8,
} as const;

// =============================================================================
// Interaction Animation
// =============================================================================

/**
 * Hover interaction animation.
 */
export const HOVER = {
  /** Scale multiplier when hovered (1.12 = 12% larger) */
  scaleMultiplier: 1.12,
  /** Lerp speed for smooth transition (0-1, higher = faster) */
  lerpSpeed: 0.1,
} as const;

/**
 * Selection interaction animation.
 */
export const SELECTION = {
  /** Scale multiplier when selected (1.25 = 25% larger) */
  scaleMultiplier: 1.25,
  /** Selection ring opacity */
  ringOpacity: 0.7,
  /** Selection ring emissive intensity boost */
  emissiveBoost: 2.0,
} as const;

// =============================================================================
// Edge Animation
// =============================================================================

/**
 * Edge curve and glow animation.
 */
export const EDGE = {
  /** How curved edges are (0 = straight, 0.15 = moderate curve) */
  curveIntensity: 0.12,
  /** Glow pulse speed for active edges */
  glowPulseSpeed: 2.0,
  /** Number of segments for bezier curve (more = smoother, slower) */
  curveSegments: 16,
} as const;

// =============================================================================
// Violation Animation (Forest-specific, but could be shared)
// =============================================================================

/**
 * Violation/error state animation.
 */
export const VIOLATION = {
  /** Pulse frequency for warning state */
  pulseFrequency: 2.0,
  /** Thorn visibility pulse */
  thornPulse: 0.1,
} as const;

// =============================================================================
// Growth Rings (Forest-specific animation)
// =============================================================================

/**
 * Growth ring animation for forest theme.
 */
export const GROWTH_RINGS = {
  /** Opacity falloff per ring (outer rings more transparent) */
  opacityFalloff: 0.08,
  /** Base opacity for innermost ring */
  baseOpacity: 0.4,
  /** Minimum opacity for outermost ring */
  minOpacity: 0.1,
  /** Ring spacing multiplier */
  spacing: 0.15,
  /** Ring thickness as fraction of base size */
  thickness: 0.1,
} as const;

// =============================================================================
// Performance Tiers
// =============================================================================

/**
 * Animation settings by performance tier.
 * Allows graceful degradation on lower-end devices.
 */
export const PERFORMANCE_TIERS = {
  /** Full animations, all effects */
  cinematic: {
    breathingEnabled: true,
    flowParticlesEnabled: true,
    glowEnabled: true,
    curveSegments: 24,
  },
  /** Standard animations */
  high: {
    breathingEnabled: true,
    flowParticlesEnabled: true,
    glowEnabled: true,
    curveSegments: 16,
  },
  /** Reduced animations */
  standard: {
    breathingEnabled: true,
    flowParticlesEnabled: true,
    glowEnabled: false,
    curveSegments: 12,
  },
  /** Minimal animations for performance */
  minimal: {
    breathingEnabled: false,
    flowParticlesEnabled: false,
    glowEnabled: false,
    curveSegments: 8,
  },
} as const;

export type PerformanceTier = keyof typeof PERFORMANCE_TIERS;

// =============================================================================
// Combined Preset
// =============================================================================

/**
 * All animation presets combined for easy import.
 */
export const ANIMATION_PRESETS = {
  breathing: BREATHING,
  flowParticles: FLOW_PARTICLES,
  hover: HOVER,
  selection: SELECTION,
  edge: EDGE,
  violation: VIOLATION,
  growthRings: GROWTH_RINGS,
  performanceTiers: PERFORMANCE_TIERS,
} as const;

export default ANIMATION_PRESETS;
