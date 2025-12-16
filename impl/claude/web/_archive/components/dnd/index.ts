/**
 * DnD Components: Drag-and-drop system for agent composition.
 *
 * This module provides the infrastructure for dragging agents and building
 * pipelines. It uses @dnd-kit for accessible, performant drag-and-drop.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

// Context provider
export { DndProvider, type DndProviderProps } from './DndProvider';

// Draggable items
export { DraggableAgent, type DraggableAgentProps, type DragHandleMode } from './DraggableAgent';

// Drop zones
export { PipelineSlot, type PipelineSlotProps } from './PipelineSlot';

// Drag preview
export { DragPreview, type DragPreviewProps } from './DragPreview';

// Types
export type {
  DragItemType,
  DragData,
  AgentDragData,
  PipelineNodeDragData,
  DropZoneConfig,
  DropResult,
  PipelineNodeData,
  Port,
  PipelineEdge,
  Pipeline,
} from './types';

// Type guards
export { isAgentDragData, isPipelineNodeDragData } from './types';
