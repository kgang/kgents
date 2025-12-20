/**
 * Generated types for AGENTESE path: world.scenery
 * SceneGraph projection types for React consumption.
 *
 * DO NOT EDIT - regenerate with: npm run sync-types
 */

// =============================================================================
// Enums
// =============================================================================

/**
 * Semantic node types for scene rendering.
 * Each kind maps to specific visual semantics in React components.
 */
export type SceneNodeKind =
  | 'PANEL' // Container with borders and padding
  | 'TRACE' // TraceNode visualization (timeline item)
  | 'INTENT' // IntentTree node (task/goal)
  | 'OFFERING' // Offering badge (context indicator)
  | 'COVENANT' // Permission indicator (trust level)
  | 'WALK' // Walk timeline (session progress)
  | 'RITUAL' // Ritual state (workflow phase)
  | 'TEXT' // Plain text content
  | 'GROUP'; // Grouping container (no visual, just structure)

/**
 * Elastic layout modes.
 */
export type LayoutMode = 'COMPACT' | 'COMFORTABLE' | 'SPACIOUS';

/**
 * Lens transformation modes.
 */
export type LensMode = 'TIMELINE' | 'GRAPH' | 'SUMMARY' | 'DETAIL';

/**
 * View lifecycle status.
 */
export type ViewStatus = 'IDLE' | 'ACTIVE' | 'PAUSED' | 'CRASHED';

/**
 * Selection operators for filtering.
 */
export type SelectionOperator =
  | 'EQ'
  | 'NE'
  | 'IN'
  | 'NOT_IN'
  | 'CONTAINS'
  | 'STARTS_WITH'
  | 'GT'
  | 'LT'
  | 'GTE'
  | 'LTE';

// =============================================================================
// Layout
// =============================================================================

/**
 * Declarative layout specification.
 * Layouts are elastic: they adapt to the projection target's capabilities.
 */
export interface LayoutDirective {
  direction: 'vertical' | 'horizontal' | 'grid' | 'free';
  mode: LayoutMode;
  gap: number;
  padding: number;
  align: 'start' | 'center' | 'end' | 'stretch';
  wrap: boolean;
}

// =============================================================================
// Style (Joy-Inducing)
// =============================================================================

/**
 * Node visual style.
 * These are hints to the projection target.
 */
export interface NodeStyle {
  // Colors (Living Earth palette)
  background?: string | null;
  foreground?: string | null;
  border?: string | null;

  // Animation hints
  breathing: boolean;
  unfurling: boolean;

  // Texture hints
  paper_grain: boolean;

  // Opacity
  opacity: number;
}

// =============================================================================
// Interaction
// =============================================================================

/**
 * Node interaction hint.
 */
export interface Interaction {
  kind: 'click' | 'hover' | 'focus' | 'drag';
  action: string; // AGENTESE path or callback name
  requires_trust: number; // Minimum trust level (0-3)
  metadata?: Record<string, unknown>;
}

// =============================================================================
// SceneNode
// =============================================================================

/**
 * Atomic visual element in the scene graph.
 */
export interface SceneNode {
  id: string;
  kind: SceneNodeKind;
  content: unknown;
  label: string;
  style: NodeStyle;
  flex: number;
  min_width?: number | null;
  min_height?: number | null;
  interactions: Interaction[];
  metadata: Record<string, unknown>;
}

// =============================================================================
// SceneEdge
// =============================================================================

/**
 * Edge between SceneNodes in a graph layout.
 */
export interface SceneEdge {
  source: string;
  target: string;
  label: string;
  style: 'solid' | 'dashed' | 'dotted';
  metadata?: Record<string, unknown>;
}

// =============================================================================
// SceneGraph
// =============================================================================

/**
 * Composable scene structure with category laws.
 *
 * Laws:
 * - Law 1 (Identity): SceneGraph.empty() >> G == G == G >> SceneGraph.empty()
 * - Law 2 (Associativity): (A >> B) >> C == A >> (B >> C)
 */
export interface SceneGraph {
  id: string;
  nodes: SceneNode[];
  edges: SceneEdge[];
  layout: LayoutDirective;
  title: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// =============================================================================
// Selection Query
// =============================================================================

/**
 * Single predicate in a selection query.
 */
export interface SelectionPredicate {
  field: string;
  op: SelectionOperator;
  value: unknown;
}

/**
 * Query for selecting TraceNodes to display.
 */
export interface SelectionQuery {
  predicates: SelectionPredicate[];
  limit?: number | null;
  offset: number;
  order_by: string;
  descending: boolean;
}

// =============================================================================
// Lens Config
// =============================================================================

/**
 * Configuration for how to transform traces into visual elements.
 */
export interface LensConfig {
  mode: LensMode;
  show_links: boolean;
  show_umwelt: boolean;
  show_metadata: boolean;
  group_by?: string | null;
  collapse_threshold: number;
  node_style: NodeStyle;
  layout: LayoutDirective;
}

// =============================================================================
// TerrariumView
// =============================================================================

/**
 * Configured projection over TraceNode streams.
 */
export interface TerrariumView {
  id: string;
  name: string;
  selection: SelectionQuery;
  lens: LensConfig;
  status: ViewStatus;
  fault_isolated: boolean;
  observer_id?: string | null;
  trust_level: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

// =============================================================================
// AGENTESE Request/Response Types
// =============================================================================

/**
 * Response for world.scenery.manifest
 */
export interface WorldSceneryManifestResponse {
  path: string;
  description: string;
  scene: SceneGraph;
  views: {
    total: number;
    active: number;
  };
  node_kinds: SceneNodeKind[];
  lens_modes: LensMode[];
  laws: string[];
}

/**
 * SSE event for world.scenery.stream
 */
export interface WorldSceneryStreamEvent {
  type: 'scene';
  graph: SceneGraph;
  timestamp: string;
  event_count: number;
}

/**
 * Request for world.scenery.create_view
 */
export interface WorldSceneryCreateViewRequest {
  name?: string;
  lens_mode?: 'timeline' | 'graph' | 'summary' | 'detail';
  origin_filter?: string | null;
  limit?: number;
}

/**
 * Response for world.scenery.create_view
 */
export interface WorldSceneryCreateViewResponse {
  created: boolean;
  view: TerrariumView;
}

/**
 * Response for world.scenery.list_views
 */
export interface WorldSceneryListViewsResponse {
  count: number;
  views: TerrariumView[];
}

/**
 * Request for world.scenery.project
 */
export interface WorldSceneryProjectRequest {
  view_id?: string | null;
  traces?: Record<string, unknown>[] | null;
}

/**
 * Response for world.scenery.project
 */
export interface WorldSceneryProjectResponse {
  view_id: string;
  view_name: string;
  lens_mode: LensMode;
  scene: SceneGraph;
}

// =============================================================================
// Helper Types for React Components
// =============================================================================

/**
 * Props for SceneNode React components.
 */
export interface SceneNodeProps {
  node: SceneNode;
  onClick?: (nodeId: string) => void;
  onHover?: (nodeId: string, isHovered: boolean) => void;
}

/**
 * Props for SceneRenderer.
 */
export interface SceneRendererProps {
  graph: SceneGraph;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

/**
 * Default node style.
 */
export const DEFAULT_NODE_STYLE: NodeStyle = {
  background: null,
  foreground: null,
  border: null,
  breathing: false,
  unfurling: false,
  paper_grain: false,
  opacity: 1.0,
};

/**
 * Default layout directive.
 */
export const DEFAULT_LAYOUT: LayoutDirective = {
  direction: 'vertical',
  mode: 'COMFORTABLE',
  gap: 1.0,
  padding: 1.0,
  align: 'start',
  wrap: false,
};
