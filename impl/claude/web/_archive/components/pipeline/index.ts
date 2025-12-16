/**
 * Pipeline Components: Visual pipeline builder.
 *
 * These components enable users to visually compose agents into
 * executable pipelines. The canvas supports drag-drop, connection
 * drawing, and undo/redo.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

// Canvas
export { PipelineCanvas, type PipelineCanvasProps, type CanvasMode } from './PipelineCanvas';

// Nodes and edges
export { PipelineNode, type PipelineNodeProps } from './PipelineNode';
export {
  PipelineEdge,
  DraftEdge,
  EdgeMarkers,
  type PipelineEdgeProps,
  type DraftEdgeProps,
  createStraightPath,
  createOrthogonalPath,
} from './PipelineEdge';

// Context menus
export {
  ContextMenu,
  NodeContextMenu,
  EdgeContextMenu,
  useContextMenu,
  type ContextMenuProps,
  type ContextMenuItem,
  type ContextMenuSection,
  type NodeContextMenuProps,
  type EdgeContextMenuProps,
  type UseContextMenuReturn,
} from './ContextMenu';

// State management
export {
  usePipeline,
  type PipelineState,
  type PipelineActions,
  type ValidationResult,
  type ValidationError,
} from './usePipeline';
