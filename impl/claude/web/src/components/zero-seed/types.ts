/**
 * Zero Seed Navigation Types
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 */

// -----------------------------------------------------------------------------
// Type Aliases
// -----------------------------------------------------------------------------

export type NodeId = string;
export type EdgeId = string;

// -----------------------------------------------------------------------------
// Geometric Primitives
// -----------------------------------------------------------------------------

export interface Vector2D {
  x: number;
  y: number;
}

export interface Position2D {
  x: number;
  y: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

// -----------------------------------------------------------------------------
// Colors
// -----------------------------------------------------------------------------

export interface Color {
  r: number;
  g: number;
  b: number;
  alpha?: number;
}

export type ColormapName = 'viridis' | 'coolwarm' | 'terrain';

// -----------------------------------------------------------------------------
// Loss Types
// -----------------------------------------------------------------------------

export interface GaloisLossComponents {
  content_loss: number;
  proof_loss: number;
  edge_loss: number;
  metadata_loss: number;
  total: number;
}

export interface NodeGaloisLoss {
  node_id: NodeId;
  loss: number;
  components: GaloisLossComponents;
}

export interface LossAnnotation {
  loss: number;
  components: GaloisLossComponents;
  threshold_status: 'visible' | 'hidden';
  tooltip: string;
}

// -----------------------------------------------------------------------------
// Gradient Field
// -----------------------------------------------------------------------------

export interface GradientVector {
  x: number;
  y: number;
  magnitude: number;
}

export interface LossGradientField {
  vectors: Record<NodeId, GradientVector>;
}

// -----------------------------------------------------------------------------
// Node Projection
// -----------------------------------------------------------------------------

export interface NodeProjection {
  node_id: NodeId;
  layer: number;
  position: Position2D;
  scale: number;
  opacity: number;
  is_focal: boolean;
  color: string; // CSS color string
  color_hex: string;
  glow: boolean;
  glow_intensity: number;
  gradient?: GradientVector;
  annotation?: LossAnnotation;
}

// -----------------------------------------------------------------------------
// Gradient Arrow
// -----------------------------------------------------------------------------

export interface GradientArrow {
  start: Position2D;
  end: Position2D;
  magnitude: number;
  color: string;
  width: number;
}

// -----------------------------------------------------------------------------
// Telescope State
// -----------------------------------------------------------------------------

export interface GaloisTelescopeState {
  focal_distance: number;
  focal_point: NodeId | null;
  show_loss: boolean;
  show_gradient: boolean;
  loss_threshold: number;
  loss_colormap: ColormapName;
  visible_layers: number[];
  node_scale: number;
  preferred_layer: number;
}

// -----------------------------------------------------------------------------
// Navigation Actions
// -----------------------------------------------------------------------------

export type NavigationAction =
  | 'focus'
  | 'zoom_in'
  | 'zoom_out'
  | 'go_lowest_loss'
  | 'go_highest_loss'
  | 'follow_gradient'
  | 'toggle_loss'
  | 'toggle_gradient'
  | 'decrease_threshold'
  | 'increase_threshold';

// -----------------------------------------------------------------------------
// Layer Visualization
// -----------------------------------------------------------------------------

export type NodeShape =
  | 'circle' // L1 Axioms
  | 'diamond' // L2 Values
  | 'star' // L3 Goals
  | 'rectangle' // L4 Specs
  | 'hexagon' // L5 Actions
  | 'octagon' // L6 Reflections
  | 'cloud'; // L7 Representations

export const LAYER_SHAPES: Record<number, NodeShape> = {
  1: 'circle',
  2: 'diamond',
  3: 'star',
  4: 'rectangle',
  5: 'hexagon',
  6: 'octagon',
  7: 'cloud',
};

export const LAYER_NAMES: Record<number, string> = {
  1: 'Axioms',
  2: 'Values',
  3: 'Goals',
  4: 'Specs',
  5: 'Actions',
  6: 'Reflections',
  7: 'Representations',
};

// Base colors for each layer (before loss blending)
export const LAYER_BASE_COLORS: Record<number, string> = {
  1: '#8B4513', // Saddle brown
  2: '#228B22', // Forest green
  3: '#4169E1', // Royal blue
  4: '#9932CC', // Dark orchid
  5: '#DC143C', // Crimson
  6: '#FFD700', // Gold
  7: '#F5F5F5', // White smoke
};

// -----------------------------------------------------------------------------
// API Response Types
// -----------------------------------------------------------------------------

export interface NavigationResponse {
  telescope_state: GaloisTelescopeState;
  projections: NodeProjection[];
  gradient_arrows: GradientArrow[];
  high_loss_nodes: Array<{
    node_id: NodeId;
    loss: number;
    reason: string;
  }>;
}

export interface NavigateToResponse {
  previous: NodeId | null;
  current: NodeId;
  loss: number;
  gradient_magnitude: number;
  at_local_minimum: boolean;
}

// -----------------------------------------------------------------------------
// Keybinding Map
// -----------------------------------------------------------------------------

export const NAVIGATION_KEYBINDINGS = {
  // Loss navigation
  gl: 'go_lowest_loss',
  gh: 'go_highest_loss',
  'Shift+G': 'follow_gradient', // gradient symbol approximation
  L: 'toggle_loss',
  G: 'toggle_gradient',
  '[': 'decrease_threshold',
  ']': 'increase_threshold',

  // Telescope navigation
  '+': 'zoom_in',
  '-': 'zoom_out',
  '=': 'auto_focus',
  '0': 'reset_macro',
  'Shift+0': 'reset_micro',

  // Layer navigation
  '1': 'goto_layer_1',
  '2': 'goto_layer_2',
  '3': 'goto_layer_3',
  '4': 'goto_layer_4',
  '5': 'goto_layer_5',
  '6': 'goto_layer_6',
  '7': 'goto_layer_7',
  Tab: 'next_layer',
  'Shift+Tab': 'prev_layer',
} as const;
