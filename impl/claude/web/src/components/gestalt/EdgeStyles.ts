/**
 * Edge Styles - Semantic Edge Configuration
 *
 * Chunk 3: Transform static gray lines into semantic, informative data flows.
 *
 * Design philosophy:
 * - Imports are subtle background context (gray, thin)
 * - Violations demand attention (red, thick, pulsing)
 * - Future infrastructure types have distinct visual signatures
 *
 * @see plans/_continuations/gestalt-visual-showcase-chunk3.md
 */

// =============================================================================
// Types
// =============================================================================

/**
 * Complete edge style configuration.
 */
export interface EdgeStyle {
  /** Stroke color (hex or CSS color) */
  color: string;
  /** Whether to render as dashed line */
  dash: boolean;
  /** Dash array pattern if dashed [dash, gap] */
  dashArray?: [number, number];
  /** Line width in pixels */
  width: number;
  /** Base opacity (0-1) */
  opacity: number;
  /** Whether this edge type supports flow animation */
  animated?: boolean;
  /** Animation speed multiplier (1 = default) */
  animationSpeed?: number;
  /** Glow color for highlighted state */
  glowColor?: string;
  /** Glow intensity (0-1) */
  glowIntensity?: number;
}

/**
 * Edge type identifier.
 */
export type EdgeType =
  // Current types
  | 'import'
  | 'violation'
  // Future infrastructure types (Phase 5 prep)
  | 'reads'
  | 'writes'
  | 'calls'
  | 'publishes'
  | 'subscribes'
  | 'extends'
  | 'implements';

// =============================================================================
// Style Configuration
// =============================================================================

/**
 * Edge styles by type.
 *
 * Color semantics:
 * - Gray (#6b7280): neutral, background structure
 * - Red (#ef4444): danger, violations, attention
 * - Blue (#3b82f6): data reads, information flow
 * - Orange (#f97316): calls, function invocation
 * - Purple (#8b5cf6): events, pub/sub messaging
 * - Cyan (#06b6d4): inheritance, type relationships
 */
export const EDGE_STYLES: Record<EdgeType, EdgeStyle> = {
  // Current types (used now)
  import: {
    color: '#6b7280',
    dash: false,
    width: 1,
    opacity: 0.25,
    animated: false,
  },
  violation: {
    color: '#ef4444',
    dash: false,
    width: 2.5,
    opacity: 0.9,
    animated: true,
    animationSpeed: 0.5, // Slow, attention-drawing pulse
    glowColor: '#ef4444',
    glowIntensity: 0.3,
  },

  // Future infrastructure types (Phase 5 prep)
  reads: {
    color: '#3b82f6',
    dash: false,
    width: 2,
    opacity: 0.6,
    animated: true,
    animationSpeed: 1.0,
  },
  writes: {
    color: '#ef4444',
    dash: false,
    width: 2,
    opacity: 0.6,
    animated: true,
    animationSpeed: 0.8,
  },
  calls: {
    color: '#f97316',
    dash: true,
    dashArray: [4, 2],
    width: 1.5,
    opacity: 0.5,
    animated: true,
    animationSpeed: 1.5, // Fast, transient
  },
  publishes: {
    color: '#8b5cf6',
    dash: false,
    width: 1.5,
    opacity: 0.5,
    animated: true,
    animationSpeed: 1.2,
    glowColor: '#8b5cf6',
    glowIntensity: 0.2,
  },
  subscribes: {
    color: '#8b5cf6',
    dash: true,
    dashArray: [3, 3],
    width: 1.5,
    opacity: 0.5,
    animated: false,
  },
  extends: {
    color: '#06b6d4',
    dash: false,
    width: 2,
    opacity: 0.7,
    animated: false,
  },
  implements: {
    color: '#06b6d4',
    dash: true,
    dashArray: [5, 2],
    width: 1.5,
    opacity: 0.5,
    animated: false,
  },
};

// =============================================================================
// Style Selection
// =============================================================================

/**
 * Get edge style for a dependency link.
 *
 * @param isViolation - Whether this edge represents a violation
 * @param edgeType - Optional edge type override
 * @returns Complete edge style configuration
 */
export function getEdgeStyle(isViolation: boolean, edgeType?: string): EdgeStyle {
  if (isViolation) {
    return EDGE_STYLES.violation;
  }

  if (edgeType && edgeType in EDGE_STYLES) {
    return EDGE_STYLES[edgeType as EdgeType];
  }

  return EDGE_STYLES.import;
}

/**
 * Get style for selected/highlighted edges.
 * Increases visibility while maintaining semantic color.
 */
export function getHighlightedStyle(baseStyle: EdgeStyle): EdgeStyle {
  return {
    ...baseStyle,
    opacity: Math.min(baseStyle.opacity + 0.4, 1.0),
    width: baseStyle.width * 1.5,
    glowIntensity: (baseStyle.glowIntensity || 0) + 0.3,
  };
}

/**
 * Get style for dimmed/background edges.
 * Reduces visibility when not in focus.
 */
export function getDimmedStyle(baseStyle: EdgeStyle): EdgeStyle {
  return {
    ...baseStyle,
    opacity: baseStyle.opacity * 0.3,
    width: baseStyle.width * 0.8,
    animated: false, // Stop animation on dimmed edges
  };
}

// =============================================================================
// Animation Parameters
// =============================================================================

/**
 * Animation configuration for particle flow.
 */
export interface FlowAnimationConfig {
  /** Particle count per edge */
  particleCount: number;
  /** Particle radius */
  particleRadius: number;
  /** Base speed (units per second) */
  baseSpeed: number;
  /** Whether particles emit light */
  emissive: boolean;
}

/**
 * Default flow animation configuration.
 */
export const DEFAULT_FLOW_CONFIG: FlowAnimationConfig = {
  particleCount: 3,
  particleRadius: 0.04,
  baseSpeed: 0.4,
  emissive: true,
};

/**
 * Violation-specific animation configuration.
 * Larger particles, slower movement, draws attention.
 */
export const VIOLATION_FLOW_CONFIG: FlowAnimationConfig = {
  particleCount: 2,
  particleRadius: 0.06,
  baseSpeed: 0.2,
  emissive: true,
};

/**
 * Get flow animation config for an edge type.
 */
export function getFlowConfig(isViolation: boolean): FlowAnimationConfig {
  return isViolation ? VIOLATION_FLOW_CONFIG : DEFAULT_FLOW_CONFIG;
}

// =============================================================================
// Pulse Animation (Violations)
// =============================================================================

/**
 * Calculate pulse opacity for violation edges.
 * Gentle sine wave oscillation.
 *
 * @param time - Current time in seconds
 * @param baseOpacity - Base opacity value
 * @returns Animated opacity value
 */
export function calculatePulseOpacity(time: number, baseOpacity: number): number {
  // Slow sine wave: oscillate between 70% and 100% of base opacity
  const wave = Math.sin(time * 2) * 0.15 + 0.85;
  return baseOpacity * wave;
}

/**
 * Calculate pulse glow intensity for violation edges.
 *
 * @param time - Current time in seconds
 * @returns Glow intensity (0-1)
 */
export function calculatePulseGlow(time: number): number {
  // Pulse between 0.2 and 0.5
  return 0.35 + Math.sin(time * 2.5) * 0.15;
}
