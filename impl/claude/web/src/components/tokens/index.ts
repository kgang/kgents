/**
 * Interactive Text Token Components
 *
 * Barrel export for token renderers.
 *
 * Seven token types (from SYNTHESIS-living-spec.md):
 * 1. AGENTESEPathToken — Clickable AGENTESE paths
 * 2. TaskCheckboxToken — Toggleable tasks
 * 3. PortalToken — Expandable hyperedges ("the doc comes to you")
 * 4. CodeBlockToken — Syntax-highlighted code
 * 5. ImageToken — Images with AI analysis
 * 6. PrincipleToken — Architectural principle references
 * 7. LinkToken — Hyperlinks with preview
 *
 * Plus supporting tokens:
 * - TextSpan — Plain text
 * - BlockquoteToken — Quoted text
 * - HorizontalRuleToken — Section dividers
 * - MarkdownTableToken — Tables
 */

// =============================================================================
// Core Token Components
// =============================================================================

export { AGENTESEPathToken } from './AGENTESEPathToken';
export { TaskCheckboxToken } from './TaskCheckboxToken';
export { PortalToken, type PortalDestination } from './PortalToken';
export { CodeBlockToken } from './CodeBlockToken';
export { ImageToken } from './ImageToken';
export { PrincipleToken, type PrincipleCategory } from './PrincipleToken';
export { LinkToken } from './LinkToken';

// =============================================================================
// Supporting Token Components
// =============================================================================

export { TextSpan } from './TextSpan';
export { BlockquoteToken } from './BlockquoteToken';
export { HorizontalRuleToken } from './HorizontalRuleToken';
export { MarkdownTableToken } from './MarkdownTableToken';

// =============================================================================
// Rich Highlighting (inspired by Rich's ReprHighlighter)
// =============================================================================

export {
  RichHighlighter,
  useRichHighlight,
  hasHighlightableContent,
  type HighlightType,
} from './RichHighlighter';

// =============================================================================
// Container Component
// =============================================================================

export { InteractiveDocument } from './InteractiveDocument';

// =============================================================================
// Types
// =============================================================================

export type {
  // Scene Graph types
  Affordance,
  Interaction,
  LayoutDirective,
  MeaningTokenContent,
  MeaningTokenKind,
  NodeStyle,
  SceneEdge,
  SceneGraph,
  SceneNode,
  SceneNodeKind,
  // Token data types
  AGENTESEPathData,
  BlockquoteData,
  CodeBlockData,
  HorizontalRuleData,
  ImageData,
  ImageTokenData,
  LinkData,
  MarkdownTableData,
  PortalData,
  PrincipleData,
  TaskCheckboxData,
} from './types';

// =============================================================================
// Type Guards
// =============================================================================

export { getTokenData, isMeaningTokenContent, isTextContent } from './types';
