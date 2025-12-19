/**
 * Gestalt Components
 *
 * UI components for the Living Architecture Visualizer.
 *
 * Components:
 * - Gestalt2D: Main container with ElasticSplit
 * - LayerCard: Health-colored layer panels
 * - ViolationFeed: Streaming violation alerts
 * - ModuleDetail: Module detail side panel
 */

// Types
export * from './types';

// =============================================================================
// Gestalt2D Components (Phase 3 - 2D Renaissance)
// =============================================================================

export { Gestalt2D } from './Gestalt2D';
export type { Gestalt2DProps } from './Gestalt2D';

// =============================================================================
// GestaltTree Components (Phase 4 - Living Architecture Navigator)
// =============================================================================

export {
  GestaltTree,
  GestaltTreeNode,
  HealthBadge,
  HealthBadgeLarge,
  buildGestaltTree,
  buildLayerTree,
  buildPathTree,
  getViolationMap,
  GRADE_ORDER,
  gradeToNumber,
  numberToGrade,
  getWorstGrade,
} from './GestaltTree';
export type {
  GestaltNode,
  GestaltTreeProps,
  GestaltTreeNodeProps,
  HealthBadgeProps,
  TreeMode,
} from './GestaltTree';

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
// Legend Components (KEEP - reusable)
// =============================================================================

export { Legend } from './Legend';
export type { LegendProps, NodeKindConfig, EdgeKindConfig } from './Legend';

// Edge Styles (types and utilities)
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
