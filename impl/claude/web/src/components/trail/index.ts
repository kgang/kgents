/**
 * Trail components - Visual Trail Graph feature.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * @see brainstorming/visual-trail-graph-r&d.md
 * @see spec/protocols/trail-protocol.md Section 8
 */

// Visualization
export { TrailGraph } from './TrailGraph';
export { ContextNode, nodeTypes, getEdgeColor } from './ContextNode';

// Panels
export { ReasoningPanel } from './ReasoningPanel';
export { ExplorerPresence } from './ExplorerPresence';
export { BudgetRing } from './BudgetRing';

// Trail Builder (Creation UI)
export { TrailBuilderPanel } from './TrailBuilderPanel';
export { PathPicker } from './PathPicker';

// Types
export type { ContextNodeData } from './ContextNode';
