/**
 * Theme Types for 3D Projection Primitives
 *
 * Defines the common interface for all 3D themes (crystal, forest, etc.)
 * following the THREE_PROJECTION_OPERAD composition laws.
 *
 * @see plans/3d-projection-consolidation.md
 * @see spec/protocols/projection.md
 */

// =============================================================================
// Core Theme Interfaces
// =============================================================================

/**
 * Color palette for node tiers.
 * Each tier represents a state/quality level determined by domain-specific metrics.
 */
export interface NodeTierColors {
  /** Main node color */
  core: string;
  /** Emissive/glow color */
  glow: string;
  /** Growth ring / indicator ring color */
  ring: string;
}

/**
 * Color palette for edge states.
 */
export interface EdgeColors {
  /** Normal state base color */
  base: string;
  /** Active/selected highlight color */
  highlight: string;
  /** Glow effect color */
  glow: string;
  /** Optional violation/error state color */
  violation?: string;
}

/**
 * Color palette for flow particles.
 */
export interface ParticleColors {
  /** Normal flow particle color */
  normal: string;
  /** Active/highlighted flow particle color */
  active: string;
}

/**
 * Scene atmosphere settings.
 */
export interface AtmosphereConfig {
  /** Fog settings */
  fog?: {
    color: string;
    near: number;
    far: number;
  };
  /** Background color */
  background?: string;
  /** Ambient light tint */
  ambientTint?: string;
}

/**
 * Complete theme palette for 3D projections.
 *
 * Philosophy: Themes are not just colors—they are complete visual identities
 * that emerge from the domain's conceptual model.
 *
 * Crystal theme → memories as gemstones, resolution as clarity
 * Forest theme → code as organisms, health as vitality
 */
export interface ThemePalette {
  /** Theme identifier */
  name: string;

  /** Human-readable description */
  description: string;

  /**
   * Node colors by tier.
   * Keys are domain-specific tier names (e.g., 'vivid', 'ghost' for crystal;
   * 'healthy', 'critical' for forest).
   */
  nodeTiers: Record<string, NodeTierColors>;

  /** Edge colors for various states */
  edgeColors: EdgeColors;

  /** Particle colors for flow animations */
  particleColors: ParticleColors;

  /** Optional scene atmosphere */
  atmosphere?: AtmosphereConfig;

  /** Selection indicator color */
  selectionColor: string;

  /** Hover indicator color */
  hoverColor: string;

  /** Label text color */
  labelColor: string;

  /** Label outline color */
  labelOutlineColor: string;
}

// =============================================================================
// Tier Calculation
// =============================================================================

/**
 * Function type for calculating tier from domain data.
 * Different domains use different metrics (resolution, health score, etc.)
 *
 * @template T - The domain data type
 */
export type TierCalculator<T> = (data: T) => string;

/**
 * Function type for calculating node size from domain data.
 *
 * @template T - The domain data type
 */
export type SizeCalculator<T> = (data: T, density: Density) => number;

// =============================================================================
// Shared Types
// =============================================================================

/**
 * Layout density - controls spacing and sizing.
 * Shared across Brain, Gestalt, and all 3D projections.
 */
export type Density = 'compact' | 'comfortable' | 'spacious';

/**
 * Label configuration by density.
 */
export interface LabelConfig {
  fontSize: number;
  offset: number;
}

/**
 * Default label configs by density.
 */
export const LABEL_CONFIGS: Record<Density, LabelConfig> = {
  compact: { fontSize: 0.12, offset: 0.2 },
  comfortable: { fontSize: 0.14, offset: 0.25 },
  spacious: { fontSize: 0.18, offset: 0.3 },
} as const;

// =============================================================================
// Theme Validation
// =============================================================================

/**
 * Validate that a theme has all required tiers.
 * Returns list of missing tier names.
 */
export function validateThemeTiers(theme: ThemePalette, requiredTiers: string[]): string[] {
  const missing: string[] = [];
  for (const tier of requiredTiers) {
    if (!(tier in theme.nodeTiers)) {
      missing.push(tier);
    }
  }
  return missing;
}

/**
 * Get tier colors with fallback to first available tier.
 * Ensures graceful degradation if tier is not found.
 */
export function getTierColors(theme: ThemePalette, tier: string): NodeTierColors {
  if (tier in theme.nodeTiers) {
    return theme.nodeTiers[tier];
  }
  // Fallback to first available tier
  const tiers = Object.keys(theme.nodeTiers);
  if (tiers.length > 0) {
    return theme.nodeTiers[tiers[0]];
  }
  // Ultimate fallback
  return {
    core: '#666666',
    glow: '#888888',
    ring: '#444444',
  };
}
