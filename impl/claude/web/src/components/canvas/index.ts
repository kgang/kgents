/**
 * Canvas Components for CLI v7 Phase 5: Collaborative Canvas.
 *
 * These components render the AGENTESE mind-map with agent presence
 * and spring-physics cursor animation.
 *
 * @see plans/cli-v7-implementation.md Phase 5
 */

export {
  AgentCanvas,
  generateRadialLayout,
  type CanvasNode,
  type AgentCanvasProps,
} from './AgentCanvas';

export {
  CursorOverlay,
  PresenceStatusBadge,
  CursorList,
  type CursorOverlayProps,
  type PresenceStatusBadgeProps,
  type CursorListProps,
} from './CursorOverlay';

export { AnimatedCursor, type AnimatedCursorProps } from './AnimatedCursor';

export { NodeDetailPanel, type NodeDetailPanelProps } from './NodeDetailPanel';
