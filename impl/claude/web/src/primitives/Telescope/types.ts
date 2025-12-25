/**
 * Telescope Types
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * A universal viewer with focal distance, aperture, and filter controls.
 * Replaces GaloisTelescope (1,200 LOC) + TelescopeNavigator (800 LOC) with ~400 LOC.
 */

// =============================================================================
// Geometric Primitives
// =============================================================================

export interface Point {
  x: number;
  y: number;
}

export interface GradientVector {
  x: number;
  y: number;
  magnitude: number;
}

// =============================================================================
// Node Projection
// =============================================================================

export interface NodeProjection {
  node_id: string;
  layer: number;
  position: Point;
  scale: number;
  opacity: number;
  is_focal: boolean;
  color: string; // CSS color (viridis-mapped from loss)
  loss?: number;
  gradient?: GradientVector;
}

// =============================================================================
// Telescope State
// =============================================================================

export interface TelescopeState {
  focalDistance: number; // 0 = ground (L7), 1 = cosmic (L1)
  focalPoint: string | null; // Currently focused node ID
  visibleLayers: number[]; // Derived from focalDistance
  lossThreshold: number; // Filter nodes by loss (0-1)
}

// =============================================================================
// Telescope Props
// =============================================================================

export interface TelescopeProps {
  /** Node projections to render */
  nodes: NodeProjection[];

  /** Gradient vectors by node ID */
  gradients: Map<string, GradientVector>;

  /** Callback when node is clicked */
  onNodeClick?: (nodeId: string) => void;

  /** Callback when navigation occurs */
  onNavigate?: (nodeId: string, direction: NavigationDirection) => void;

  /** Initial telescope state */
  initialState?: Partial<TelescopeState>;

  /** Enable keyboard navigation */
  keyboardEnabled?: boolean;

  /** Canvas dimensions */
  width?: number;
  height?: number;
}

// =============================================================================
// Navigation
// =============================================================================

export type NavigationDirection = 'focus' | 'gradient' | 'lowest' | 'highest';

export interface GradientArrow {
  start: Point;
  end: Point;
  color: string;
  magnitude: number;
  width: number;
}

// =============================================================================
// Layer Metadata
// =============================================================================

export const LAYER_NAMES: Record<number, string> = {
  1: 'Axioms',
  2: 'Values',
  3: 'Goals',
  4: 'Specs',
  5: 'Actions',
  6: 'Reflections',
  7: 'Representations',
};

export const LAYER_BASE_COLORS: Record<number, string> = {
  1: '#8B4513', // Saddle brown
  2: '#228B22', // Forest green
  3: '#4169E1', // Royal blue
  4: '#9932CC', // Dark orchid
  5: '#DC143C', // Crimson
  6: '#FFD700', // Gold
  7: '#F5F5F5', // White smoke
};
