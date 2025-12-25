/**
 * SceneGraph types for Interactive Text rendering.
 *
 * These types mirror the backend's scene.py and tokens_to_scene.py structures,
 * enabling type-safe rendering of meaning tokens.
 *
 * See: protocols/agentese/projection/tokens_to_scene.py
 */

// =============================================================================
// Token Kinds (from MeaningTokenKind enum)
// =============================================================================

export type MeaningTokenKind =
  | 'AGENTESE_PORTAL' // AGENTESE path with navigate/hover
  | 'TASK_TOGGLE' // Checkbox with toggle affordance
  | 'IMAGE_EMBED' // Image with expand/analyze
  | 'CODE_REGION' // Code block with run/edit
  | 'PRINCIPLE_ANCHOR' // Principle reference badge
  | 'REQUIREMENT_TRACE' // Requirement reference badge
  | 'MARKDOWN_TABLE' // Table with export/edit
  | 'LINK' // Hyperlink with preview
  | 'BLOCKQUOTE' // Quoted text block
  | 'HORIZONTAL_RULE' // Section divider
  | 'PORTAL' // Expandable hyperedge (from SYNTHESIS-living-spec)
  | 'PRINCIPLE' // Principle reference (unified from PRINCIPLE_ANCHOR)
  | 'IMAGE' // Image with AI analysis (unified from IMAGE_EMBED)
  | 'PLAIN_TEXT'; // Non-token text (markdown prose)

// Also include base SceneNodeKind values
export type SceneNodeKind = MeaningTokenKind | 'TEXT' | 'PANEL' | 'GROUP';

// =============================================================================
// Token Content (from MeaningTokenContent dataclass)
// =============================================================================

export interface MeaningTokenContent {
  token_type: string; // e.g., "agentese_path", "task_checkbox"
  source_text: string; // Original text
  source_position: [number, number]; // (start, end)
  token_id: string; // Unique identifier
  token_data: Record<string, unknown>; // Token-specific data
  affordances: Affordance[]; // Serialized affordances
}

export interface Affordance {
  name: string;
  action: string; // "click", "hover", "drag", etc.
  handler: string;
  enabled: boolean;
}

// =============================================================================
// Node Style (from NodeStyle dataclass)
// =============================================================================

export interface NodeStyle {
  foreground?: string;
  background?: string;
  border?: string;
  breathing?: boolean;
  paper_grain?: boolean;
  unfurling?: boolean;
}

// =============================================================================
// Interaction (from Interaction dataclass)
// =============================================================================

export interface Interaction {
  kind: string; // "click", "hover", etc.
  action: string; // Handler function name
  requires_trust: number;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Scene Node (from SceneNode dataclass)
// =============================================================================

export interface SceneNode {
  id: string;
  kind: SceneNodeKind;
  content: MeaningTokenContent | string | Record<string, unknown>;
  label: string;
  style: NodeStyle;
  flex: number;
  min_width: number | null;
  min_height: number | null;
  interactions: Interaction[];
  /** Section index for Document Proxy incremental updates (null if not section-aware) */
  section_index: number | null;
  metadata: Record<string, unknown>;
}

// =============================================================================
// Layout Directive (from LayoutDirective dataclass)
// =============================================================================

export interface LayoutDirective {
  direction: 'vertical' | 'horizontal';
  gap: number;
  padding: number;
  mode: 'COMPACT' | 'COMFORTABLE' | 'SPACIOUS';
}

// =============================================================================
// Scene Edge (from SceneEdge dataclass)
// =============================================================================

export interface SceneEdge {
  source: string;
  target: string;
  label: string;
  style: 'solid' | 'dashed' | 'dotted';
  metadata: Record<string, unknown>;
}

// =============================================================================
// Scene Graph (from SceneGraph dataclass)
// =============================================================================

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
// Type Guards
// =============================================================================

export function isMeaningTokenContent(
  content: SceneNode['content']
): content is MeaningTokenContent {
  return (
    typeof content === 'object' &&
    content !== null &&
    'token_type' in content &&
    'source_text' in content
  );
}

export function isTextContent(content: SceneNode['content']): content is string {
  return typeof content === 'string';
}

// =============================================================================
// Token-specific content helpers
// =============================================================================

export interface AGENTESEPathData {
  path: string;
  exists: boolean;
}

export interface TaskCheckboxData {
  checked: boolean;
  description: string;
}

export interface CodeBlockData {
  language: string;
  code: string;
}

export interface ImageData {
  src: string;
  alt_text: string;
}

export interface MarkdownTableData {
  columns: Array<{
    header: string;
    alignment: 'left' | 'center' | 'right';
    index: number;
  }>;
  rows: string[][];
  row_count: number;
  column_count: number;
}

export interface LinkData {
  text: string;
  url: string;
}

export interface BlockquoteData {
  content: string;
  attribution?: string;
}

export interface HorizontalRuleData {
  style?: 'single' | 'double' | 'dashed';
}

// =============================================================================
// NEW: Portal Token Data (from SYNTHESIS-living-spec.md + §15 Deep Integration)
// =============================================================================

/**
 * Portal authoring state — beyond expand/collapse.
 * See spec/protocols/portal-token.md §15.2
 *
 * RESOLVED: Has edge_type -> destination (can be expanded)
 * UNPARSED: Natural language query, missing -> (can be cured)
 * CURING: LLM resolution in progress
 * FAILED: LLM couldn't resolve
 */
export type PortalAuthoringState = 'RESOLVED' | 'UNPARSED' | 'CURING' | 'FAILED';

export interface PortalDestination {
  path: string;
  title?: string;
  preview?: string;
  exists?: boolean;
}

export interface PortalCureResult {
  success: boolean;
  resolved_portal?: string;
  confidence: number;
  alternatives?: string[];
}

/**
 * Resource types for portal URIs.
 * See spec/protocols/portal-resource-system.md
 */
export type PortalResourceType =
  | 'file'
  | 'chat'
  | 'turn'
  | 'mark'
  | 'trace'
  | 'evidence'
  | 'constitutional'
  | 'crystal'
  | 'node';

export interface PortalURI {
  raw: string;
  resource_type: PortalResourceType;
  resource_path: string;
  fragment: string | null;
}

export interface ResolvedResource {
  uri: string;
  resource_type: PortalResourceType;
  exists: boolean;
  title: string;
  preview: string;
  content: unknown;
  actions: string[];
  metadata: Record<string, unknown>;
}

export interface PortalData {
  /** Edge type — null if unparsed */
  edge_type: string | null;
  source_path?: string;
  destinations: PortalDestination[];
  /** Authoring state (defaults to RESOLVED for backward compat) */
  authoring_state?: PortalAuthoringState;
  /** Natural language query (if UNPARSED) */
  natural_language?: string;
  /** Whether auto-discovered vs explicitly authored */
  is_discovered?: boolean;
  /** Resource type information (NEW) */
  resource_type?: PortalResourceType;
  resolved_resource?: ResolvedResource;
  /** Evidence ID from witness mark (Phase 2) */
  evidence_id?: string;
}

/**
 * Portal syntax as parsed from markdown @[...] tokens.
 * See spec/protocols/portal-token.md §15.8
 */
export interface PortalSyntax {
  raw_text: string;
  state: PortalAuthoringState;
  edge_type: string | null;
  destinations: string[] | null;
  natural_language: string | null;
  span: [number, number];
  line: number;
}

// =============================================================================
// NEW: Principle Token Data
// =============================================================================

export type PrincipleCategory = 'architectural' | 'constitutional' | 'operational';

export interface PrincipleData {
  principle: string;
  title?: string;
  description?: string;
  category?: PrincipleCategory;
}

// =============================================================================
// NEW: Image Token Data
// =============================================================================

export interface ImageTokenData {
  src: string;
  alt: string;
  ai_description?: string;
  caption?: string;
}

export function getTokenData<T>(content: MeaningTokenContent): T {
  return content.token_data as T;
}
