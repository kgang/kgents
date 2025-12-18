/**
 * Gestalt Components
 *
 * UI components for the Living Architecture Visualizer.
 *
 * 2D Renaissance (2025-12-18): Three.js components mothballed.
 * See _mothballed/three-visualizers/gestalt/ for preserved components.
 *
 * Phase 3 (2025-12-18): Gestalt2D implementation complete.
 * - Gestalt2D: Main container with ElasticSplit
 * - LayerCard: Health-colored layer panels
 * - ViolationFeed: Streaming violation alerts
 * - ModuleDetail: Module detail side panel
 *
 * @see spec/protocols/2d-renaissance.md
 */

// Types
export * from './types';

// =============================================================================
// Gestalt2D Components (Phase 3 - 2D Renaissance)
// =============================================================================

export { Gestalt2D } from './Gestalt2D';
export type { Gestalt2DProps } from './Gestalt2D';

export { LayerCard } from './LayerCard';
export type { LayerCardProps } from './LayerCard';

export { ViolationFeed } from './ViolationFeed';
export type { ViolationFeedProps } from './ViolationFeed';

export { ModuleDetail } from './ModuleDetail';
export type { ModuleDetailProps } from './ModuleDetail';

// =============================================================================
// Filter Components (KEEP - reusable)
// =============================================================================

export { FilterPanel } from './FilterPanel';
export { HealthFilter } from './HealthFilter';
export { ModuleSearch } from './ModuleSearch';
export { ViewPresets } from './ViewPresets';

// =============================================================================
// Legend & Tooltip Components (KEEP - reusable)
// =============================================================================

export { Legend } from './Legend';
export type { LegendProps, NodeKindConfig, EdgeKindConfig } from './Legend';
export { NodeTooltip, StandaloneTooltip } from './NodeTooltip';
export type { NodeTooltipProps, StandaloneTooltipProps } from './NodeTooltip';

// Edge Styles (KEEP - types and utilities, no Three.js)
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

// =============================================================================
// MOTHBALLED (2025-12-18): Three.js visualization components
// Preserved in: _mothballed/three-visualizers/gestalt/
// - GestaltVisualization.tsx (1060 lines)
// - OrganicNode.tsx
// - VineEdge.tsx
// - AnimatedEdge.tsx
// Revival condition: VR/AR projections or 3D-specific requirements
// =============================================================================
