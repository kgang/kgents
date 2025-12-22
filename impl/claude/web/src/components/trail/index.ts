/**
 * Trail components - Visual Trail Graph feature.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Living Earth Aesthetic (Crown Jewels Genesis):
 * - Warm earth tones (Soil, Bark, Wood, Clay, Sand)
 * - Living greens (Moss, Fern, Sage, Mint, Sprout)
 * - Ghibli glow accents (Lantern, Honey, Amber, Copper, Bronze)
 * - Breathing animations on all nodes
 * - Growing/unfurling transitions on panels
 *
 * @see brainstorming/visual-trail-graph-r&d.md
 * @see spec/protocols/trail-protocol.md Section 8
 * @see creative/crown-jewels-genesis-moodboard.md
 */

// Visualization
export { TrailGraph } from './TrailGraph';
export { ContextNode, nodeTypes, getEdgeColor } from './ContextNode';

// Panels
export { ReasoningPanel } from './ReasoningPanel';
export { ExplorerPresence } from './ExplorerPresence';
export { BudgetRing } from './BudgetRing';
export { SuggestionPanel } from './SuggestionPanel';

// Trail Builder (Creation UI)
export { TrailBuilderPanel } from './TrailBuilderPanel';
export { PathPicker } from './PathPicker';

// Design System
export {
  LIVING_EARTH,
  EDGE_COLORS,
  BACKGROUNDS,
  BREATHING,
  GROWING,
  UNFURLING,
  FLOWING,
  STATUS_GLYPHS,
  getEdgeColor as getLivingEdgeColor,
  glowShadow,
  nodeGlow,
  breathingVariant,
  growingVariant,
  unfurlingVariant,
} from './living-earth';

// Types
export type { ContextNodeData, ZoomLevel } from './ContextNode';
export type { SuggestionPanelProps } from './SuggestionPanel';
