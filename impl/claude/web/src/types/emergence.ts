/**
 * Emergence Visualization Types
 *
 * Type definitions for the emergence visualization system:
 * - Cymatics (wave interference patterns)
 * - Differential Growth (organic form emergence)
 *
 * These types are isomorphic to the Python implementations in:
 * - impl/claude/agents/i/reactive/animation/cymatics.py
 * - impl/claude/agents/i/reactive/animation/growth.py
 *
 * Philosophy:
 *   "Cymatics makes vibration visible. Growth makes emergence tangible.
 *    Both reveal the hidden structure—we simply found the medium."
 *
 * @see docs/creative/emergence-principles.md
 */

// =============================================================================
// Cymatics Types
// =============================================================================

/**
 * A source of vibration in the cymatics field.
 *
 * Represents an agent, event, or state change that creates "ripples"
 * in the visualization space.
 */
export interface VibrationSource {
  /** Vibration frequency in Hz (0.1 to 10 typical). Higher = faster oscillation. */
  frequency: number;
  /** Intensity of the vibration (0-1). Higher = stronger waves. */
  amplitude: number;
  /** Phase offset in radians (0 to 2*PI). Used for synchronization. */
  phase: number;
  /** (x, y) position in normalized space (-1 to 1). */
  position: [number, number];
  /** Distance decay factor. Higher = waves fade faster with distance. */
  decay: number;
}

/**
 * Result of cymatics interference computation.
 *
 * A Chladni pattern shows where waves constructively and destructively
 * interfere. Nodes are points of high amplitude; antinodes are points
 * of low amplitude.
 */
export interface ChladniPattern {
  /** Points of constructive interference (high amplitude regions) */
  nodes: Array<[number, number]>;
  /** Points of destructive interference (low amplitude regions) */
  antinodes: Array<[number, number]>;
  /** Minimum amplitude in the pattern */
  minAmplitude: number;
  /** Maximum amplitude in the pattern */
  maxAmplitude: number;
  /** Pattern stability score (0 = chaotic, 1 = harmonic) */
  stability: number;
}

/**
 * Configuration for the CymaticsField component.
 */
export interface CymaticsConfig {
  /** Grid resolution for rendering (higher = more detail, slower) */
  resolution?: number;
  /** Color scheme for the visualization */
  colorScheme?: 'cool' | 'warm' | 'neutral' | 'coalition';
  /** Whether to show the interference pattern grid */
  showGrid?: boolean;
  /** Whether to animate the field over time */
  animate?: boolean;
  /** Animation speed multiplier */
  animationSpeed?: number;
  /** Whether to show node/antinode markers */
  showMarkers?: boolean;
}

/**
 * Default source for coalition health visualization.
 * Harmonic sources produce stable patterns.
 */
export function createHarmonicSource(
  position: [number, number],
  frequency = 2.0,
  amplitude = 1.0
): VibrationSource {
  return {
    frequency,
    amplitude,
    phase: 0,
    position,
    decay: 0.5,
  };
}

/**
 * Create a ring of harmonic sources for symmetric patterns.
 */
export function createHarmonicRing(
  count: number,
  radius = 0.5,
  frequency = 2.0,
  amplitude = 1.0
): VibrationSource[] {
  const sources: VibrationSource[] = [];
  for (let i = 0; i < count; i++) {
    const angle = (2 * Math.PI * i) / count;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);
    sources.push(createHarmonicSource([x, y], frequency, amplitude));
  }
  return sources;
}

/**
 * Create dissonant sources for visualizing conflict/stress.
 */
export function createDissonantSources(
  frequencies: number[],
  amplitude = 1.0,
  spread = 0.3
): VibrationSource[] {
  const count = frequencies.length;
  return frequencies.map((freq, i) => ({
    frequency: freq,
    amplitude,
    phase: 0,
    position: [
      count > 1 ? -spread + (2 * spread * i) / (count - 1) : 0,
      0,
    ] as [number, number],
    decay: 0.5,
  }));
}

// =============================================================================
// Differential Growth Types
// =============================================================================

/**
 * Rules governing differential growth behavior.
 */
export interface GrowthRules {
  /** Pull toward targets (0-1). Higher = faster convergence. */
  attraction: number;
  /** Push from neighbors (0-1). Higher = more spacing. */
  repulsion: number;
  /** Follow local direction (0-1). Higher = smoother curves. */
  alignment: number;
  /** Accursed share injection (0-1). Higher = more organic. */
  randomness: number;
  /** Base growth per step. */
  growthRate: number;
  /** Minimum distance between nodes. */
  minDistance: number;
  /** Velocity damping (0-1). Higher = faster settling. */
  damping: number;
}

/**
 * A node in the growth simulation.
 */
export interface GrowthNode {
  /** Unique identifier */
  id: string;
  /** 3D position (x, y, z) */
  position: [number, number, number];
  /** Current velocity vector */
  velocity: [number, number, number];
  /** Optional target position for attraction */
  target?: [number, number, number];
  /** Age in simulation steps */
  age: number;
  /** If true, node cannot move */
  fixed: boolean;
  /** Node importance (affects repulsion strength) */
  weight: number;
}

/**
 * An edge growing between two nodes.
 *
 * Edges don't teleport into existence—they grow from source to target.
 */
export interface GrowthEdge {
  /** Unique identifier */
  id: string;
  /** Source node ID */
  sourceId: string;
  /** Target node ID */
  targetId: string;
  /** Growth progress (0 = none, 1 = complete) */
  progress: number;
  /** Intermediate points for organic paths */
  waypoints: Array<[number, number, number]>;
  /** Speed multiplier for this edge */
  growthRate: number;
}

/**
 * Growth rules presets.
 */
export const GROWTH_PRESETS: Record<string, GrowthRules> = {
  /** Organic preset: high randomness, moderate forces */
  organic: {
    attraction: 0.2,
    repulsion: 0.3,
    alignment: 0.2,
    randomness: 0.2,
    growthRate: 0.05,
    minDistance: 0.1,
    damping: 0.9,
  },
  /** Crystalline preset: low randomness, strong structure */
  crystalline: {
    attraction: 0.4,
    repulsion: 0.5,
    alignment: 0.3,
    randomness: 0.05,
    growthRate: 0.05,
    minDistance: 0.1,
    damping: 0.9,
  },
  /** Fluid preset: low repulsion, high alignment */
  fluid: {
    attraction: 0.3,
    repulsion: 0.2,
    alignment: 0.4,
    randomness: 0.15,
    growthRate: 0.05,
    minDistance: 0.1,
    damping: 0.9,
  },
};

/**
 * State of the growth animation.
 */
export interface GrowthAnimationState {
  /** Current simulation time */
  time: number;
  /** Total kinetic energy (for detecting settling) */
  kineticEnergy: number;
  /** Whether the system has settled */
  isSettled: boolean;
  /** Active edges being animated */
  activeEdges: GrowthEdge[];
}

// =============================================================================
// Integration Types (Brain Topology)
// =============================================================================

/**
 * Configuration for organic edge growth in BrainTopology.
 */
export interface EdgeGrowthConfig {
  /** Whether to animate edge growth */
  enabled: boolean;
  /** Growth preset to use */
  preset: keyof typeof GROWTH_PRESETS;
  /** Custom rules (overrides preset) */
  customRules?: Partial<GrowthRules>;
  /** Animation duration in ms */
  duration: number;
  /** Whether to show growth trail */
  showTrail: boolean;
}

/**
 * Default edge growth config for BrainTopology.
 */
export const DEFAULT_EDGE_GROWTH_CONFIG: EdgeGrowthConfig = {
  enabled: true,
  preset: 'organic',
  duration: 1500,
  showTrail: true,
};

// =============================================================================
// Shader Uniforms Types
// =============================================================================

/**
 * Uniforms for the cymatics shader.
 */
export interface CymaticsUniforms {
  /** Current time for animation */
  uTime: number;
  /** Number of active vibration sources */
  uSourceCount: number;
  /** Source positions (flat array: [x1, y1, x2, y2, ...]) */
  uSourcePositions: number[];
  /** Source frequencies */
  uSourceFrequencies: number[];
  /** Source amplitudes */
  uSourceAmplitudes: number[];
  /** Source phases */
  uSourcePhases: number[];
  /** Source decay factors */
  uSourceDecays: number[];
  /** Primary color */
  uColorPrimary: [number, number, number];
  /** Secondary color */
  uColorSecondary: [number, number, number];
}
