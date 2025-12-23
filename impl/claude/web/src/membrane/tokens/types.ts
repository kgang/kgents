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

export function getTokenData<T>(content: MeaningTokenContent): T {
  return content.token_data as T;
}
