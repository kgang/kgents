/**
 * Gestalt Components
 *
 * Visual showcase components for the Living Architecture Visualizer.
 *
 * Sprint 3: Forest Theme - Organic, plant-like visualization
 * "The codebase is a forest, not a machine."
 *
 * @see plans/gestalt-visual-showcase.md
 * @see plans/_continuations/gestalt-sprint3.md
 */

// Types
export * from './types';

// Chunk 1: Filter Components
export { FilterPanel } from './FilterPanel';
export { HealthFilter } from './HealthFilter';
export { ModuleSearch } from './ModuleSearch';
export { ViewPresets } from './ViewPresets';

// Chunk 2: Legend & Tooltip Components
export { Legend } from './Legend';
export type { LegendProps, NodeKindConfig, EdgeKindConfig } from './Legend';
export { NodeTooltip, StandaloneTooltip } from './NodeTooltip';
export type { NodeTooltipProps, StandaloneTooltipProps } from './NodeTooltip';

// Chunk 3: Edge Styling & Animation Components (Original)
export { AnimatedEdge, StaticEdge, SmartEdge } from './AnimatedEdge';
export type { AnimatedEdgeProps, StaticEdgeProps, SmartEdgeProps } from './AnimatedEdge';
export {
  EDGE_STYLES,
  getEdgeStyle,
  getHighlightedStyle,
  getDimmedStyle,
  getFlowConfig,
  DEFAULT_FLOW_CONFIG,
  VIOLATION_FLOW_CONFIG,
  calculatePulseOpacity,
  calculatePulseGlow,
} from './EdgeStyles';
export type { EdgeStyle, EdgeType, FlowAnimationConfig } from './EdgeStyles';

// Sprint 3: Organic/Forest Theme Components
export { OrganicNode } from './OrganicNode';
export type { OrganicNodeProps } from './OrganicNode';
export { VineEdge, SmartVineEdge } from './VineEdge';
export type { VineEdgeProps, SmartVineEdgeProps } from './VineEdge';
